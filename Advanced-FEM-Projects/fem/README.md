# 1D Axial-Bar FEM

A compact linear finite-element example for axial bars. It assembles the global
stiffness matrix, applies prescribed nodal displacements, solves for nodal
displacement, and reports element axial force. Use consistent units throughout.
This project does not include beam elements or claim to reproduce unavailable
historical results.

## Install and run

From the portfolio folder:

```powershell
python -m pip install -e .\fem
python -m axial_fem
python -m unittest discover -s fem\tests
```

The Python API accepts node positions, `Element(start, end, youngs_modulus,
area)` objects, nodal loads, and prescribed displacements. Non-finite values,
invalid node references, zero-length elements, and singular unconstrained
systems fail with explicit `ValueError` messages.

## Status

This runnable example was created because the referenced archive and its FEM
source/results were not supplied. Its printed output is a demonstration of
this example only, not a validation result for another model.
