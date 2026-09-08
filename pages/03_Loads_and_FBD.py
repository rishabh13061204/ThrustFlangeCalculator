
import math
import numpy as np
import streamlit as st
from core.state import init_state, complete_step
init_state()
loads=st.session_state.results.get("pressure",{})
p=st.session_state.project

st.title("03 — Loads & Free-Body Diagram")
st.caption("Isolate the nozzle. Every force and moment is resolved at the flange plane, X=Y=Z=0.")

st.subheader("1. Ground-test attitude")
orient=st.radio("Test configuration",["Vertical","Horizontal"],horizontal=True)
theta=st.number_input("Engine-axis angle above ground [deg]",0.0,90.0,90.0 if orient=="Vertical" else 0.0,1.0)
g=9.80665
if orient=="Vertical":
    gx,gy,gz=0,g,0
else:
    a=math.radians(theta)
    gx,gy,gz=-g*math.sin(a),g*math.cos(a),0
st.info("Physical meaning: +Y is downward along gravity in the vertical reference. The nozzle is below the flange, so its weight loads the flange in +Y.")
st.write(f"Gravity vector = [{gx:+.6f}, {gy:+.6f}, {gz:+.6f}] m/s²; magnitude = {math.sqrt(gx*gx+gy*gy+gz*gz):.6f} m/s²")

st.subheader("2. Nozzle mass & centre of gravity")
c1,c2,c3,c4=st.columns(4)
with c1: mass=st.number_input("Nozzle mass [kg]",0.0,1e6,100.0,1.0)
with c2: cgx=st.number_input("CG X from flange [mm]",-1e6,1e6,500.0,1.0)
with c3: cgy=st.number_input("CG Y from flange [mm]",-1e6,1e6,0.0,1.0)
with c4: cgz=st.number_input("CG Z from flange [mm]",-1e6,1e6,0.0,1.0)
W=np.array([mass*gx,mass*gy,mass*gz])
r=np.array([cgx,cgy,cgz])/1000
M_w=np.cross(r,W)

st.subheader("3. Additional ground-test loads")
c1,c2,c3=st.columns(3)
with c1: ext=np.array([st.number_input("External axial Fx [kN]",value=0.0),st.number_input("External lateral Fy [kN]",value=0.0),0.0])*1000
with c2: trans=np.array([st.number_input("Startup/transient Fx [kN]",value=0.0),st.number_input("Startup/transient Fy [kN]",value=0.0),0.0])*1000
with c3:
    M_ext=np.array([0.0,0.0,st.number_input("Additional Mz [kN·m]",value=0.0)])*1000

pressure_force=np.array([float(loads.get("pressure_resultant_N",0.0)),0.0,0.0])
F_external=pressure_force+W+ext+trans
R_nozzle=-F_external
F_flange=F_external
M_external=M_w+M_ext
M_reaction=-M_external
M_flange=M_external
Fres=np.linalg.norm(F_external)

st.subheader("4. Free-body equilibrium")
df={
"Load":[
"Page 02 pressure resultant","Nozzle gravity","Additional external","Startup/transient",
"TOTAL EXTERNAL ON NOZZLE","JOINT REACTION ON NOZZLE","LOAD APPLIED BY NOZZLE TO FLANGE"],
"Fx [kN]":[pressure_force[0]/1000,W[0]/1000,ext[0]/1000,trans[0]/1000,F_external[0]/1000,R_nozzle[0]/1000,F_flange[0]/1000],
"Fy [kN]":[pressure_force[1]/1000,W[1]/1000,ext[1]/1000,trans[1]/1000,F_external[1]/1000,R_nozzle[1]/1000,F_flange[1]/1000],
"Fz [kN]":[0, W[2]/1000,0,0,F_external[2]/1000,R_nozzle[2]/1000,F_flange[2]/1000],
}
st.dataframe(df,use_container_width=True,hide_index=True)

st.subheader("5. CG moment")
st.write(f"Weight moment = [{M_w[0]:+.3f}, {M_w[1]:+.3f}, {M_w[2]:+.3f}] N·m")
st.write(f"Flange moment = [{M_flange[0]:+.3f}, {M_flange[1]:+.3f}, {M_flange[2]:+.3f}] N·m")
eqF=np.linalg.norm(F_external+R_nozzle)
eqM=np.linalg.norm(M_external+M_reaction)
if eqF<1e-6 and eqM<1e-6:
    st.success("NOZZLE FREE-BODY EQUILIBRIUM: PASS")
else: st.error("Equilibrium check failed.")

st.subheader("6. Loads passed to flange design")
c1,c2,c3,c4=st.columns(4)
c1.metric("Fx",f"{F_flange[0]/1000:+.3f} kN")
c2.metric("Fy",f"{F_flange[1]/1000:+.3f} kN")
c3.metric("Resultant",f"{Fres/1000:.3f} kN")
c4.metric("Mz",f"{M_flange[2]/1000:+.4f} kN·m")
st.info("Downstream pages use the nozzle → flange vector, not the reaction-on-nozzle vector.")

st.session_state.results["loads"]={
"load_nozzle_to_flange_N":F_flange.tolist(),
"moment_nozzle_to_flange_Nm":M_flange.tolist(),
"pressure_reaction_on_nozzle_N":pressure_force.tolist(),
"weight_vector_N":W.tolist(),
"gravity_vector_m_s2":[gx,gy,gz],
"nozzle_mass_kg":mass,"cg_mm":[cgx,cgy,cgz],
"resultant_force_N":Fres,
"gravity_moment_Nm":M_w.tolist(),
"equilibrium_force_error_N":eqF,"equilibrium_moment_error_Nm":eqM,
}
if st.button("Accept Loads & Continue →",type="primary"):
    complete_step(3); st.switch_page("pages/04_Thermal.py")
