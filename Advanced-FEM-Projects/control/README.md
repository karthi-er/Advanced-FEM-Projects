# Control Log Analysis

Analyze a recorded setpoint/output CSV and calculate sample count, tracking
RMSE, maximum absolute error, and final error. This project describes supplied
measurements; it does **not** implement or tune a control algorithm, and the
included sample is illustrative rather than a reported engineering result.

## Install and run

From the portfolio folder:

```powershell
python -m pip install -e .\control
python -m control_log .\control\sample_log.csv
python -m unittest discover -s control\tests
```

Input CSV must have `time,setpoint,output` columns, at least one data row,
finite numeric values, and strictly increasing time values. Invalid input
returns a concise error and a nonzero exit status.

## Status and publishing

This is a newly created baseline because the referenced project archive was
not supplied. Historical control results could not be verified and are not
reproduced here. Add the original dataset and independently verified results
before making result-based claims.
