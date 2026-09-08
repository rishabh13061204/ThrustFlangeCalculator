
import math
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from core.state import init_state, complete_step
init_state()
p = st.session_state.project

st.title("02 — Pressure & Thrust")
st.caption("Convert the pressure distribution into a physically traceable pressure resultant and, most importantly, determine the pressure at the flange joint.")

st.subheader("1. Why pressure distribution matters")
st.write(
    "The flange does not automatically see chamber pressure. The pressure acting at the joint is the "
    "local internal pressure at the joint station. For joint separation, the relevant pressure difference "
    "is normally internal minus external pressure over the effective pressure area."
)

# Default validation dataset
default_ch = pd.DataFrame({
    "x_mm":[-700,-500,-300,-150,-100,-50,0],
    "diameter_mm":[479.2,479.2,450,360,330,310,368],
    "pressure_bar_abs":[22.13,22.0,21.9,20.5,15.0,6.0,1.0419],
})
default_noz = pd.DataFrame({
    "x_mm":[0,1.5,100,200,500,900,1113.3],
    "diameter_mm":[368,290,320,430,700,1050,1119.3],
    "pressure_bar_abs":[1.0419,1.0329,0.75,0.15,0.10,0.09,0.081],
})

def _find_col(df, candidates):
    """Find a CSV column by normalized name."""
    normalized = {str(c).strip().lower().replace(" ", "").replace("-", "").replace("_", ""): c for c in df.columns}
    for candidate in candidates:
        key = candidate.lower().replace(" ", "").replace("-", "").replace("_", "")
        if key in normalized:
            return normalized[key]
    return None

def _csv_to_pressure_table(uploaded, existing_geometry):
    """
    Convert a CSV into the Page-02 schema.
    Accepted x columns include x_mm / x_calculator / x / position.
    Accepted pressure columns include pressure_bar_abs / pressure_bar / pressure / bar.
    Diameter is optional. If omitted, diameter is interpolated from the existing
    manual geometry table.
    """
    raw = pd.read_csv(uploaded)
    if raw.empty:
        raise ValueError("CSV is empty.")

    x_col = _find_col(raw, [
        "x_mm", "x_calculator", "x_calculator_mm", "x", "position_mm",
        "axial_position_mm", "distance_mm"
    ])
    p_col = _find_col(raw, [
        "pressure_bar_abs", "pressure_bar", "pressure_abs_bar",
        "pressure", "bar", "pressure_abs"
    ])
    d_col = _find_col(raw, [
        "diameter_mm", "diameter", "d_mm", "dia_mm"
    ])

    if x_col is None or p_col is None:
        raise ValueError(
            "CSV must contain an axial-position column and a pressure column. "
            "Examples: x_mm + pressure_bar_abs, or X_calculator + Pressure."
        )

    out = pd.DataFrame({
        "x_mm": pd.to_numeric(raw[x_col], errors="coerce"),
        "pressure_bar_abs": pd.to_numeric(raw[p_col], errors="coerce"),
    })

    if d_col is not None:
        out["diameter_mm"] = pd.to_numeric(raw[d_col], errors="coerce")
    else:
        # Pressure-only CSVs are supported. Geometry remains controlled by
        # the user's current Page-02 geometry stations and is interpolated.
        geom = existing_geometry.copy()
        geom["x_mm"] = pd.to_numeric(geom["x_mm"], errors="coerce")
        geom["diameter_mm"] = pd.to_numeric(geom["diameter_mm"], errors="coerce")
        geom = geom.dropna(subset=["x_mm", "diameter_mm"]).sort_values("x_mm")
        if len(geom) < 2:
            raise ValueError(
                "CSV has no diameter column. At least two valid manual geometry "
                "stations are required so diameter can be interpolated."
            )
        out["diameter_mm"] = np.interp(
            out["x_mm"].to_numpy(),
            geom["x_mm"].to_numpy(),
            geom["diameter_mm"].to_numpy()
        )

    out = out[["x_mm", "diameter_mm", "pressure_bar_abs"]].dropna()
    out = out.sort_values("x_mm").drop_duplicates("x_mm", keep="last")
    if len(out) < 2:
        raise ValueError("CSV must contain at least two valid pressure stations.")
    return out.reset_index(drop=True)

if "pressure_ch_data" not in st.session_state:
    st.session_state["pressure_ch_data"] = default_ch.copy()
if "pressure_nz_data" not in st.session_state:
    st.session_state["pressure_nz_data"] = default_noz.copy()
if "pressure_table_version" not in st.session_state:
    st.session_state["pressure_table_version"] = 0

st.subheader("2. Pressure stations")
st.info(
    "Enter steady-state or design-basis stations manually, or import pressure-distribution CSVs below. "
    "Do not scale startup/transient data to the design chamber pressure unless the pressure field itself is justified."
)

with st.expander("2.1 Import pressure distribution from CSV", expanded=False):
    st.caption(
        "CSV import accepts either a complete table (x + pressure + diameter) or a pressure-only CSV "
        "(x + pressure). For pressure-only CSVs, diameter is interpolated from the current manual geometry."
    )
    csv_c1, csv_c2 = st.columns(2)
    with csv_c1:
        ch_csv = st.file_uploader(
            "Chamber / converging-side CSV",
            type=["csv"],
            key="pressure_ch_csv"
        )
    with csv_c2:
        nz_csv = st.file_uploader(
            "Nozzle / divergent-side CSV",
            type=["csv"],
            key="pressure_nz_csv"
        )

    import_col1, import_col2 = st.columns(2)
    with import_col1:
        import_ch = st.button("Import Chamber CSV", key="import_ch_csv", type="secondary")
    with import_col2:
        import_nz = st.button("Import Nozzle CSV", key="import_nz_csv", type="secondary")

    if import_ch:
        if ch_csv is None:
            st.error("Select a chamber CSV first.")
        else:
            try:
                # Use the current geometry table as the interpolation basis.
                geom = st.session_state["pressure_ch_data"]
                st.session_state["pressure_ch_data"] = _csv_to_pressure_table(ch_csv, geom)
                st.session_state["pressure_table_version"] += 1
                st.session_state.pop("pressure_ch_editor", None)
                st.success(
                    f"Imported {len(st.session_state['pressure_ch_data'])} chamber pressure stations."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Chamber CSV import failed: {exc}")

    if import_nz:
        if nz_csv is None:
            st.error("Select a nozzle CSV first.")
        else:
            try:
                geom = st.session_state["pressure_nz_data"]
                st.session_state["pressure_nz_data"] = _csv_to_pressure_table(nz_csv, geom)
                st.session_state["pressure_table_version"] += 1
                st.session_state.pop("pressure_nz_editor", None)
                st.success(
                    f"Imported {len(st.session_state['pressure_nz_data'])} nozzle pressure stations."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Nozzle CSV import failed: {exc}")

with st.form("pressure_form"):
    st.markdown("**Chamber / converging side**")
    ch = st.data_editor(
        st.session_state["pressure_ch_data"],
        num_rows="dynamic",
        use_container_width=True,
        key=f"pressure_ch_editor_{st.session_state['pressure_table_version']}"
    )
    st.markdown("**Nozzle / divergent side**")
    nz = st.data_editor(
        st.session_state["pressure_nz_data"],
        num_rows="dynamic",
        use_container_width=True,
        key=f"pressure_nz_editor_{st.session_state['pressure_table_version']}"
    )
    ambient = st.number_input(
        "Ambient pressure [bar abs]",
        value=float(p.get("ambient_pressure_bar_abs",1.01325)),
        step=0.001,
        format="%.5f"
    )
    submitted = st.form_submit_button(
        "Apply / Recalculate Pressure Model",
        type="primary"
    )

if submitted or "pressure" not in st.session_state.results:
    def clean(df):
        d=df.copy()
        for col in ["x_mm","diameter_mm","pressure_bar_abs"]:
            d[col]=pd.to_numeric(d[col], errors="coerce")
        d=d.dropna().sort_values("x_mm")
        return d
    ch=clean(ch); nz=clean(nz)
    # Persist the user's manual edits so they remain the geometry basis for
    # later pressure-only CSV imports.
    st.session_state["pressure_ch_data"] = ch.copy()
    st.session_state["pressure_nz_data"] = nz.copy()
    allst=pd.concat([ch,nz]).drop_duplicates(subset=["x_mm"], keep="last").sort_values("x_mm")
    # local joint pressure by interpolation
    pj = float(np.interp(0.0, allst["x_mm"].to_numpy(), allst["pressure_bar_abs"].to_numpy()))
    D_local = float(np.interp(0.0, allst["x_mm"].to_numpy(), allst["diameter_mm"].to_numpy()))
    dp=max(pj-ambient,0.0)
    Aeff=math.pi/4*(D_local/1000)**2
    opening=dp*1e5*Aeff

    # Pressure thrust estimate from axisymmetric internal surface:
    # axial force on a differential conical surface = p * pi*D * sin(theta) dx
    # sin(theta)=dr/ds; with x as axis and r(x), dA_x=2*pi*r*dr.
    # Numerically integrate p * pi*D * dD/dx /2? 2*pi*r dr = pi D dD.
    x=allst["x_mm"].to_numpy()/1000
    D=allst["diameter_mm"].to_numpy()/1000
    P=(allst["pressure_bar_abs"].to_numpy()-ambient)*1e5
    dDdx=np.gradient(D,x,edge_order=1)
    wall_axial=np.trapezoid(P*math.pi*D*dDdx,x)
    # Boundary opening terms for a control volume: inlet pressure on inlet plane and exit pressure on exit plane.
    Pin=(ch.iloc[0]["pressure_bar_abs"]-ambient)*1e5 if len(ch) else 0
    Din=(ch.iloc[0]["diameter_mm"]/1000) if len(ch) else D[0]
    Pexit=(nz.iloc[-1]["pressure_bar_abs"]-ambient)*1e5 if len(nz) else P[-1]
    Dexit=(nz.iloc[-1]["diameter_mm"]/1000) if len(nz) else D[-1]
    inlet_boundary=Pin*math.pi*Din**2/4
    exit_boundary=Pexit*math.pi*Dexit**2/4
    pressure_resultant=wall_axial + inlet_boundary - exit_boundary
    target=p.get("target_thrust_kN",0)*1000
    cf_req=target/(Aeff*pj*1e5) if pj>0 else 0

    st.session_state.results["pressure"]={
        "status":"Calculated",
        "joint_pressure_bar_abs":pj,
        "joint_pressure_gauge_bar":dp,
        "joint_diameter_mm":D_local,
        "pressure_opening_N":opening,
        "pressure_resultant_N":pressure_resultant,
        "wall_axial_N":wall_axial,
        "inlet_boundary_N":inlet_boundary,
        "exit_boundary_N":exit_boundary,
        "target_thrust_N":target,
        "cf_required_joint_basis":cf_req,
        "chamber_stations":ch.to_dict("records"),
        "nozzle_stations":nz.to_dict("records"),
        "ambient_pressure_bar_abs":ambient,
        "basis":"Gauge pressure used for wall traction and joint separation. Joint opening load uses local pressure at x=0.",
    }

r=st.session_state.results.get("pressure",{})
if r:
    st.subheader("3. Results")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Local joint pressure", f"{r['joint_pressure_bar_abs']:.4f} bar abs")
    c2.metric("Joint gauge pressure", f"{r['joint_pressure_gauge_bar']:.4f} bar")
    c3.metric("Pressure opening load", f"{r['pressure_opening_N']/1000:.3f} kN")
    c4.metric("Pressure resultant", f"{r['pressure_resultant_N']/1000:.3f} kN")

    st.subheader("4. Why the local joint pressure is important")
    st.info(
        f"At the current joint station the model gives {r['joint_pressure_bar_abs']:.4f} bar abs. "
        f"That is the pressure used for joint opening, not the {p.get('chamber_pressure_bar_abs',0):.2f} bar chamber pressure."
    )

    fig,ax=plt.subplots(figsize=(9,4))
    for df,label in [(pd.DataFrame(r["chamber_stations"]),"Chamber"),(pd.DataFrame(r["nozzle_stations"]),"Nozzle")]:
        ax.plot(df["x_mm"],df["pressure_bar_abs"],marker="o",label=label)
    ax.axvline(0,linestyle="--")
    ax.set_xlabel("x from joint [mm]"); ax.set_ylabel("Pressure [bar abs]"); ax.legend(); ax.grid(True,alpha=.25)
    st.pyplot(fig,use_container_width=True); plt.close(fig)

    with st.expander("Traceability",expanded=True):
        st.latex(r"p_g=p_{abs}-p_{ambient}")
        st.latex(r"F_{joint}=\Delta p\frac{\pi D_{eff}^2}{4}")
        st.latex(r"dF_{wall,x}=p_g\,2\pi r\,dr")
        st.write("The pressure-force model is a numerical axisymmetric surface-traction integration. The joint opening force is reported separately because it is the quantity used directly in the flange separation check.")

    if abs(r["pressure_resultant_N"]-r["target_thrust_N"])/max(abs(r["target_thrust_N"]),1)>0.10:
        st.warning("Pressure resultant and target thrust differ by more than 10%. Review the pressure field, throat/geometry, and operating point.")
    else:
        st.success("Pressure resultant is within 10% of target thrust.")

if st.button("Accept Pressure Model & Continue →",type="primary"):
    complete_step(2)
    st.switch_page("pages/03_Loads_and_FBD.py")
