# OpenSpecs

This repository uses a lightweight OpenSpecs format for documenting operational changes.

Every change record must include:

1. Summary
2. Problem / Trigger
3. Scope
4. Files changed
5. Decision / implementation
6. Verification
7. Risks / rollback

The goal is to keep the reasoning explicit, reproducible, and reviewable without depending on undocumented assumptions.

## Template

Use the following structure for new change entries:

- Title
- Date
- Context
- Problem
- Change made
- Files touched
- Validation
- Notes / next steps

## Current policy

- Active configuration files in directories such as myPackages, myAutomation, myScripts, myTemplate, myInput, and myGroup are considered operational.
- Files in _doc and _sandbox are backup or experimental material only and are not part of the active runtime.
