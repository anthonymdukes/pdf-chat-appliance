# agent-shared/ Directory Overview

This directory is the cross-agent workspace for logs, training artifacts, technical deep dives, overflow documentation, and review outputs. It is designed for collaboration, knowledge sharing, and persistent memory across all agents and environments.

## Key Contents

- `training-day-summary.md` — Comprehensive summary of each autonomous training day, including progress, outcomes, and lessons learned.
- `advanced-technical-deep-dives.md` — In-depth technical modules and implementation patterns from advanced agent training.
- `overflow-training.md` — Additional insights, simulation scenarios, and future training proposals generated during training.
- `docs-review.md` — Documentation strategy evaluations, standards reviews, and improvement proposals.
- `logs/` — Runtime logs and performance metrics from agent workflows.
- `test-results/` — Integration and performance test outputs.
- `cross-agent/` — Artifacts and outputs from cross-agent collaboration and simulation.
- `temp/`, `api-data/`, `ingestion-data/`, `debug-files/`, `model-outputs/` — Staging areas for shared data, debug artifacts, and model results.

## Planned & Automation Files
- `visual-docs-map.md` (planned) — Visual map of documentation structure and agent knowledge flow.
- `automation-scripts/` (planned) — Scripts for markdownlint, spell check, and TOC generation automation.

## Usage
- All agents should read and write to this folder for cross-environment file exchange.
- Place model outputs, logs, test data, and other artifacts here for team access.
- See `SHARED_DIRECTORY_USAGE.md` in `/docs/` for detailed usage policies and best practices. 