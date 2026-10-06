namespace SharpManager;

/// <summary>
/// Gives exactly one packet reader ownership of the transport. Merely pausing
/// the background loop leaves a window between its suspension check and read.
/// This lock covers the complete foreground exchange or incoming packet.
/// </summary>
internal sealed class SerialProtocolGate
{
    private readonly SemaphoreSlim semaphore = new(1, 1);
    internal async Task<IDisposable> EnterAsync(CancellationToken cancellationToken = default)
    {
        await semaphore.WaitAsync(cancellationToken).ConfigureAwait(false);
        return new Lease(semaphore);
    }
    private sealed class Lease(SemaphoreSlim semaphore) : IDisposable
    {
        private SemaphoreSlim? owner = semaphore;
        public void Dispose() => Interlocked.Exchange(ref owner, null)?.Release();
    }
}
