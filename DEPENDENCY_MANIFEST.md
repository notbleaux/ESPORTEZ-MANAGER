# RadiantX Game - Dependency Manifest

> **Project:** RadiantX - Tactical FPS Coach Sim  
> **Analysis Date:** 2026-03-30  
> **Source Paths:**
> - `/root/.openclaw/workspace/eSports-EXE/platform/simulation-game/`
> - `/root/.openclaw/workspace/eSports-EXE/packages/shared/apps/radiantx-game/`

---

## 1. Godot Engine Version

| Property | Value |
|----------|-------|
| **Godot Version** | 4.0 |
| **Config Version** | 5 |
| **Rendering Method** | Forward Plus |
| **Physics Ticks** | 60 TPS |
| **Project Name** | RadiantX - Tactical FPS Coach Sim |

### Display Configuration
- Viewport: 1280x720
- Resizable: true

---

## 2. Addons Used

### GUT (Godot Unit Testing)
| Property | Value |
|----------|-------|
| **Name** | GUT |
| **Description** | Unit Testing for Godot |
| **Author** | Tommy Bartlett |
| **Version** | 9.2.1 |
| **Language** | GDScript |
| **Path** | `res://addons/gut/` |

---

## 3. NuGet Packages

### C# Projects Overview

| Project | Target Framework | Type | Dependencies |
|---------|------------------|------|--------------|
| `SimCore.csproj` | .NET 8.0 | Library | None (base) |
| `ConsoleRunner.csproj` | .NET 8.0 | Executable | SimCore |
| `SimConsoleRunner.csproj` | .NET 8.0 | Executable | SimCore |

### Project References
```
ConsoleRunner → SimCore
SimConsoleRunner → SimCore
```

### NuGet Dependencies
**None detected** - Projects use only local project references.

---

## 4. External API Endpoints

### Primary API
| Endpoint | Purpose | Location |
|----------|---------|----------|
| `https://sator-api.onrender.com` | SATOR API base URL | `IntegratedRoundRunner.cs`, `RotasIntegration.gd` |
| `https://sator-api.onrender.com/api/rotas` | ROTAS analysis endpoint | `RotasIntegration.gd` |

### API Usage Details

#### In C# (SimCore)
```csharp
// From IntegratedRoundRunner.cs
var apiKey = Environment.GetEnvironmentVariable("SATOR_API_KEY");
_apiClient = new SatorApiClient(
    "https://sator-api.onrender.com", 
    apiKey
);
```

#### In GDScript
```gdscript
# From RotasIntegration.gd
var online_endpoint: String = 'https://sator-api.onrender.com/api/rotas'

# From LiveSeasonModule.gd (ExportClient)
@export var api_endpoint: String = ""  # Configurable at runtime
@export var api_key: String = ""       # Configurable at runtime
```

### Other URLs
| URL | Purpose | Location |
|-----|---------|----------|
| `https://sator.io/schemas/mod-v2.json` | Mod schema reference | `Defs/Mods/example-mod-v2.json` |
| `https://example.com/mods/vandal-x.zip` | Example mod download URL | `Defs/Mods/example-mod-v2.json` |

---

## 5. Environment Variables

| Variable | Required | Usage | Default |
|----------|----------|-------|---------|
| `SATOR_API_KEY` | Optional | API authentication for SATOR services | `null` |

### Variable Usage
```csharp
// From IntegratedRoundRunner.cs
var apiKey = Environment.GetEnvironmentVariable("SATOR_API_KEY");
if (!string.IsNullOrEmpty(apiKey))
{
    _apiClient = new SatorApiClient("https://sator-api.onrender.com", apiKey);
}
```

---

## 6. File Path Dependencies

### Godot Project Structure (res:// paths)

| Path | Purpose | Referenced In |
|------|---------|---------------|
| `res://scenes/Main.tscn` | Main scene | `project.godot` |
| `res://icon.svg` | Application icon | `project.godot` |
| `res://scripts/RotasIntegration.gd` | Autoload singleton | `project.godot` |
| `res://maps/training_ground.json` | Default map | `Main.gd` |
| `res://Defs` | Game definitions directory | `DataLoader.gd` |

### Configuration Files

| File | Purpose |
|------|---------|
| `res://Defs/features.json` | Feature flags configuration |
| `res://Defs/agents/` | Agent definitions |
| `res://Defs/rulesets/rulesets.json` | Game rulesets |
| `res://Defs/weapons/` | Weapon definitions |
| `res://Defs/utilities/` | Utility definitions |
| `res://Defs/Mods/` | Mod definitions |

### External Data Paths

| Pattern | Usage |
|---------|-------|
| `ConsoleRunner/` | C# console test runner |
| `SimConsoleRunner/` | C# simulation runner |
| `SimCore/` | Core C# simulation library |

---

## 7. Key Code Files Mapping

### GDScript (Godot)

| File | Purpose |
|------|---------|
| `scripts/RotasIntegration.gd` | ROTAS API integration, online/offline analysis |
| `src/LiveSeasonModule.gd` | Match export, data sanitization, SATOR API client |
| `src/ExportClient.gd` | HTTP client with retry logic and offline queue |
| `scripts/Main.gd` | Main game logic |
| `scripts/Data/DataLoader.gd` | Data loading utilities |

### C# (SimCore)

| File | Purpose |
|------|---------|
| `SimCore/Sim/IntegratedRoundRunner.cs` | Round simulation with feature flags and caching |
| `SimCore/Cache/` | Simulation caching system |
| `SimCore/Features/` | Feature flag management |
| `SimCore/Api/` | SATOR API client |

---

## 8. Feature Flags (Configuration)

From `res://Defs/features.json`:

| Feature | Enabled | Rollout | Description |
|---------|---------|---------|-------------|
| `new_rating_algorithm` | true | 25% | Updated SimRating with economy weighting |
| `advanced_ai_agents` | false | 0% | Belief-based AI with utility reasoning |
| `deterministic_replays` | true | 100% | Seed-based replay reconstruction |
| `real_time_api_sync` | true | 50% | Sync simulation with live API data |
| `enhanced_economy` | true | 75% | Improved economic simulation model |
| `spatial_heatmaps` | false | 10% | Visual heatmap generation |

---

## 9. Data Partition Firewall

The project implements a strict data partition between Game-only fields and Web-exportable fields:

### GAME_ONLY_FIELDS (Never Exported)
- `internalAgentState`
- `radarData`
- `detailedReplayFrameData`
- `simulationTick`
- `seedValue`
- `visionConeData`
- `smokeTickData`
- `recoilPattern`

### Safe Export Fields
- Player stats: kills, deaths, assists, damage, headshots, etc.
- Match metadata: matchId, mapName, scores, duration
- Round summaries (without frame data)

---

## 10. Migration Checklist

### Critical Items
- [ ] Verify `SATOR_API_KEY` environment variable in production
- [ ] Update API endpoint if migrating from `onrender.com`
- [ ] Ensure `res://Defs/features.json` exists in build
- [ ] Configure GUT addon for testing (dev only)

### Path Dependencies to Verify
- [ ] `res://maps/` directory exists with JSON map files
- [ ] `res://Defs/` directory with all definition subdirectories
- [ ] C# projects compile with .NET 8.0 SDK

### External Dependencies
- [ ] SATOR API availability at `https://sator-api.onrender.com`
- [ ] Network connectivity for online mode features
- [ ] Fallback offline mode functional without API

---

*Generated by Dependency-Map Agent for ESPORTEZ-MANAGER migration planning.*
