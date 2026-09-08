
import streamlit as st
from core.state import init_state
init_state()
st.title("09 — Design Review")
st.caption("One page for the engineer/reviewer: what was selected, why it was selected, and what remains open.")

p=st.session_state.project; pr=st.session_state.results.get("pressure",{}); ld=st.session_state.results.get("loads",{})
th=st.session_state.results.get("thermal",{}); fl=st.session_state.results.get("flange",{}); se=st.session_state.results.get("seal",{}); b=st.session_state.results.get("bolt",{}); ew=st.session_state.results.get("ebw",{})

st.subheader("Engineering summary")
rows=[
["Joint pressure",f"{pr.get('joint_pressure_bar_abs',0):.4f} bar abs","Local pressure at flange; used for separation"],
["Flange axial load",f"{ld.get('load_nozzle_to_flange_N',[0])[0]/1000:.3f} kN","Nozzle → flange"],
["Flange bending Mz",f"{ld.get('moment_nozzle_to_flange_Nm',[0,0,0])[2]/1000:.4f} kN·m","CG / applied moment"],
["Thermal mismatch",f"{th.get('differential_thermal_strain',0)*1e6:.1f} µε","Free CTE mismatch"],
["CuCrZr thickness",f"{fl.get('chamber_flange_thickness_mm','—')} mm","Preliminary screening"],
["IN718 thickness",f"{fl.get('nozzle_flange_thickness_mm','—')} mm","Preliminary screening"],
["Seal family",se.get("family","—"),"Supplier-specific"],
["Seal clamp load",f"{se.get('minimum_total_clamp_load_N',0)/1000:.2f} kN","Seating + hydrostatic basis"],
["Bolt arrangement",f"{b.get('N','—')} × M{b.get('d_mm','—')}","Preliminary"],
["Bolt preload",f"{b.get('preload_nominal_N',0)/1000:.2f} kN/bolt","Nominal"],
["Hot bolt utilization",f"{b.get('yield_utilization',0)*100:.1f}%","Screening"],
]
st.table({"Parameter":[r[0] for r in rows],"Result":[r[1] for r in rows],"Meaning":[r[2] for r in rows]})

st.subheader("Why the geometry?")
st.write(f"**PCD:** {fl.get('bolt_pcd_mm','—')} mm — provides the bolt lever arm and distributes clamp load around the seal.")
st.write(f"**Flange OD:** {fl.get('flange_od_mm','—')} mm — provides bolt edge distance and bending section while staying within AM limits.")
st.write(f"**Seal diameter:** {se.get('mean_diameter_mm','—')} mm — establishes the sealing circumference and seating-load path.")
st.write(f"**Bolt size/count:** {b.get('N','—')} × M{b.get('d_mm','—')} — selected to provide the required preload and distribute external load without exceeding the screening bolt limits.")

st.subheader("Open engineering items")
open_items=[
"Pressure field must be a qualified design-basis steady-state distribution.",
"Material allowables must be replaced with qualified temperature-dependent data for actual AM/heat-treated conditions.",
"Metal seal size, coating/jacket, compression and groove geometry must come from the selected supplier.",
"Detailed flange/bolt joint stiffness and separation analysis is still required; current clamped-member stiffness is simplified.",
"Thermal bolt preload requires a coupled thermal/structural model for final design.",
"Fastener preload method and torque-tension correlation require qualification.",
"Fatigue, preload relaxation, embedment and cyclic thermal/pressure loading require dedicated assessment.",
"Final local flange, bolt-hole, seal-groove and fillet stresses require FEA or an applicable validated design method.",
"EBW requires representative dissimilar-material qualification and NDE acceptance criteria.",
]
for x in open_items: st.checkbox(x, value=False, key="review_"+x[:10])
st.error("Release status: PRELIMINARY / ENGINEERING SCREENING — not flight-release.")
