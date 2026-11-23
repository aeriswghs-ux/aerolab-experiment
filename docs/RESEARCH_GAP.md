# Research gap and limits — literature and software landscape (November 2026)

Existing tools:
- AeroSandbox: airfoil XFOIL workflows, simulation and optimization
  https://github.com/peterdsharpe/AeroSandbox
- AeroPy: Python interface to XFOIL
  https://aeropy.readthedocs.io/en/latest/
- OpenAeroStruct: VLM and structural beam aeroelastic optimization
  https://mdolab-openaerostruct.readthedocs-hosted.com/en/latest/
- MetPy: units and physical atmospheric quantities
  https://unidata.github.io/MetPy/latest/api/generated/metpy.calc.density.html
- PyAero: airfoil geometry preparation / structured meshing
  https://pyaero.readthedocs.io/en/v3.0/index.html
- Other narrow wind-tunnel analysis repos exist and sometimes include related functionality.
- A tool called "AeroLab" was described in a 2026 SoftwareX publication; name overlap noted:
  https://www.sciencedirect.com/science/article/pii/S2352711026005704

Unmet need *hypothesis* (requires user interviews): an easily reproducible, accessible
measurement-first workflow where each transformation is explicit, uncertainty and
caveats are mandatory, and there is no confusion between numerical prediction and
physical measurement. Not a first-in-the-world novelty claim.

v0.1 scope: rectangular finite-span airfoils with pre-calibrated force channels aligned
in wind axes, pitot-static differential pressure, and ambient temperature/pressure.

Do not claim validation without data from calibrated hardware, repeated runs,
uncertainty budget, and matched external references.
