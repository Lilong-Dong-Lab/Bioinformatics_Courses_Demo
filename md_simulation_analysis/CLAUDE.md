# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a template/seed project for bioinformatics molecular dynamics (MD) simulation analysis. It serves as a modern, reproducible foundation for computational workflows analyzing MD simulations in bioinformatics contexts.

## Environment Management

This project uses **Pixi** for reproducible Python environment management:

```bash
# Initialize environment and install dependencies
pixi install

# Enter the development shell
pixi shell

# Run defined tasks
pixi run <task-name>

# Update environment
pixi update
```

The project configuration is in `pixi.toml` which defines the workspace, channels (conda-forge), and platform (Linux-64).

## Architecture and Structure

**Current State**: This is a starter template with minimal files:
- `pixi.toml` - Project and dependency configuration
- `.gitignore` - Git ignore rules for pixi environments
- `.gitattributes` - Git configuration for pixi.lock file handling

**Expected Development Structure** (to be created as the project develops):
- `src/` or `scripts/` - Analysis scripts and MD processing workflows
- `data/` - Input structures, trajectories, and simulation parameters
- `results/` - Output files, plots, and analysis results
- `notebooks/` - Jupyter notebooks for interactive analysis
- `tests/` - Unit tests for analysis scripts

## Development Workflow

1. **Environment Setup**: Always work within `pixi shell` to ensure reproducible dependencies
2. **Dependencies**: Add MD analysis packages to `pixi.toml` as needed (MDAnalysis, NumPy, Pandas, etc.)
3. **Modular Design**: Create separate scripts/modules for different analysis tasks
4. **Configuration**: Keep analysis parameters in separate configuration files
5. **Testing**: Add pytest tests for analysis functionality

## Key Technologies

- **Python** - Primary language for MD analysis
- **Pixi** - Modern dependency management for reproducible environments
- **Expected MD Libraries** (to be added as needed):
  - MDAnalysis for trajectory processing
  - NumPy/Pandas for data manipulation
  - Matplotlib/Seaborn for visualization
  - Jupyter for interactive analysis

## Data Processing Pattern

The project follows a typical bioinformatics workflow:
1. Raw simulation data → 2. Feature extraction → 3. Statistical analysis → 4. Visualization/reports

## Git Configuration

The `.gitattributes` file ensures proper handling of the `pixi.lock` file by using binary merge strategy to prevent conflicts in dependency resolution.

This template provides a clean starting point for building reproducible molecular dynamics analysis workflows in bioinformatics.