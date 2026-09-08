
import streamlit as st
import math
from core.state import init_state, complete_step
init_state()

st.title("01 — Engine Inputs")
st.caption("Define the geometry, operating condition and ground-test configuration used by every downstream calculation.")

st.subheader("1. What are these inputs?")
st.write(
    "These values establish the physical reference frame and the pressure/geometry model. "
    "The calculator will not silently substitute chamber pressure for local joint pressure."
)

p = st.session_state.project
c1,c2,c3 = st.columns(3)
with c1:
    p["project_name"] = st.text_input("Project / hardware name", p.get("project_name","Thrust Chamber / Nozzle Flange"))
    p["target_thrust_kN"] = st.number_input("Target thrust [kN]", value=float(p.get("target_thrust_kN",1200)), min_value=0.0, step=10.0)
with c2:
    p["chamber_pressure_bar_abs"] = st.number_input("Chamber pressure [bar abs]", value=float(p.get("chamber_pressure_bar_abs",110)), min_value=0.0, step=1.0)
    p["ambient_pressure_bar_abs"] = st.number_input("Ambient pressure [bar abs]", value=float(p.get("ambient_pressure_bar_abs",1.01325)), min_value=0.0, step=0.001, format="%.5f")
with c3:
    p["test_orientation"] = st.radio("Ground-test orientation", ["Vertical","Horizontal"], horizontal=True)
    p["axis_angle_deg"] = st.number_input("Engine-axis angle above ground [deg]", 0.0 if p["test_orientation"]=="Vertical" else 0.0, 90.0, 90.0 if p["test_orientation"]=="Vertical" else 0.0, 1.0)

st.subheader("2. Reference geometry")
c1,c2,c3,c4 = st.columns(4)
with c1:
    p["chamber_diameter_mm"] = st.number_input("Chamber / inlet diameter [mm]", value=float(p.get("chamber_diameter_mm",479.2)), min_value=1.0, step=1.0)
with c2:
    p["throat_diameter_mm"] = st.number_input("Throat diameter [mm]", value=float(p.get("throat_diameter_mm",289.0)), min_value=1.0, step=1.0)
with c3:
    p["joint_diameter_mm"] = st.number_input("Joint effective diameter [mm]", value=float(p.get("joint_diameter_mm",368.0)), min_value=1.0, step=1.0)
with c4:
    p["exit_diameter_mm"] = st.number_input("Nozzle exit diameter [mm]", value=float(p.get("exit_diameter_mm",1119.3)), min_value=1.0, step=1.0)

c1,c2,c3 = st.columns(3)
with c1:
    p["chamber_length_mm"] = st.number_input("Chamber length [mm]", value=float(p.get("chamber_length_mm",369.8)), min_value=0.0, step=1.0)
with c2:
    p["nozzle_length_mm"] = st.number_input("Nozzle length from joint [mm]", value=float(p.get("nozzle_length_mm",1113.3)), min_value=0.0, step=1.0)
with c3:
    p["joint_x_mm_from_throat"] = st.number_input("Joint plane downstream of throat [mm]", value=float(p.get("joint_x_mm_from_throat",126.2)), min_value=0.0, step=0.1)

st.subheader("3. Ground-test load significance")
st.info(
    "The engine-axis angle controls how gravity resolves into axial and lateral components. "
    "Nozzle mass and CG are entered on Page 03. Chamber mass is deliberately excluded from this "
    "isolated nozzle-flange free body."
)

st.subheader("4. Sanity checks")
At = math.pi*(p["throat_diameter_mm"]/1000)**2/4
cf_req = (p["target_thrust_kN"]*1000)/(At*p["chamber_pressure_bar_abs"]*1e5) if p["chamber_pressure_bar_abs"]>0 else 0
c1,c2 = st.columns(2)
c1.metric("Throat area", f"{At*1e6:.1f} mm²")
c2.metric("Required Cf at chamber pressure", f"{cf_req:.3f}")
if cf_req > 3:
    st.error("REVIEW — target thrust, throat diameter and chamber pressure are not mutually plausible under a simple thrust-coefficient check.")
else:
    st.success("Basic thrust-coefficient sanity check is plausible.")

if st.button("Accept Engine Inputs & Continue →", type="primary"):
    st.session_state.validation["engine"] = cf_req <= 3
    complete_step(1)
    st.switch_page("pages/02_Pressure_and_Thrust.py")
