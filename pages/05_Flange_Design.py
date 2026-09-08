
import math
import streamlit as st
from core.state import init_state, complete_step
init_state()
st.title("05 — Flange Design")
st.caption("Size the chamber-side CuCrZr and nozzle-side IN718 flange halves separately. The page explains why each diameter and thickness exists.")

ld=st.session_state.results.get("loads",{}); th=st.session_state.results.get("thermal",{}); pr=st.session_state.results.get("pressure",{})
F=ld.get("load_nozzle_to_flange_N",[0,0,0]); M=ld.get("moment_nozzle_to_flange_Nm",[0,0,0])
Fx,Fy,Fz=map(float,F); Mx,My,Mz=map(float,M); Fres=math.sqrt(Fx**2+Fy**2+Fz**2); Mres=math.sqrt(Mx**2+My**2+Mz**2)

st.subheader("1. What loads does the flange actually see?")
st.write("These are the loads transmitted from the nozzle into the flange. The flange must react them while maintaining seal compression and preventing local yielding/separation.")
c1,c2,c3,c4=st.columns(4)
c1.metric("Fx",f"{Fx/1000:+.3f} kN"); c2.metric("Fy",f"{Fy/1000:+.3f} kN"); c3.metric("Resultant",f"{Fres/1000:.3f} kN"); c4.metric("Mz",f"{Mz/1000:+.4f} kN·m")

st.subheader("2. Geometry — why these diameters exist")
c1,c2,c3,c4=st.columns(4)
with c1: Dh=st.number_input("Hot-gas boundary ID [mm]",1.0,5000.0,340.0,1.0)
with c2: Ds=st.number_input("Seal mean diameter [mm]",Dh+1,5000.0,370.0,1.0)
with c3: Dp=st.number_input("Bolt PCD [mm]",Ds+1,5000.0,500.0,1.0)
with c4: Do=st.number_input("Flange OD [mm]",Dp+1,5000.0,550.0,1.0)
st.write(
    "**Hot-gas ID:** keeps the load path outside the hot-gas wall.  "
    "**Seal diameter:** places the seal outboard of the hot-gas boundary.  "
    "**PCD:** gives the bolts a lever arm to maintain clamp load and resist opening moment.  "
    "**Flange OD:** provides bolt-edge distance and bending section while remaining inside the common AM envelope."
)

st.subheader("3. Material properties")
c1,c2=st.columns(2)
with c1:
    st.markdown("**CuCrZr chamber side**")
    Ecu=st.number_input("E CuCrZr [GPa]",1.0,300.0,120.0,1.0)
    Sycu=st.number_input("Yield CuCrZr [MPa]",1.0,2000.0,240.0,5.0)
    foscu=st.number_input("Required FOS CuCrZr",1.0,5.0,2.0,0.1)
with c2:
    st.markdown("**IN718 nozzle side**")
    Ein=st.number_input("E IN718 [GPa]",1.0,300.0,200.0,1.0)
    Syin=st.number_input("Yield IN718 [MPa]",1.0,2000.0,1030.0,5.0)
    fosin=st.number_input("Required FOS IN718",1.0,5.0,2.0,0.1)

st.subheader("4. Pressure separation load")
project = st.session_state.project

Pj = float(pr.get("joint_pressure_bar_abs", 1.01325))
Pa = float(project.get("ambient_pressure_bar_abs", 1.01325))
dp = max(Pj - Pa, 0.0)
Deff=st.number_input("Pressure effective diameter [mm]",Dh,Ds,Ds,1.0)
Fp=dp*1e5*math.pi/4*(Deff/1000)**2
st.write(f"Local joint pressure = {Pj:.4f} bar abs; gauge pressure = {dp:.4f} bar.")
st.metric("Pressure opening force",f"{Fp/1000:.3f} kN")

st.subheader("5. Preliminary flange thickness")
st.write("The screening model combines a circumferential membrane term and a strip-bending term. This is a sizing model, not a substitute for circular-flange analysis or FEA.")
allowcu=Sycu/foscu; allowin=Syin/fosin
rhot=Dh/2
# conservative use of global axial load; bending line moment approximated at bolt circle
Mline=abs(Mz)*1000/(math.pi*Dp) # N since Nmm/mm
Fdesign=max(abs(Fx),Fp)
def size(allow):
    tmem=Fdesign/(2*math.pi*rhot*allow)
    tbend=math.sqrt(max(6*Mline/max(allow,1e-9),0))
    t=max(4,tmem,tbend)
    return tmem,tbend,t
cu=size(allowcu); ino=size(allowin)
c1,c2=st.columns(2)
with c1:
    st.markdown("### CuCrZr")
    st.metric("Allowable",f"{allowcu:.1f} MPa"); st.metric("Membrane t",f"{cu[0]:.2f} mm"); st.metric("Bending t",f"{cu[1]:.2f} mm"); st.metric("Recommended t",f"{math.ceil((cu[2]+2)*2)/2:.1f} mm")
with c2:
    st.markdown("### IN718")
    st.metric("Allowable",f"{allowin:.1f} MPa"); st.metric("Membrane t",f"{ino[0]:.2f} mm"); st.metric("Bending t",f"{ino[1]:.2f} mm"); st.metric("Recommended t",f"{math.ceil((ino[2]+2)*2)/2:.1f} mm")
st.info("Thickness is driven by load capacity and bending stiffness. The two materials are intentionally sized separately because their strength differs greatly.")

st.subheader("6. AM envelope")
c1,c2,c3=st.columns(3)
with c1: buildx=st.number_input("AM build X [mm]",100.0,3000.0,600.0,10.0)
with c2: buildy=st.number_input("AM build Y [mm]",100.0,3000.0,600.0,10.0)
with c3: edge=st.number_input("AM edge margin [mm]",0.0,100.0,10.0,1.0)
ammax=min(buildx,buildy)-2*edge
st.metric("Maximum circular AM OD",f"{ammax:.1f} mm")
if Do<=ammax: st.success("PASS — flange OD fits the common AM envelope.")
else: st.error("FAIL — flange OD exceeds AM envelope.")

st.session_state.results["flange"]={
"hot_id_mm":Dh,"seal_mean_diameter_mm":Ds,"bolt_pcd_mm":Dp,"flange_od_mm":Do,
"pressure_effective_diameter_mm":Deff,"pressure_opening_N":Fp,
"chamber_flange_thickness_mm":math.ceil((cu[2]+2)*2)/2,
"nozzle_flange_thickness_mm":math.ceil((ino[2]+2)*2)/2,
"chamber_allowable_MPa":allowcu,"nozzle_allowable_MPa":allowin,
"chamber_structural_t_mm":cu[2],"nozzle_structural_t_mm":ino[2],
"am_max_od_mm":ammax,"design_F_N":Fdesign,"design_M_Nm":Mres,
}
with st.expander("Why PCD and OD matter",expanded=True):
    st.write("PCD increases the bolt lever arm and spreads the clamp load. OD provides bolt-edge distance and section stiffness. Both increase manufacturing envelope and mass, so neither should be maximized blindly.")
if st.button("Accept Flange Design & Continue →",type="primary"):
    complete_step(5); st.switch_page("pages/06_Seal_Design.py")
