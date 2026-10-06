using System;
using System.IO;
using System.Text.Json;

namespace SharpManager.Properties;

// This BASIC edition must never read or write the official application's
// user.config. It has a separate identity and a separate preferences folder.
internal sealed class Settings
{
    private static readonly string preferencesFile = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "SharpManagerBasicPc1403", "V5", "settings.json");
    public static Settings Default { get; } = Load();
    public Settings() { }
    public string? SerialPort { get; set; }
    public bool ShowDebugMessages { get; set; }
    public string? DiskDirectory { get; set; }

    private static Settings Load()
    {
        try
        {
            return JsonSerializer.Deserialize<Settings>(File.ReadAllText(preferencesFile)) ?? new Settings();
        }
        catch (IOException) { return new Settings(); }
        catch (UnauthorizedAccessException) { return new Settings(); }
        catch (JsonException) { return new Settings(); }
    }

    public void Save()
    {
        Directory.CreateDirectory(Path.GetDirectoryName(preferencesFile)!);
        File.WriteAllText(preferencesFile, JsonSerializer.Serialize(this));
    }
}
