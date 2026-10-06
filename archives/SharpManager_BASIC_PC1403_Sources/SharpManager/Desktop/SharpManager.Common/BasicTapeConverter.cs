using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Text;
using System.Text.RegularExpressions;

namespace SharpManager;

/// <summary>
/// Converts numbered BASIC source to a PC-1403 cassette image using Pocket Tools.
/// Temporary files belong to one operation and never appear beside the user's source.
/// </summary>
public static class BasicTapeConverter
{
    public static async Task<byte[]> ConvertAsync(string sourcePath, string toolsDirectory,
        Action<string>? log = null, CancellationToken cancellationToken = default)
    {
        // Check the complete bundle before doing any work or starting a serial transfer.
        string tokenizer = Path.Combine(toolsDirectory, "bas2img.exe");
        string encoder = Path.Combine(toolsDirectory, "bin2wav.exe");
        foreach (string tool in new[] { tokenizer, encoder })
            if (!File.Exists(tool)) throw new FileNotFoundException(
                "Pocket Tools introuvable. Décompressez toute l'archive, y compris le dossier PocketTools.", tool);

        string source = await File.ReadAllTextAsync(sourcePath, cancellationToken);
        ValidateSource(source);
        string workDirectory = Path.Combine(Path.GetTempPath(), "SharpManager-Basic", Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(workDirectory);
        try
        {
            // Use short ASCII paths within the temporary directory: older Pocket Tools
            // builds do not handle Windows Unicode paths consistently. The parent temp
            // path is addressed only as the process working directory.
            await File.WriteAllTextAsync(Path.Combine(workDirectory, "source.bas"),
                source, new UTF8Encoding(false), cancellationToken);
            await RunToolAsync(tokenizer, workDirectory,
                new[] { "--pc=1403", "source.bas", "program.img" }, log, cancellationToken);
            await RunToolAsync(encoder, workDirectory,
                new[] { "--pc=1403", "--tap", "--name=" + GetTapeName(sourcePath), "program.img", "program.tap" },
                log, cancellationToken);
            byte[] tape = await File.ReadAllBytesAsync(Path.Combine(workDirectory, "program.tap"), cancellationToken);
            // The unchanged Arduino protocol carries the length as an unsigned 16-bit word.
            if (tape.Length < 10 || tape.Length > ushort.MaxValue)
                throw new InvalidDataException("La taille du fichier cassette produit est invalide.");
            return tape;
        }
        finally
        {
            // A cleanup failure must not hide the actual converter/transfer error.
            try { Directory.Delete(workDirectory, true); }
            catch (IOException) { }
            catch (UnauthorizedAccessException) { }
        }
    }

    /// <summary>Decode a received PC-1403 BASIC cassette without touching the user's destination.</summary>
    public static async Task<string> DecodeAsync(byte[] tape, string toolsDirectory,
        Action<string>? log = null, CancellationToken cancellationToken = default)
    {
        string decoder = Path.Combine(toolsDirectory, "wav2bin.exe");
        if (!File.Exists(decoder)) throw new FileNotFoundException(
            "Le décodeur wav2bin.exe est introuvable dans PocketTools.", decoder);
        // Data, binary and password-protected cassettes must keep their TAP format.
        if (tape.Length < 10 || (tape[0] != 0x70 && tape[0] != 0x72))
            throw new InvalidDataException("Cette cassette n'est pas un programme BASIC non protégé. Sauvegardez-la en .tap.");
        string workDirectory = Path.Combine(Path.GetTempPath(), "SharpManager-Basic", Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(workDirectory);
        try
        {
            await File.WriteAllBytesAsync(Path.Combine(workDirectory, "received.tap"), tape, cancellationToken);
            await RunToolAsync(decoder, workDirectory,
                new[] { "--pc=1403", "--tap", "--type=bas", "--utf8=yes", "--width=0", "received.tap", "received.bas" },
                log, cancellationToken);
            string source = await File.ReadAllTextAsync(Path.Combine(workDirectory, "received.bas"), cancellationToken);
            ValidateSource(source);
            return source;
        }
        finally
        {
            try { Directory.Delete(workDirectory, true); }
            catch (IOException) { }
            catch (UnauthorizedAccessException) { }
        }
    }

    public static void ValidateSource(string source)
    {
        int previous = -1;
        int count = 0;
        foreach (string rawLine in source.Split('\n'))
        {
            string line = rawLine.Trim();
            if (line.Length == 0) continue;
            // Reject unnumbered or out-of-order source rather than allowing a converter
            // to silently drop lines. Sharp BASIC accepts both '10 PRINT' and '10PRINT'.
            Match match = Regex.Match(line, @"^(\d+)(.*)$");
            if (!match.Success || !int.TryParse(match.Groups[1].Value, out int number)
                || number < 1 || number > 65279 || number <= previous
                || string.IsNullOrWhiteSpace(match.Groups[2].Value))
                throw new InvalidDataException(
                    "Le BASIC doit comporter des lignes numérotées de 1 à 65279, dans l'ordre croissant et sans doublon. Ligne : " + line);
            previous = number;
            count++;
        }
        if (count == 0) throw new InvalidDataException("Le fichier BASIC est vide.");
    }

    public static string GetTapeName(string sourcePath)
    {
        string name = Regex.Replace(Path.GetFileNameWithoutExtension(sourcePath).ToUpperInvariant(), "[^A-Z0-9]", "");
        if (name.Length == 0) return "PROGRAM";
        return name[..Math.Min(name.Length, 7)];
    }

    private static async Task RunToolAsync(string executable, string workDirectory,
        IEnumerable<string> arguments, Action<string>? log, CancellationToken cancellationToken)
    {
        var startInfo = new ProcessStartInfo(executable)
        {
            WorkingDirectory = workDirectory,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true
        };
        // ArgumentList avoids shell interpretation and correctly quotes filenames.
        foreach (string argument in arguments) startInfo.ArgumentList.Add(argument);
        using var process = Process.Start(startInfo) ?? throw new IOException("Impossible de lancer Pocket Tools.");
        Task<string> output = process.StandardOutput.ReadToEndAsync();
        Task<string> error = process.StandardError.ReadToEndAsync();
        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeout.CancelAfter(TimeSpan.FromSeconds(30));
        try { await process.WaitForExitAsync(timeout.Token); }
        catch (OperationCanceledException)
        {
            if (!process.HasExited) process.Kill(entireProcessTree: true);
            await process.WaitForExitAsync();
            if (cancellationToken.IsCancellationRequested) throw;
            throw new TimeoutException("La conversion BASIC a dépassé 30 secondes.");
        }
        string diagnostics = (await output + "\n" + await error).Trim();
        if (diagnostics.Length > 0) log?.Invoke(diagnostics);
        if (process.ExitCode != 0)
            throw new InvalidDataException($"Conversion BASIC échouée ({Path.GetFileName(executable)}, code {process.ExitCode}).\n{diagnostics}");
    }
}
