
import math
import streamlit as st
from core.state import init_state, complete_step
init_state()
st.title("04 — Thermal / CTE Mismatch")
st.caption("Thermal page answers: how much do the two flange materials want to move differently, and how strongly could the joint restrain that movement?")

st.subheader("1. Joint temperatures")
c1,c2,c3=st.columns(3)
with c1: Tref=st.number_input("Assembly/reference temperature [°C]",20.0,500.0,20.0,1.0)
with c2: Tcu=st.number_input("CuCrZr flange temperature [°C]",-100.0,1000.0,100.0,5.0)
with c3: Tin=st.number_input("IN718 flange temperature [°C]",-100.0,1000.0,100.0,5.0)
st.info("Reference temperature is the temperature at which the joint is assumed stress-free for this screening calculation. Flange temperature means metal temperature in the load path, not hot-gas temperature.")

st.subheader("2. Material behaviour")
c1,c2=st.columns(2)
with c1:
    st.markdown("**CuCrZr / C18160**")
    acu=st.number_input("CTE α [µm/m·K]",0.0,100.0,18.6,0.1)
    Ecu=st.number_input("E [GPa]",1.0,300.0,120.0,1.0)
with c2:
    st.markdown("**IN718**")
    ain=st.number_input("CTE α [µm/m·K]",0.0,100.0,13.0,0.1)
    Ein=st.number_input("E [GPa]",1.0,300.0,200.0,1.0)

st.subheader("3. Geometry used to express mismatch")
c1,c2,c3=st.columns(3)
with c1: D=st.number_input("Joint effective diameter [mm]",1.0,5000.0,368.0,1.0)
with c2: PCD=st.number_input("Bolt-circle diameter [mm]",0.0,5000.0,500.0,1.0)
with c3: L=st.number_input("Reference axial length [mm]",0.0,5000.0,100.0,1.0)

dTcu=Tcu-Tref; dTin=Tin-Tref
ecu=acu*1e-6*dTcu; ein=ain*1e-6*dTin; ed=ecu-ein
dDcu=ecu*D; dDin=ein*D; dD=dDcu-dDin
dPCD=(ecu-ein)*PCD
dLcu=ecu*L; dLin=ein*L

st.subheader("4. Free expansion — physical significance")
st.write("This is what each material would do if it were free. The difference is the mismatch the joint must accommodate or restrain.")
c1,c2,c3=st.columns(3)
c1.metric("CuCrZr strain",f"{ecu*1e6:+.1f} µε")
c2.metric("IN718 strain",f"{ein*1e6:+.1f} µε")
c3.metric("Differential strain",f"{ed*1e6:+.1f} µε")
st.write(f"Axial free expansion: CuCrZr {dLcu:+.5f} mm; IN718 {dLin:+.5f} mm; difference {dLcu-dLin:+.5f} mm.")
st.write(f"Diameter growth: CuCrZr {dDcu:+.5f} mm; IN718 {dDin:+.5f} mm; difference {dD:+.5f} mm.")
st.write(f"PCD mismatch: {dPCD:+.5f} mm.")

st.subheader("5. What is the restraint factor?")
st.write(
    "The restraint factor R is a sensitivity parameter, not a material property. R=0 means the two parts are "
    "allowed to expand freely and the mismatch creates essentially no elastic restraint force. R=1 is a deliberately "
    "conservative upper-bound screen in which the selected differential strain is treated as fully suppressed. "
    "The real joint lies somewhere between these limits and depends on flange stiffness, bolt stiffness, contact, "
    "seal stiffness, friction and temperature gradients."
)
R=st.slider("Illustrative restraint factor R",0.0,1.0,0.25,0.05)
sigcu=R*Ecu*1e3*abs(ed); sigin=R*Ein*1e3*abs(ed)
st.write(f"Restrained stress sensitivity: CuCrZr {sigcu:.2f} MPa; IN718 {sigin:.2f} MPa.")
st.warning("Do not add this stress directly to Page 05 as a force. It is a sensitivity screen. The final thermal joint load is resolved in the bolt/joint stiffness model.")

st.subheader("6. Imported mechanical load")
ld=st.session_state.results.get("loads",{})
fv=ld.get("load_nozzle_to_flange_N",[0,0,0]); mv=ld.get("moment_nozzle_to_flange_Nm",[0,0,0])
st.write(f"Page 03 flange load = [{fv[0]/1000:+.3f}, {fv[1]/1000:+.3f}, {fv[2]/1000:+.3f}] kN")
st.write(f"Page 03 flange moment = [{mv[0]/1000:+.4f}, {mv[1]/1000:+.4f}, {mv[2]/1000:+.4f}] kN·m")

st.session_state.results["thermal"]={
"T_ref_C":Tref,"T_cuCrZr_C":Tcu,"T_IN718_C":Tin,"alpha_cu":acu,"alpha_in718":ain,
"E_cu_GPa":Ecu,"E_in718_GPa":Ein,"differential_thermal_strain":ed,
"differential_D_mm":dD,"differential_PCD_mm":dPCD,"differential_axial_mm":dLcu-dLin,
"restraint_factor":R,"screened_stress_cu_MPa":sigcu,"screened_stress_in718_MPa":sigin,
}
with st.expander("Traceability",expanded=True):
    st.latex(r"\varepsilon_{th}=\alpha\Delta T")
    st.latex(r"\Delta L=\alpha\Delta T L")
    st.latex(r"\Delta D=\alpha\Delta T D")
    st.latex(r"\sigma_{screen}=R E |\Delta\varepsilon_{diff}|")
if st.button("Accept Thermal Model & Continue →",type="primary"):
    complete_step(4); st.switch_page("pages/05_Flange_Design.py")
