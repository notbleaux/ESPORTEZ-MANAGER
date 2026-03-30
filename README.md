# ESPORTEZ-MANAGER

A comprehensive eSports team and tournament management system built with Godot Engine.

## Project Structure

```
ESPORTEZ-MANAGER/
├── project.godot          # Godot project file
├── scenes/                # Godot scene files (.tscn)
├── scripts/               # GDScript files
├── entities/              # Game entities and data models
├── maps/                  # Map/level data
├── Defs/                  # Definition files and constants
├── addons/                # Godot addons and plugins
├── tests/                 # Test files for Godot components
├── sim-core/              # C# Simulation Core
│   ├── SimCore/           # Core simulation engine
│   ├── ConsoleRunner/     # Console-based test runner
│   └── SimConsoleRunner/  # Simulation console interface
├── radiantx-game/         # Godot client application
│   ├── src/               # Source code
│   └── tests/             # Client tests
└── docs/                  # Documentation
```

## Components

### sim-core/
The C# based simulation engine that handles:
- Tournament logic and bracket management
- Team and player statistics
- Match simulation
- Data persistence

### radiantx-game/
The Godot client application providing:
- User interface for team management
- Tournament visualization
- Live match tracking
- Administrative tools

## Getting Started

1. Open `project.godot` in Godot Engine 4.x
2. Ensure .NET build tools are installed for C# support
3. Build the solution to compile sim-core

## License

[License TBD]
