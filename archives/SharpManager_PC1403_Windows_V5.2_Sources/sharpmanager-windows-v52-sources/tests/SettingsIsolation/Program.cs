using SharpManager.Properties;
using System.Diagnostics;
using System.Reflection;
using System.Text.Json;

// Run each stage in a fresh process: Default is loaded once at application startup.
if (args.Length > 0)
{
    var settings = Settings.Default;
    if (args[0] == "write")
    {
        if (settings.SerialPort != null || settings.ShowDebugMessages || settings.DiskDirectory != null)
            throw new Exception("Unexpected existing preferences");
        settings.SerialPort = "COM5";
        settings.ShowDebugMessages = true;
        settings.DiskDirectory = "disk é";
        settings.Save();
    }
    else if (args[0] == "read")
    {
        if (settings.SerialPort != "COM5" || !settings.ShowDebugMessages || settings.DiskDirectory != "disk é")
            throw new Exception("Preferences round-trip failed");
    }
    else if (args[0] == "invalid" && (settings.SerialPort != null || settings.ShowDebugMessages))
        throw new Exception("Corrupt preferences not handled");
    return;
}
var taskDirectory = Path.Combine(Path.GetTempPath(), "SharpManager-preferences-test-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(taskDirectory);
try
{
    // Linux harness redirects LocalApplicationData with XDG_DATA_HOME. The product
    // uses Windows' LocalApplicationData and its own SharpManagerBasicPc1403 folder.
    string original = Path.Combine(taskDirectory, "Codaris Computing", "SharpManager", "user.config");
    Directory.CreateDirectory(Path.GetDirectoryName(original)!);
    const string untouched = "Original preferences sentinel: COM5";
    File.WriteAllText(original, untouched);
    void Stage(string stage)
    {
        var start = new ProcessStartInfo(Environment.ProcessPath!) { UseShellExecute = false };
        if (Path.GetFileNameWithoutExtension(Environment.ProcessPath) == "dotnet")
            start.ArgumentList.Add(Assembly.GetExecutingAssembly().Location);
        start.ArgumentList.Add(stage);
        start.Environment["XDG_DATA_HOME"] = taskDirectory;
        using var process = Process.Start(start)!;
        process.WaitForExit();
        if (process.ExitCode != 0) throw new Exception("Stage failed: " + stage);
    }
    Stage("write");
    Stage("read");
    string isolated = Path.Combine(taskDirectory, "SharpManagerBasicPc1403", "V5", "settings.json");
    if (!File.Exists(isolated) || File.ReadAllText(original) != untouched) throw new Exception("Isolation failed");
    var files = Directory.GetFiles(taskDirectory, "*", SearchOption.AllDirectories);
    if (files.Length != 2) throw new Exception("Unexpected preference file written");
    File.WriteAllText(isolated, "{bad json");
    Stage("invalid");
    Console.WriteLine("PASS: isolated path, saved/loaded preferences, original config unchanged, corrupt JSON defaults.");
}
finally { Directory.Delete(taskDirectory, true); }
