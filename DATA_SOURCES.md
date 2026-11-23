# Data sources and provenance

Retrieved/screened 2026-11-23. Code license does not relicense external data.

## Bundled experimental reference

Charles L. Ladson (1988), *Effects of Independent Variation of Mach and Reynolds Numbers on the Low-Speed Aerodynamic Characteristics of the NACA 0012 Airfoil Section*, NASA TM-4074.
[NASA report record](https://ntrs.nasa.gov/citations/19880019495).
NASA's indexed record labels the report “Work of the US Gov.” Numerical facts are retained with attribution; no claim of NASA endorsement.

[Turbulence Modeling Resource](https://tmbwg.github.io/turbmodels/naca0012_val.html) supplies the [coefficient table](https://tmbwg.github.io/turbmodels/NACA0012_validation/CLCD_Ladson_expdata.dat). The bundled file is unchanged: 53 rows, three trip conditions (80/120/180 grit), NACA 0012, Re=6,000,000, Mach 0.15. The table contains no standard uncertainties or raw forces. Treat uncertainty as unknown. Transition differs between zones; do not pool them as repeat measurements. Near-stall results require particular caution.

Pinned repository revision: `20a39f549dbff988a6accc421ac84dafc4487695`.
SHA-256: `78cd2f6aa4968e80f44cbf6c96f699bd9c6e45681d958ec528a10cf72ed23357`.
`scripts/fetch_reference.py` retrieves the pinned bytes and checks the hash. The parser only separates zones and converts numeric text; it performs no digitization, smoothing, or interpolation.

## NACA 0018 sources screened, not bundled

- W. A. Timmer (2008), [Two-dimensional low-Reynolds number wind tunnel results for airfoil NACA 0018](https://repository.tudelft.nl/record/uuid:697c29b1-d1c4-4f78-9675-9a338933eec2), DOI [10.1260/030952408787548848](https://doi.org/10.1260/030952408787548848). Institutional record gives no open license and restricts redistribution. No curves digitized or copied.
- [Technion Flow Control Lab](https://www.flowcontrollab.com/data-resource): NACA 0018 pressure/coefficient/PIV data at Re=65,000–750,000, including surge, pitch and blowing. Individual case suitability and reuse permission remain unresolved. Not treated as a matched steady reference.
- D. Blake Stringer (2022), [Airfoil 360 v2022: Wind Tunnel Data](https://data.mendeley.com/datasets/dz4bv26ncd/1), DOI 10.17632/dz4bv26ncd.1, CC BY 4.0. NACA 0012/2412 and Selig s1210 at Re=50,000/100,000; not NACA 0018. Direct download attempts returned HTTP 403. No data imported.

## Formula references

- [NASA lift coefficient definition](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-coefficient/): CL=L/(qS), with Reynolds/Mach compatibility required for physical comparison.
- [NIST TN 1297 Appendix A](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-appendix-law-propagation-uncertainty): first-order propagation including covariance. AeroLab implements only independent-input budgets; covariance is a limitation, not assumed measured zero.

## Original software

User-supplied `AeroLab_Python_v0.1.0.zip`, SHA-256 `b88f7196049033d6983019a85863712a9e0c9ca70ff1cdf5f795a8ae54847f66`.
MIT license preserved. Original synthetic CSV and configuration retained unchanged. Original archive had 23 tests; all passed after package installation. No actual user tunnel measurements were supplied.
