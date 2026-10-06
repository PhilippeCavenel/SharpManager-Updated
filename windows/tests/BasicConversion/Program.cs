using SharpManager;

// Portable integration harness. Supply native Pocket Tools compiled for this OS
// (named bas2img.exe/bin2wav.exe, as expected by the application).
string tools = Path.GetFullPath(args[0]);
void Check(bool condition, string message) { if (!condition) throw new Exception(message); }
void Reject(string text)
{
    try { BasicTapeConverter.ValidateSource(text); }
    catch (InvalidDataException) { return; }
    throw new Exception("Invalid source was accepted: " + text);
}
BasicTapeConverter.ValidateSource("10PRINT \"TEST\"\r\n20 END\n");
foreach (string source in new[] { "", "PRINT 1", "10 END\n10 END", "20 END\n10 END", "0 END", "65280 END", "10" }) Reject(source);
Check(BasicTapeConverter.GetTapeName("é chrono long.bas") == "CHRONOL", "Tape name sanitization");
Check(BasicTapeConverter.GetTapeName("é.bas") == "PROGRAM", "Empty tape name fallback");
string dir = Path.Combine(Path.GetTempPath(), "Sharp BASIC test é " + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(dir);
try
{
    string sourcePath = Path.Combine(dir, "mon programme é.bas");
    await File.WriteAllTextAsync(sourcePath, "10 PRINT \"BONJOUR\"\n20 END\n");
    var logs = new List<string>();
    byte[] tape = await BasicTapeConverter.ConvertAsync(sourcePath, tools, logs.Add);
    Check(tape.Length > 20 && tape[0] == 0x70, "PC-1403 TAP header");
    Check(Directory.GetFiles(dir).Length == 1, "Intermediates leaked into user directory");
    Check(logs.Count == 2, "Converter diagnostics missing");
    await File.WriteAllBytesAsync(Path.Combine(dir, "result.tap"), tape);
    // Caller can inspect/round-trip the generated tape; tests do not need real hardware.
    if (args.Length > 1) await File.WriteAllBytesAsync(args[1], tape);
    try { await BasicTapeConverter.ConvertAsync(sourcePath, Path.Combine(dir, "missing")); throw new Exception("Missing tools accepted"); }
    catch (FileNotFoundException) { }
    using var cancelled = new CancellationTokenSource();
    cancelled.Cancel();
    try { await BasicTapeConverter.ConvertAsync(sourcePath, tools, cancellationToken: cancelled.Token); throw new Exception("Cancellation ignored"); }
    catch (OperationCanceledException) { }
    byte[] originalTape = tape.ToArray();
    string decoded = await BasicTapeConverter.DecodeAsync(tape, tools);
    Check(decoded.Contains("BONJOUR"), "BASIC decoding lost the string literal");
    Check(tape.SequenceEqual(originalTape), "Decoder modified the received cassette");
    string decodedPath = Path.Combine(dir, "reçu é.bas");
    await File.WriteAllTextAsync(decodedPath, decoded);
    byte[] reencoded = await BasicTapeConverter.ConvertAsync(decodedPath, tools);
    Check(reencoded.Skip(10).SequenceEqual(tape.Skip(10)), "BASIC round-trip changed cassette program data");
    try { await BasicTapeConverter.DecodeAsync(new byte[10], tools); throw new Exception("Non-BASIC accepted"); }
    catch (InvalidDataException) { }
    using var stopDecode = new CancellationTokenSource();
    stopDecode.Cancel();
    try { await BasicTapeConverter.DecodeAsync(tape, tools, cancellationToken: stopDecode.Token); throw new Exception("Decode cancellation ignored"); }
    catch (OperationCanceledException) { }
    byte[] corrupted = tape.ToArray();
    corrupted[^1] ^= 1;
    try { await BasicTapeConverter.DecodeAsync(corrupted, tools); throw new Exception("Checksum error accepted"); }
    catch (InvalidDataException) { }
    if (args.Length > 2)
    {
        byte[] chrono = await BasicTapeConverter.ConvertAsync(Path.GetFullPath(args[2]), tools);
        string chronoSource = await BasicTapeConverter.DecodeAsync(chrono, tools);
        Check(chronoSource.Contains("RIGHT$") && chronoSource.Contains("GOTO"), "CHRONO decoder");
        await File.WriteAllTextAsync(decodedPath, chronoSource);
        byte[] chronoAgain = await BasicTapeConverter.ConvertAsync(decodedPath, tools);
        Check(chronoAgain.Skip(10).SequenceEqual(chrono.Skip(10)), "CHRONO round-trip changed program data");
    }
    Console.WriteLine("PASS: BASIC decode/export, unchanged source cassette, round-trip, non-BASIC rejection, cancellation and checksum validation.");
    Console.WriteLine("PASS: validation, tape name, native conversion, Unicode/spaced source path, missing tools, cancellation.");
}
finally { Directory.Delete(dir, true); }
