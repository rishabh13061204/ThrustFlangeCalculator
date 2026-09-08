
import math
import pandas as pd
import streamlit as st
from core.state import init_state, complete_step

init_state()

st.title("07 — Bolt Design")
st.caption(
    "Final joint-level screening: bolt material behaviour, preload, bolt/joint stiffness, "
    "load sharing, separation, thermal preload change, torque and candidate selection."
)

ld = st.session_state.results.get("loads", {})
fl = st.session_state.results.get("flange", {})
th = st.session_state.results.get("thermal", {})
seal = st.session_state.results.get("seal", {})

F = ld.get("load_nozzle_to_flange_N", [0.0, 0.0, 0.0])
M = ld.get("moment_nozzle_to_flange_Nm", [0.0, 0.0, 0.0])
Fx, Fy, Fz = map(float, F)
Mx, My, Mz = map(float, M)
Fres = math.sqrt(Fx**2 + Fy**2 + Fz**2)
Mres = math.sqrt(Mx**2 + My**2 + Mz**2)

PCD_design = float(fl.get("bolt_pcd_mm", 500.0))
flange_od = float(fl.get("flange_od_mm", 550.0))
seal_d = float(seal.get("mean_diameter_mm", 370.0))
seal_required_total = float(seal.get("minimum_total_clamp_load_N", 0.0))

st.subheader("1. What the bolt joint must accomplish")
st.write(
    "The bolts must maintain enough clamp force to seat the seal and keep the joint closed while "
    "external axial force, bending, pressure, and temperature changes act on the assembly. "
    "A bolt is therefore sized by **strength + stiffness + preload + joint separation**, not tensile strength alone."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Nozzle → flange Fx", f"{Fx/1000:+.3f} kN")
c2.metric("Resultant force", f"{Fres/1000:.3f} kN")
c3.metric("Flange moment", f"{Mres/1000:.4f} kN·m")
c4.metric("Seal clamp requirement", f"{seal_required_total/1000:.2f} kN")

# -------------------------------------------------------------------------
# Candidate inputs / geometry
# -------------------------------------------------------------------------
st.subheader("2. Joint geometry used by the bolt model")
c1, c2, c3, c4 = st.columns(4)
with c1:
    min_pcd = st.number_input(
        "Minimum allowed PCD [mm]", 50.0, 5000.0,
        max(float(seal_d + 40.0), 50.0), 1.0,
        help="Must remain outside the seal and provide the required seal-to-bolt radial clearance."
    )
with c2:
    max_pcd = st.number_input(
        "Maximum allowed PCD [mm]", min_pcd, 5000.0,
        max(min_pcd + 80.0, PCD_design), 1.0,
        help="Limited by flange OD, bolt edge distance and the common AM envelope."
    )
with c3:
    bolt_edge = st.number_input(
        "Minimum bolt-center to flange OD edge [mm]", 1.0, 200.0, 15.0, 1.0
    )
with c4:
    hole_clear = st.number_input(
        "Nominal radial hole clearance [mm]", 0.5, 10.0, 1.5, 0.5
    )

st.info(
    "PCD physical meaning: moving the bolts farther from the joint centre increases their moment arm and "
    "usually improves resistance to flange opening/rotation, but consumes flange width and increases mass. "
    "The useful PCD is therefore a **design window**, not simply the largest possible diameter."
)

# -------------------------------------------------------------------------
# Fastener material behaviour
# -------------------------------------------------------------------------
st.subheader("3. Fastener material behaviour")
material = st.selectbox(
    "Fastener material",
    ["A286 / UNS S66286", "IN718 / UNS N07718", "Other — qualified material"]
)

defaults = {
    "A286 / UNS S66286": dict(E=199.0, Sy=655.0, Su=965.0, alpha=16.5, proof=550.0),
    "IN718 / UNS N07718": dict(E=200.0, Sy=1030.0, Su=1240.0, alpha=13.0, proof=900.0),
    "Other — qualified material": dict(E=200.0, Sy=700.0, Su=900.0, alpha=13.0, proof=600.0),
}
dflt = defaults[material]

c1, c2, c3, c4 = st.columns(4)
with c1:
    Tbolt = st.number_input("Bolt operating temperature [°C]", -100.0, 1000.0, 100.0, 5.0)
with c2:
    E_hot = st.number_input(
        "E at operating temperature [GPa]", 20.0, 300.0,
        float(dflt["E"]), 1.0,
        help="Enter qualified temperature-dependent modulus. For A286/IN718, published modulus decreases with temperature."
    )
with c3:
    Sy_hot = st.number_input(
        "Yield / proof allowable at operating temperature [MPa]", 50.0, 2500.0,
        float(dflt["Sy"]), 5.0,
        help="Use the approved fastener lot/specification value at the actual operating temperature."
    )
with c4:
    Su_hot = st.number_input(
        "Ultimate allowable at operating temperature [MPa]", 50.0, 3000.0,
        float(dflt["Su"]), 5.0,
    )

c1, c2 = st.columns(2)
with c1:
    alpha_b = st.number_input(
        "Bolt CTE [µm/m·K]", 0.0, 30.0, float(dflt["alpha"]), 0.1
    )
with c2:
    proof_hot = st.number_input(
        "Proof / preload-control allowable [MPa]", 50.0, 2500.0,
        float(dflt["proof"]), 5.0
    )

st.warning(
    "Fastener strength is temperature- and heat-treatment-dependent. The calculator does not invent "
    "an elevated-temperature allowable from room-temperature strength. Enter the qualified value for "
    "the actual bolt material, heat treatment, diameter and temperature."
)

# -------------------------------------------------------------------------
# Thread geometry
# -------------------------------------------------------------------------
st.subheader("4. Bolt dimensions")
c1, c2, c3 = st.columns(3)
with c1:
    d = st.selectbox(
        "Nominal bolt diameter [mm]",
        [12, 14, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 42],
        index=2
    )
with c2:
    pitch = st.selectbox(
        "Metric thread pitch [mm]",
        [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
        index=3
    )
with c3:
    grip = st.number_input(
        "Effective grip length [mm]", 10.0, 1000.0, 60.0, 1.0,
        help="Elastic length of the bolt over the clamped joint. Longer grip generally lowers bolt stiffness."
    )

# ISO-style screening tensile stress area
As = math.pi / 4.0 * (d - 0.9382 * pitch) ** 2
root_d = d - 1.22687 * pitch
Aroot = math.pi / 4.0 * root_d ** 2

st.write(
    f"M{d}×{pitch:.2f}: tensile-stress area ≈ **{As:.1f} mm²**; "
    f"thread-root area screen ≈ **{Aroot:.1f} mm²**."
)

# -------------------------------------------------------------------------
# Number of bolts / preload
# -------------------------------------------------------------------------
st.subheader("5. Number of bolts and preload")
c1, c2, c3, c4 = st.columns(4)
with c1:
    N = st.number_input("Number of bolts", 4, 96, 12, 2)
with c2:
    preload_fraction = st.number_input(
        "Nominal preload / proof fraction", 0.30, 0.85, 0.60, 0.01
    )
with c3:
    preload_scatter = st.number_input(
        "Preload scatter ± fraction", 0.00, 0.30, 0.10, 0.01
    )
with c4:
    nut_factor = st.number_input(
        "Nut factor K", 0.10, 0.30, 0.20, 0.01
    )

# Limit nominal preload by both proof/yield and ultimate-based ductile/brittle screening.
# NASA-STD-5020B describes 0.85 Ptu-allow for ductile and 0.75 for brittle in the separation-before-rupture framework.
ductile_limit = 0.85 * Su_hot
preload_allow_stress = min(preload_fraction * proof_hot, ductile_limit)
Ppre_nom = preload_allow_stress * As
Ppre_min = Ppre_nom * (1.0 - preload_scatter)
Ppre_max = Ppre_nom * (1.0 + preload_scatter)

required_seal_per_bolt = seal_required_total / max(N, 1)

c1, c2, c3 = st.columns(3)
c1.metric("Nominal preload / bolt", f"{Ppre_nom/1000:.2f} kN")
c2.metric("Minimum preload / bolt", f"{Ppre_min/1000:.2f} kN")
c3.metric("Seal load / bolt", f"{required_seal_per_bolt/1000:.2f} kN")

if Ppre_min >= required_seal_per_bolt:
    st.success("PASS — minimum preload covers the entered seal seating requirement.")
else:
    st.error("FAIL — minimum preload is insufficient for seal seating.")

st.write(
    "Physical meaning: preload is the clamp force installed before firing. "
    "It must be high enough to seat the seal and maintain contact, but not so high that the bolt "
    "is already consuming too much of its temperature-dependent strength."
)

# -------------------------------------------------------------------------
# Bolt/joint stiffness
# -------------------------------------------------------------------------
st.subheader("6. Bolt stiffness vs joint stiffness")
st.write(
    "An applied tensile load does not all go into the bolt. Part increases bolt tension and part unloads the "
    "clamped joint. The split depends on bolt stiffness and local joint stiffness."
)

# Effective clamped area: conservative annular area. User may override because actual compression cone depends on geometry.
Do = float(fl.get("flange_od_mm", flange_od))
Dh = float(fl.get("hot_id_mm", 340.0))
tcu = float(fl.get("chamber_flange_thickness_mm", 10.0))
tin = float(fl.get("nozzle_flange_thickness_mm", 10.0))
t_joint = max(tcu + tin, 1.0)

stiffness_mode = st.radio(
    "Clamped-member stiffness basis",
    ["Screening annular model", "User-qualified joint stiffness"],
    horizontal=True
)

kb = E_hot * 1000.0 * As / max(grip, 1e-9)

if stiffness_mode == "Screening annular model":
    Acl = math.pi / 4.0 * max(Do**2 - Dh**2, 1.0)
    kc = E_hot * 1000.0 * Acl / t_joint
    kc_basis = "Annular compression-area screen"
else:
    kc = st.number_input(
        "Qualified clamped-member stiffness kc [kN/mm]",
        0.01, 1e6, 100.0, 1.0
    ) * 1000.0
    kc_basis = "User-qualified value"

phi = kb / max(kb + kc, 1e-12)

c1, c2, c3 = st.columns(3)
c1.metric("Bolt stiffness kb", f"{kb/1000:.2f} kN/mm")
c2.metric("Joint stiffness kc", f"{kc/1000:.2f} kN/mm")
c3.metric("Stiffness factor φ", f"{phi:.3f}")

st.info(
    f"φ = kb/(kb+kc) = {phi:.3f}. In the linear model, φ is the fraction of a load introduced "
    "at the joint that appears as bolt-load increase before separation. The actual load-introduction "
    "factor depends on where the external load enters the joint."
)

# -------------------------------------------------------------------------
# External load sharing and separation
# -------------------------------------------------------------------------
st.subheader("7. External load sharing and separation")
load_introduction = st.number_input(
    "Load-introduction factor n", 0.10, 1.00, 0.25, 0.01,
    help="Represents how strongly the applied tensile load is introduced into the bolt/joint load path."
)

# Direct axial load distributed equally; moment creates first-order sinusoidal bolt-group load.
bolt_axial_share = abs(Fx) / max(N, 1)
bolt_moment_share = 0.0
if PCD_design > 0:
    bolt_moment_share = abs(Mz) / max(N * (PCD_design / 2.0 / 1000.0), 1e-9)

applied_per_bolt = bolt_axial_share + bolt_moment_share
bolt_load_increment = load_introduction * phi * applied_per_bolt
bolt_load_before_thermal = Ppre_nom + bolt_load_increment

# NASA-style separation screen: minimum preload is the primary conservative separation criterion.
# Also report linear residual clamp after applied unloading.
clamp_unload_per_bolt = (1.0 - load_introduction * phi) * applied_per_bolt
residual_clamp = Ppre_min - clamp_unload_per_bolt

c1, c2, c3, c4 = st.columns(4)
c1.metric("Axial share / bolt", f"{bolt_axial_share/1000:.2f} kN")
c2.metric("Moment share / bolt", f"{bolt_moment_share/1000:.2f} kN")
c3.metric("Bolt load increase", f"{bolt_load_increment/1000:.2f} kN")
c4.metric("Residual clamp", f"{residual_clamp/1000:.2f} kN")

if residual_clamp > 0:
    st.success("PASS — linear joint screen remains clamped under the entered mechanical load.")
else:
    st.error("FAIL — linear joint screen predicts loss of clamp.")

# -------------------------------------------------------------------------
# Thermal preload
# -------------------------------------------------------------------------
st.subheader("8. Thermal bolt preload change")
st.write(
    "Bolt and clamped members generally have different CTEs. When temperature changes, their free elongations "
    "differ. Because they are assembled together, that mismatch changes bolt preload."
)

Tref = float(th.get("T_ref_C", 20.0))
Tmember_cu = float(th.get("T_cuCrZr_C", 100.0))
Tmember_in = float(th.get("T_IN718_C", 100.0))
Tbolt = st.number_input("Bolt temperature used for preload-change calculation [°C]", -100.0, 1000.0, Tmember_in, 5.0)

alpha_cu = float(th.get("alpha_cu", 18.6)) * 1e-6
alpha_in = float(th.get("alpha_in718", 13.0)) * 1e-6

# Effective clamped-member CTE: stiffness-weighted average of the two flange sides.
cu_E = float(fl.get("chamber_E_GPa", 120.0))
in_E = float(fl.get("nozzle_E_GPa", 200.0))
w_cu = max(cu_E * tcu, 1e-9)
w_in = max(in_E * tin, 1e-9)
alpha_member_eff = (w_cu * alpha_cu + w_in * alpha_in) / (w_cu + w_in)

deltaT = Tbolt - Tref
free_bolt = alpha_b * deltaT * grip
free_member = alpha_member_eff * deltaT * grip
delta_free = free_bolt - free_member

thermal_preload_change = -E_hot * 1000.0 * As * delta_free / max(grip, 1e-9)
# Negative means bolt preload falls because bolt expands more than effective member.
bolt_hot = bolt_load_before_thermal + thermal_preload_change

c1, c2, c3 = st.columns(3)
c1.metric("Effective member CTE", f"{alpha_member_eff*1e6:.2f} µm/m·K")
c2.metric("Differential free elongation", f"{delta_free:+.5f} mm")
c3.metric("Thermal preload change", f"{thermal_preload_change/1000:+.2f} kN/bolt")

st.write(f"Hot operating bolt load screen = **{bolt_hot/1000:.2f} kN/bolt**.")

# -------------------------------------------------------------------------
# Strength, proof, ultimate
# -------------------------------------------------------------------------
st.subheader("9. Bolt strength / material utilization")
stress_hot = bolt_hot / max(As, 1e-12)
yield_util = stress_hot / max(Sy_hot, 1e-12)
ultimate_util = stress_hot / max(Su_hot, 1e-12)
proof_util = stress_hot / max(proof_hot, 1e-12)

c1, c2, c3 = st.columns(3)
c1.metric("Hot tensile stress", f"{stress_hot:.1f} MPa")
c2.metric("Proof/yield utilization", f"{proof_util*100:.1f}%")
c3.metric("Ultimate utilization", f"{ultimate_util*100:.1f}%")

if proof_util <= 1.0 and ultimate_util <= 0.9:
    st.success("PASS — hot bolt stress is within the entered proof/yield and ultimate screening limits.")
else:
    st.error("FAIL / REVIEW — bolt stress exceeds one of the entered material limits.")

st.info(
    "Material behaviour considered here: temperature-dependent modulus input, temperature-dependent "
    "proof/yield and ultimate allowable inputs, CTE-driven preload change, preload scatter, and "
    "elastic load sharing. Creep, relaxation and fatigue require separate qualification data."
)

# -------------------------------------------------------------------------
# Torque
# -------------------------------------------------------------------------
st.subheader("10. Torque / preload control")
torque = nut_factor * Ppre_nom * d / 1000.0
c1, c2 = st.columns(2)
c1.metric("Nominal torque estimate", f"{torque:.1f} N·m")
c2.metric("Preload from torque equation", f"{Ppre_nom/1000:.2f} kN/bolt")
st.write(
    "Torque is an indirect preload-control method. Friction scatter can dominate the achieved preload. "
    "For critical hardware, direct bolt elongation, ultrasonic measurement, or a validated torque–tension "
    "procedure should be used and qualified."
)
st.latex(r"T=KFd")

# -------------------------------------------------------------------------
# Automatic candidate ranking
# -------------------------------------------------------------------------
st.subheader("11. Why this bolt diameter and number?")
st.write(
    "The optimizer should choose the smallest practical arrangement that satisfies seal seating, "
    "joint-clamp, proof/yield and ultimate limits while remaining inside the PCD window. "
    "The table below shows the candidate logic rather than hiding the selection."
)

candidate_rows = []
for cand_d in [16, 18, 20, 22, 24, 27, 30]:
    cand_pitch = 2.0 if cand_d <= 24 else 2.5
    cand_As = math.pi/4*(cand_d-0.9382*cand_pitch)**2
    for cand_N in [8, 10, 12, 16, 20, 24]:
        for cand_pcd in sorted(set([min_pcd, 0.5*(min_pcd+max_pcd), max_pcd])):
            # bolt-group moment share
            cand_mshare = abs(Mz) / max(cand_N*(cand_pcd/2/1000),1e-9)
            cand_ashare = abs(Fx)/cand_N
            cand_applied = cand_ashare + cand_mshare
            cand_kb = E_hot*1000*cand_As/max(grip,1e-9)
            cand_phi = cand_kb/max(cand_kb+kc,1e-12)
            cand_inc = load_introduction*cand_phi*cand_applied
            cand_pre = min(preload_fraction*proof_hot,0.85*Su_hot)*cand_As
            cand_pre_min = cand_pre*(1-preload_scatter)
            cand_residual = cand_pre_min-(1-load_introduction*cand_phi)*cand_applied
            cand_hot = cand_pre+cand_inc+thermal_preload_change*(cand_As/As)
            cand_stress = cand_hot/cand_As
            cand_seal = cand_pre_min >= seal_required_total/cand_N
            cand_clamp = cand_residual > 0
            cand_strength = cand_stress <= Sy_hot and cand_stress <= 0.9*Su_hot
            cand_edge = cand_pcd/2 + bolt_edge + cand_d/2 <= flange_od/2
            cand_pass = cand_seal and cand_clamp and cand_strength and cand_edge
            if cand_pass:
                score = cand_N*cand_d + 0.02*cand_pcd
                candidate_rows.append({
                    "Bolt":f"M{cand_d}×{cand_pitch:.1f}",
                    "Count":cand_N,
                    "PCD [mm]":round(cand_pcd,1),
                    "Min clamp [kN]":round(cand_residual/1000,2),
                    "Hot stress [MPa]":round(cand_stress,1),
                    "Status":"PASS",
                    "_score":score
                })

if candidate_rows:
    cand_df=pd.DataFrame(candidate_rows).sort_values("_score").drop(columns="_score")
    st.dataframe(cand_df.head(12),use_container_width=True,hide_index=True)
    best=cand_df.iloc[0]
    st.success(
        f"Screening selection: **{best['Bolt']} × {int(best['Count'])} @ PCD {best['PCD [mm]']:.1f} mm**. "
        "This is selected because it is the lowest-score candidate that satisfies the entered screening checks."
    )
else:
    st.error("No candidate in the current search space passes all screening checks. Increase bolt size/count or revise the PCD window.")

st.caption(
    "The candidate ranking is a screening optimizer. Final bolt selection must also consider thread engagement, "
    "hole bearing, net-section, washer/nut geometry, installation access, fatigue, relaxation, corrosion, "
    "thermal gradients and fastener qualification."
)

st.session_state.results["bolt"] = {
    "N": N,
    "d_mm": d,
    "pitch_mm": pitch,
    "As_mm2": As,
    "root_area_mm2": Aroot,
    "grip_mm": grip,
    "material": material,
    "T_C": Tbolt,
    "E_hot_GPa": E_hot,
    "Sy_hot_MPa": Sy_hot,
    "Su_hot_MPa": Su_hot,
    "proof_hot_MPa": proof_hot,
    "alpha_bolt": alpha_b,
    "kb_N_per_mm": kb,
    "kc_N_per_mm": kc,
    "phi": phi,
    "preload_nominal_N": Ppre_nom,
    "preload_min_N": Ppre_min,
    "preload_max_N": Ppre_max,
    "seal_requirement_per_bolt_N": required_seal_per_bolt,
    "applied_per_bolt_N": applied_per_bolt,
    "bolt_increment_N": bolt_load_increment,
    "residual_clamp_N_per_bolt": residual_clamp,
    "thermal_load_change_N": thermal_preload_change,
    "hot_operating_load_N": bolt_hot,
    "hot_stress_MPa": stress_hot,
    "proof_utilization": proof_util,
    "yield_utilization": yield_util,
    "ultimate_utilization": ultimate_util,
    "torque_Nm": torque,
    "candidate_table": candidate_rows,
    "basis": (
        "NASA-STD-5020B conceptual basis for threaded fastening preload, stiffness, load sharing and separation; "
        "joint stiffness is a screening model unless user supplies qualified stiffness. "
        "Temperature-dependent fastener properties are explicit inputs. Creep/relaxation/fatigue require qualification."
    ),
}

if st.button("Accept Bolt Design & Continue →", type="primary"):
    complete_step(7)
    st.switch_page("pages/08_EBW_vs_Bolted.py")
