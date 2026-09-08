
# Thrust Joint Design Calculator — FINAL v1.0

## Purpose
Traceable preliminary engineering design of a bolted/EBW flange joint between a CuCrZr chamber and an IN718 nozzle.

## Workflow
01 Engine Inputs
02 Pressure & Thrust
03 Loads & FBD
04 Thermal
05 Flange Design
06 Seal Design
07 Bolt Design
08 EBW vs Bolted
09 Design Review
10 Report

## Engineering philosophy
The application distinguishes:
- local joint pressure from chamber pressure;
- external load on the isolated nozzle from flange reaction;
- nozzle-to-flange load from reaction-on-nozzle;
- free thermal mismatch from actual restrained thermal joint load;
- seal seating load from structural flange stress;
- bolt material strength from bolt/joint stiffness;
- preliminary screening from final qualification.

## Key conventions
- Joint plane is X=Y=Z=0.
- +X is downstream.
- Vertical ground test: +Y is downward with gravity.
- Nozzle is below the flange.
- Nozzle CG is entered in XYZ coordinates.
- Page 03 passes nozzle -> flange loads downstream.

## Important basis
NASA-STD-5020B is the primary conceptual basis for threaded fastening-system stiffness, preload, load sharing and separation checks.
Technetics metal-seal literature is used for the concept that total bolt load must account for seal seating and hydrostatic load, with application-specific safety considerations.
SAE AS568F is the current aerospace O-ring size standard, but elastomeric O-rings are not assumed suitable for the hot-gas joint merely because a size exists.
Special Metals IN718 data are used as a source for temperature-dependent modulus behavior.
ATI A286 data are used as a source for A286 material identity and room-temperature strength; elevated-temperature values in the app are intentionally marked as screening interpolation and must be replaced with qualified fastener data.

## Release statement
**FINAL v1.0** means this is the frozen software architecture and calculation workflow for this project build. It does NOT mean the resulting engineering dimensions are certified for flight. Any flight/qualification release requires approved loads, material allowables, supplier seal data, detailed joint analysis/FEA, fastener qualification, NDE/weld qualification and configuration control.
