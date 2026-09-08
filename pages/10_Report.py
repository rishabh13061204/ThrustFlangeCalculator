
import json
import streamlit as st
from core.state import init_state
init_state()
st.title("10 — Report")
st.caption("Traceable summary for design reviews. Export the current calculation state as JSON.")

p=st.session_state.project; results=st.session_state.results
st.subheader("Design basis")
st.write(f"Project: {p.get('project_name','—')}")
st.write(f"Target thrust: {p.get('target_thrust_kN','—')} kN")
st.write(f"Chamber pressure: {p.get('chamber_pressure_bar_abs','—')} bar abs")
st.write(f"Ground test: {p.get('test_orientation','—')}")

for name,title in [
("pressure","Pressure"),("loads","Loads"),("thermal","Thermal"),("flange","Flange"),
("seal","Seal"),("bolt","Bolt"),("ebw","EBW")
]:
    with st.expander(title,expanded=False):
        st.json(results.get(name,{}))

payload={"project":p,"results":results,"release_note":"Engineering screening / pre-sizing; not flight release."}
st.download_button(
    "Download complete calculation state (JSON)",
    data=json.dumps(payload,indent=2,default=str),
    file_name="thrust_joint_calculation_state.json",
    mime="application/json"
)
st.warning("The JSON is the traceability record. For controlled release, archive it together with the approved input data, material certificates, seal supplier data and analysis review.")
