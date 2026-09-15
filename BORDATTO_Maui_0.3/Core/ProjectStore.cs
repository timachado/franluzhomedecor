using System.Text.Json;
using Microsoft.Maui.Storage;

namespace BordattoStudio.Core;

public sealed record ProjectSummary(string Name, int Stitches, float WidthMm, float HeightMm, string Mode, DateTime UpdatedAt);

public static class ProjectStore
{
    private const string Key = "bordatto_recent_projects_v033";

    public static IReadOnlyList<ProjectSummary> Load()
    {
        try
        {
            var json = Preferences.Default.Get(Key, "[]");
            return JsonSerializer.Deserialize<List<ProjectSummary>>(json) ?? [];
        }
        catch
        {
            return [];
        }
    }

    public static void Remember(EmbroideryDesign design, BordattoMode mode)
    {
        try
        {
            var items = Load().ToList();
            items.RemoveAll(x => string.Equals(x.Name, design.Name, StringComparison.OrdinalIgnoreCase));
            items.Insert(0, new ProjectSummary(
                design.Name,
                design.StitchCount,
                design.WidthMm,
                design.HeightMm,
                mode == BordattoMode.Tradicional ? "Tradicional" : "Studio Pro",
                DateTime.Now));
            if (items.Count > 12) items = items.Take(12).ToList();
            Preferences.Default.Set(Key, JsonSerializer.Serialize(items));
        }
        catch
        {
            // O projeto continua utilizável mesmo se o armazenamento local falhar.
        }
    }
}
