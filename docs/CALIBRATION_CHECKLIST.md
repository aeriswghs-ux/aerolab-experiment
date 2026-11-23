# Before running AeroLab on actual experimental data

This is a documentation checklist, NOT a calibration certificate and NOT a
substitute for hardware supervision. Have a knowledgeable adult or laboratory
mentor review sensor installation and safe operating procedures.

1. Record model identifier, chord, span, area reference, and how dimensions
   were measured. Include uncertainties and airfoil orientation.
2. Record force-channel calibration method and units, separately for lift
   and drag. Do not feed raw ADC readings or grams into the `*_N` fields.
3. Identify which measured axes are wind axes. If the balance rotates with
   angle of attack, resolve normal and axial forces BEFORE using v0.1.
4. Record zero-flow, model-mounted tare force and pressure readings under
   the same conditions where possible. Support and model weight offsets
   might change with angle; v0.1 assumes CONSTANT offsets, so do not use
   it unchanged if tares vary substantially with angle.
5. Identify pressure measurement type. `dp_pa` must be true pitot
   total-minus-static pressure, not a wall static gauge reading.
6. Record temperature (C) and absolute ambient pressure (Pa).
   Relative humidity is NOT accounted for in v0.1.
7. Establish whether each CSV row is a truly independent steady-state
   observation. Keep replicate run IDs and conditions in a separate log.
8. Create a traceable uncertainty budget. Standard 1-sigma uncertainties
   are NOT synonymous with datasheet maximum errors or the number of digits
   displayed by a sensor.
9. Record sensor alignment, test-section velocity uniformity, fluctuations,
   tunnel blockage, support interference and vibration conditions; v0.1
   does not automatically correct them.
10. Have a mentor review the output before calling any data scientifically
    validated. Match Reynolds number, turbulence level and geometry when
    comparing against published polar datasets or XFOIL.

Hardware data formats and angle-varying tares are scheduled for later releases.
