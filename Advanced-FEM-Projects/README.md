# Engineering Portfolio

Four small, independently runnable Python projects: control-log analysis, a 1D
axial-bar FEM demonstration, local retrieval with an optional Claude answer
step, and a CFD export-analysis pipeline.

> **Reconstruction note:** The referenced ZIP was not available. These folders
> are newly created, runnable baselines based only on the project areas in the
> brief; they are not reconstructions of missing source code or result files.
> No historical result values have been supplied or claimed. Replace the
> author and repository placeholders before publishing.

## Projects

| Folder | Purpose | Status |
|---|---|---|
| `control/` | Validate a time-series control log and report tracking metrics. It analyzes recorded data; it does not implement a controller. | Runnable |
| `fem/` | Solve a small 1D axial-bar finite-element example. Beam elements are not included. | Runnable |
| `rag/` | Chunk and retrieve local text, with an optional Anthropic answer-generation command. The real API path requires user-run verification. | Local retrieval runnable; API call unverified |
| `cfd/` | Inspect Fluent-style CSV records and flag missing/duplicate comparison data. The included sample is explicitly synthetic; real simulation findings are pending Fluent exports. | Pipeline runnable; simulation findings pending |

## Requirements

Python 3.10 or later. Each project can be installed and run separately. The
optional Claude command in `rag/` requires the `anthropic` package, an
`ANTHROPIC_API_KEY`, and network access.

## Quick start (Windows PowerShell)

Run these commands from this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .\control
python -m control_log .\control\sample_log.csv
```

For the other projects, replace `control` with `fem`, `rag`, or `cfd` in the
install command and use their project-specific commands in each README. Run
the test runner from this folder:

```powershell
python run_tests.py
```

Each project README documents its input format, limitations, and reproducible
commands. No content is published externally by this package.

To create a ZIP beside this folder on Windows, run
`.\package.ps1` from PowerShell. It refuses to overwrite an existing archive.

## Portfolio publishing placeholders

- **Author:** `[YOUR NAME]`
- **GitHub profile:** `[YOUR GITHUB PROFILE URL]`
- **Project repository URLs:** `[ADD EACH PROJECT URL AFTER PUBLISHING]`
- **CFD Fluent values/findings:** `[PENDING REAL FLUENT EXPORTS]`

See `linkedin/` for three result-claim drafts with verification placeholders
and a separate CFD hold template. Do not turn placeholders into claims or turn
the CFD template into a result post until real exports have been reviewed.
