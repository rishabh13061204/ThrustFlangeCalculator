
import streamlit as st
from core.state import init_state, complete_step
init_state()
st.title("08 — EBW vs Bolted Joint")
st.caption("Compare the two joint architectures against the actual requirements rather than treating EBW as automatically superior.")

st.subheader("1. Bolted joint")
b=st.session_state.results.get("bolt",{})
c1,c2,c3=st.columns(3)
c1.metric("Bolts",str(b.get("N","—"))); c2.metric("Bolt size",f"M{b.get('d_mm','—')}"); c3.metric("Torque",f"{b.get('torque_Nm',0):.1f} N·m")
st.write("Strengths: inspectable joint, replaceable seal, adjustable preload, easier disassembly. Risks: preload scatter, separation, thermal preload change, bolt-hole stress, cyclic fatigue.")

st.subheader("2. EBW joint")
c1,c2,c3=st.columns(3)
with c1: ebw_qualified=st.checkbox("Representative dissimilar-material EBW qualified",False)
with c2: ndt=st.checkbox("Weld NDE procedure qualified",False)
with c3: process=st.checkbox("Production EBW process qualified",False)
st.write("For IN718 ↔ CuCrZr, qualification must be representative of the actual materials, geometry, thickness, heat input and defect acceptance criteria. A generic CuCrZr-to-CuCrZr result is not sufficient evidence for a dissimilar-material production joint.")

if ebw_qualified and ndt and process:
    st.success("EBW architecture can be considered for program review, subject to detailed qualification evidence.")
else:
    st.warning("EBW is NOT yet a release-ready architecture because one or more qualification gates are incomplete.")

st.subheader("3. Architecture recommendation")
st.write(
    "For first flight-representative development, the bolted metal-seal architecture is the lower integration-risk baseline "
    "unless the representative dissimilar EBW process is already qualified. EBW can remove bolt/seal hardware and mass, but "
    "moves risk into weld metallurgy, distortion, NDE, repairability and qualification."
)
st.session_state.results["ebw"]={
"qualified":ebw_qualified and ndt and process,
"recommendation":"Bolted baseline unless representative dissimilar EBW qualification is complete."
}
if st.button("Accept Joint Architecture & Continue →",type="primary"):
    complete_step(8); st.switch_page("pages/09_Design_Review.py")
