# CFD Export Analysis

Validate CSV records exported from a CFD workflow and assess comparison
completeness against an explicitly declared material/velocity/quantity grid.
Missing, malformed, and duplicate records remain visible in the JSON report;
the tool never silently calls a partial comparison complete.

## Install and run

From the portfolio folder:

```powershell
python -m pip install -e .\cfd
cfd-analysis .\cfd\sample_export.csv --materials aluminium,steel --velocities low,high --quantities pressure_drop
python -m unittest discover -s cfd\tests
```

The sample CSV is **synthetic data for demonstrating the pipeline only**. It
is not an aluminium simulation result and its values must not be used as
engineering findings or a publishable comparison. Replace it with actual
Fluent exports and document the expected grid before assessing real findings.

## Status and publish hold

**Real Fluent results are pending.** Do not publish a CFD result or claim a
completed aluminium simulation until the exports, units, boundary conditions,
and expected comparison grid have been checked. The original archive and any
original chart were not available to reconstruct here.
