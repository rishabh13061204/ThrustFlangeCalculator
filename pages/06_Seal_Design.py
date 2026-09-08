
import math
import streamlit as st
from core.state import init_state, complete_step
init_state()
st.title("06 — Seal Design")
st.caption("Select the seal architecture and translate supplier seal requirements into flange/bolt preload requirements.")

st.subheader("1. Why the seal is a structural load")
st.write(
    "A metal seal is not just a leak-prevention component. It requires a defined seating load to create contact pressure "
    "against the flange faces. That seating load becomes part of the required bolt preload. During operation, system pressure "
    "can pressure-energize some metal-seal geometries."
)

family=st.selectbox("Seal family",[
    "HELICOFLEX — resilient metal seal",
    "E-FLEX — metal E-ring",
    "C-FLEX — metal C-ring",
    "O-FLEX — metal O-ring",
    "Elastomeric O-ring — screening only"
])
st.info(
    "For a hot-gas rocket joint, the metal-seal families are the primary architecture to investigate. "
    "Actual size, jacket, spring/core material, coating and seating load must come from the selected supplier's quotation/catalogue."
)

st.subheader("2. Seal geometry")
c1,c2,c3,c4=st.columns(4)
with c1: ID=st.number_input("Seal ID [mm]",1.0,5000.0,350.0,1.0)
with c2: OD=st.number_input("Seal OD [mm]",ID+0.1,5000.0,390.0,1.0)
with c3: cs=st.number_input("Seal cross-section [mm]",0.1,100.0,5.0,0.1)
with c4: coating=st.text_input("Jacket/coating", "Supplier-defined")

Dmean=(ID+OD)/2
st.metric("Seal mean diameter",f"{Dmean:.2f} mm")
st.write("The seal mean diameter defines the circumferential sealing path and therefore strongly influences seating load and pressure opening area.")

st.subheader("3. Supplier seating data")
c1,c2,c3=st.columns(3)
with c1: y2=st.number_input("Required seating line load Y₂ [N/mm]",1.0,10000.0,120.0,1.0)
with c2: seal_sf=st.number_input("Seal seating safety factor",1.0,3.0,1.5,0.1)
with c3: pmax=st.number_input("Supplier qualified pressure limit [bar]",0.0,5000.0,100.0,5.0)

seat=math.pi*Dmean*y2*seal_sf
Pj=st.session_state.results.get("pressure",{}).get("joint_pressure_bar_abs",1.01325)
hyd=max(Pj-st.session_state.project.get("ambient_pressure_bar_abs",1.01325),0)*1e5*math.pi/4*(Dmean/1000)**2
bolt_min=seat+hyd

st.subheader("4. Seal load result")
c1,c2,c3=st.columns(3)
c1.metric("Seal seating load",f"{seat/1000:.2f} kN")
c2.metric("Hydrostatic opening load",f"{hyd/1000:.3f} kN")
c3.metric("Minimum total clamp-load basis",f"{bolt_min/1000:.2f} kN")
if Pj<=pmax: st.success("Pressure is within the entered supplier qualification limit.")
else: st.error("FAIL — local pressure exceeds the entered supplier qualification limit.")

st.subheader("5. Surface finish / groove meaning")
st.write(
    "The seal needs a controlled contact surface so the seal can conform to flange imperfections. "
    "For HELICOFLEX-type seals, supplier guidance uses groove geometry, compression and sealing-surface finish as coupled parameters; "
    "do not invent groove dimensions independently of the selected seal."
)
st.warning("This page intentionally does not generate a 'universal' metal-seal groove. The groove is supplier-specific and must follow the selected seal's design data.")

st.session_state.results["seal"]={
"family":family,"ID_mm":ID,"OD_mm":OD,"cross_section_mm":cs,"mean_diameter_mm":Dmean,
"seating_line_load_N_per_mm":y2,"seating_sf":seal_sf,"seating_load_N":seat,
"hydrostatic_load_N":hyd,"minimum_total_clamp_load_N":bolt_min,
"qualified_pressure_bar":pmax,"coating":coating,
"basis":"Supplier-specific metal-seal seating data required; universal groove dimensions are not generated."
}
if st.button("Accept Seal Model & Continue →",type="primary"):
    complete_step(6); st.switch_page("pages/07_Bolt_Design.py")
