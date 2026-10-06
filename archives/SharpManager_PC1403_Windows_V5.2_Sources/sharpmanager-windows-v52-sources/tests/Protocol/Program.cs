using SharpManager;
using System.Threading.Channels;
using System.Collections.Concurrent;

void Check(bool condition, string name) { if (!condition) throw new Exception(name); Console.WriteLine("PASS: " + name); }
var messages = new Messages();
using var arduino = new Arduino(messages, null);
var firmware = new Firmware();
await arduino.ConnectTransportAsync("SIM", () => firmware);
Check(arduino.IsConnected, "real initialization protocol with Driver 1.3 simulator");

// An unsolicited print packet exercises the idle reader. It must not elicit NAK.
firmware.Inject(Ascii.SOH, (byte)Command.Print, (byte)'X');
await messages.PrintReceived.Task.WaitAsync(TimeSpan.FromSeconds(3));
await Task.Delay(30);
Check(firmware.StrayWrites == 0, "valid print packet is not followed by spurious NAK");

firmware.ExpectedSyncEcho = true;
firmware.Inject(Ascii.SYN);
await firmware.SyncEchoReceived.Task.WaitAsync(TimeSpan.FromSeconds(3));
await Task.Delay(30);
Check(firmware.StrayWrites == 0, "valid unsolicited SYN gets only its SYN response");

firmware.ExpectInvalidResponse = true;
firmware.Inject(Ascii.SOH, 0xFE);
await firmware.InvalidResponseReceived.Task.WaitAsync(TimeSpan.FromSeconds(3));
Check(firmware.StrayWrites == 0, "unsupported packet still receives NAK/Unexpected");

// Fragmented delayed replies plus repeated foreground operations stress ownership.
foreach (int size in new[] { 41, 64, 65, 128, 250 })
{
    byte[] tape = new byte[size];
    tape[0] = 0x70;
    for (int i = 1; i < tape.Length; i++) tape[i] = (byte)i;
    for (int repeat = 0; repeat < 8; repeat++)
    {
        await arduino.Ping();
        await arduino.SendTapeFile(new MemoryStream(tape));
        var sent = firmware.Transfers.Last();
        var expected = tape.ToArray();
        for (int i = 1; i <= 7; i++) expected[i] = expected[i].SwapNibbles();
        Check(sent.SequenceEqual(expected), $"TAP {size} bytes, pass {repeat + 1}: bytes preserved across blocks");
    }
}
Check(firmware.MaximumConcurrentReads == 1 && firmware.StrayWrites == 0,
    "foreground commands and background listener never overlap their reads");

firmware.FirstBlockDelayMs = 6000;
await arduino.SendTapeFile(new MemoryStream(new byte[65]));
firmware.FirstBlockDelayMs = 0;
Check(firmware.Transfers.Last().Length == 65 && firmware.MaximumConcurrentReads == 1,
    "extended 8-second load timeout tolerates first block ACK delayed by 6 seconds");

// Stream V5 keeps waveform output active after the last buffer ACK and sends
// ETX only after the final tape bit. Exercise more than 64 blocks.
arduino.Disconnect();
firmware = new Firmware { Continuous = true, FinalSignalDelayMs = 180 };
await arduino.ConnectTransportAsync("STREAM", () => firmware);
byte[] largeTape = new byte[5717];
largeTape[0] = 0x70;
firmware.BlockAckDelayMs = 20;
var clock = System.Diagnostics.Stopwatch.StartNew();
await arduino.SendTapeFile(new MemoryStream(largeTape));
clock.Stop();
Check(firmware.Transfers.Last().Length == largeTape.Length && firmware.AcknowledgedBlocks == 90,
    "continuous stream accepts 90 blocks of 64 bytes");
Check(clock.ElapsedMilliseconds >= 180 && firmware.SignalFinished,
    "Windows waits for ETX after the final block ACK");
await arduino.Ping();
Check(firmware.StrayWrites == 0, "stream ETX is consumed before the next command");

var expectedCapture = firmware.CaptureTape.ToArray();
for (int i = 1; i <= 7; i++) expectedCapture[i] = expectedCapture[i].SwapNibbles();
Check((await arduino.ReadTapeFile()).SequenceEqual(expectedCapture),
    "CSAVE frame and escaped control bytes are received without background interference");

// Leave the old listener waiting, disconnect and immediately reconnect the same
// Arduino object. All old reads must end; old task cleanup must not close SIM2.
var prior = firmware;
arduino.Disconnect();
firmware = new Firmware();
await arduino.ConnectTransportAsync("SIM2", () => firmware);
await arduino.Ping();
await Task.Delay(50);
Check(prior.ActiveReads == 0 && prior.Disposed && arduino.IsConnected,
    "reconnect waits for old reader and old cleanup cannot close the new session");
for (int i = 0; i < 20; i++)
{
    arduino.Disconnect();
    var next = new Firmware();
    await arduino.ConnectTransportAsync("SIM", () => next);
    await arduino.Ping();
    Check(firmware.ActiveReads == 0 && arduino.IsConnected, "rapid reconnect " + (i + 1));
    firmware = next;
}
// Disconnect while a transfer is waiting for its initial ACK. Reconnecting must
// wait for the old command to release protocol ownership before installing SIM3.
firmware.HoldLoadAck = true;
var interrupted = arduino.SendTapeFile(new MemoryStream(new byte[65]));
await firmware.LoadStarted.Task.WaitAsync(TimeSpan.FromSeconds(3));
var interruptedFirmware = firmware;
arduino.Disconnect();
firmware = new Firmware();
var reconnect = arduino.ConnectTransportAsync("SIM3", () => firmware);
try { await interrupted; throw new Exception("Interrupted transfer unexpectedly succeeded"); }
catch (TimeoutException) { }
catch (ArduinoException) { }
await reconnect.WaitAsync(TimeSpan.FromSeconds(3));
await arduino.Ping();
Check(interruptedFirmware.ActiveReads == 0 && arduino.IsConnected,
    "reconnect after interrupted transfer drains both old command and old listener");
arduino.Disconnect();
Check(firmware.StrayWrites == 0, "disconnect sends only expected cancellation");
Console.WriteLine("All protocol tests passed. No FTDI or Sharp hardware was used.");

sealed class Messages : IDebugTarget
{
    public TaskCompletionSource PrintReceived = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public void Write(string text) { if (text == "X") PrintReceived.TrySetResult(); }
    public void DebugWrite(string text) { }
    public void ShowException(Exception error) => throw new Exception("Unexpected background error", error);
}

// Models the public serial Driver 1.3 framing, 64-byte acknowledgments and init
// header. It does not model the electrical cassette signal or Sharp checksums.
sealed class Firmware : IByteStream, IDisposable
{
    private readonly Channel<byte> input = Channel.CreateUnbounded<byte>();
    private readonly object gate = new();
    private int state, command, length, readCount;
    private List<byte> payload = new();
    private int activeReads, maximumReads;
    public ConcurrentQueue<byte[]> Transfers = new();
    public byte[] CaptureTape = new byte[] { 0x70, 1, 2, 3, 0x10, 0x15, 0x16, 0x18, 0xFF, 0xFF, 0x41 };
    public int StrayWrites;
    public int FirstBlockDelayMs;
    public int BlockAckDelayMs;
    public int FinalSignalDelayMs;
    public int AcknowledgedBlocks;
    public bool Continuous;
    public bool SignalFinished;
    public bool Disposed;
    public bool ExpectedSyncEcho, HoldLoadAck, ExpectInvalidResponse;
    private bool invalidNakReceived;
    public TaskCompletionSource InvalidResponseReceived = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public TaskCompletionSource SyncEchoReceived = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public TaskCompletionSource LoadStarted = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public int ActiveReads => Volatile.Read(ref activeReads);
    public int MaximumConcurrentReads => Volatile.Read(ref maximumReads);
    public void Inject(params byte[] bytes) { foreach (byte b in bytes) input.Writer.TryWrite(b); }
    public async Task WaitForDataAvailable(CancellationToken ct = default)
    {
        if (!await input.Reader.WaitToReadAsync(ct)) throw new ObjectDisposedException("Firmware");
    }
    public async Task<byte> ReadByteAsync(CancellationToken ct = default)
    {
        int count = Interlocked.Increment(ref activeReads);
        maximumReads = Math.Max(maximumReads, count);
        try { return await input.Reader.ReadAsync(ct); }
        catch (ChannelClosedException) { throw new ObjectDisposedException("Firmware"); }
        finally { Interlocked.Decrement(ref activeReads); }
    }
    public void ClearReceiveBuffer() { while (input.Reader.TryRead(out _)) { } }
    private void Reply(params byte[] bytes) => ReplyAfter(2, bytes);
    private void ReplyAfter(int delayMs, params byte[] bytes)
    {
        // Different delays make the exchange overlap the idle task wake-up.
        _ = Task.Run(async () => { await Task.Delay(delayMs); Inject(bytes); });
    }
    public void WriteByte(byte b)
    {
        lock (gate)
        {
            if (Disposed) throw new ObjectDisposedException("Firmware");
            if (state == 0)
            {
                if (b == Ascii.CAN) return;
                if (ExpectInvalidResponse)
                {
                    if (!invalidNakReceived && b == Ascii.NAK) { invalidNakReceived = true; return; }
                    if (invalidNakReceived && b == (byte)ErrorCode.Unexpected)
                    { ExpectInvalidResponse = false; InvalidResponseReceived.TrySetResult(); return; }
                    throw new Exception("Invalid NAK response framing");
                }
                if (b == Ascii.SYN)
                {
                    if (ExpectedSyncEcho) { ExpectedSyncEcho = false; SyncEchoReceived.TrySetResult(); }
                    else Reply(Ascii.SYN);
                    return;
                }
                if (b == Ascii.SOH) { state = 1; return; }
                StrayWrites++; return;
            }
            if (state == 1)
            {
                command = b;
                if (b == (byte)Command.Init)
                {
                    state = 0;
                    Reply(Continuous
                        ? new byte[] { Ascii.SOH, 1, 3, 64, Ascii.STX }.Concat(
                            System.Text.Encoding.ASCII.GetBytes("synchro 2s - flux continu V5 - garde 64"))
                            .Append(Ascii.ETX).ToArray()
                        : new byte[] { Ascii.SOH, 1, 3, 64, Ascii.STX, (byte)'D', Ascii.ETX });
                    return;
                }
                if (b == (byte)Command.Ping) { state = 0; Reply(Ascii.ACK); return; }
                if (b == (byte)Command.LoadTape) { state = 2; return; }
                if (b == (byte)Command.SaveTape)
                {
                    state = 0;
                    var frame = new List<byte> { Ascii.ACK, Ascii.STX };
                    foreach (byte value in CaptureTape)
                    {
                        if (value is Ascii.DLE or Ascii.SYN or Ascii.CAN or Ascii.ETX or Ascii.NAK) frame.Add(Ascii.DLE);
                        frame.Add(value);
                    }
                    frame.Add(Ascii.ETX);
                    Reply(frame.ToArray()); return;
                }
                throw new Exception("Unexpected command " + b);
            }
            if (state == 2) { length = b; state = 3; return; }
            if (state == 3) { length |= b << 8; state = 4; return; }
            if (state == 4)
            {
                if (b != 10) throw new Exception("Unexpected header length");
                payload = new(); readCount = 0; state = 5;
                LoadStarted.TrySetResult();
                if (!HoldLoadAck) Reply(Ascii.ACK);
                return;
            }
            payload.Add(b); readCount++;
            if (readCount % 64 == 0 || readCount == length)
            {
                AcknowledgedBlocks++;
                ReplyAfter(readCount <= 64 && FirstBlockDelayMs > 0 ? FirstBlockDelayMs :
                    BlockAckDelayMs > 0 ? BlockAckDelayMs : 2, Ascii.ACK);
            }
            if (readCount == length)
            {
                Transfers.Enqueue(payload.ToArray()); state = 0;
                if (Continuous) _ = Task.Run(async () =>
                {
                    await Task.Delay(Math.Max(BlockAckDelayMs, 2) + FinalSignalDelayMs);
                    SignalFinished = true;
                    Inject(Ascii.ETX);
                });
            }
        }
    }
    public void Dispose() { Disposed = true; input.Writer.TryComplete(); }
}
