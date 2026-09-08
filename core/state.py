
import streamlit as st

STEP_NAMES = {
    1: "Engine Inputs",
    2: "Pressure & Thrust",
    3: "Loads & FBD",
    4: "Thermal",
    5: "Flange Design",
    6: "Seal Design",
    7: "Bolt Design",
    8: "EBW vs Bolted",
    9: "Design Review",
    10: "Report",
}

def init_state():
    if "project" not in st.session_state:
        st.session_state.project = {
            "project_name": "Thrust Chamber / Nozzle Flange",
            "ambient_pressure_bar_abs": 1.01325,
            "test_orientation": "Vertical",
            "target_thrust_kN": 1200.0,
        }
    if "results" not in st.session_state:
        st.session_state.results = {}
    if "validation" not in st.session_state:
        st.session_state.validation = {}
    if "step_accepted" not in st.session_state:
        st.session_state.step_accepted = set()

def require_step(n):
    init_state()

def complete_step(n):
    st.session_state.step_accepted.add(n)

def back_button(n):
    if st.button(f"← Back to {STEP_NAMES.get(n, n)}", key=f"back_{n}"):
        st.switch_page(f"pages/{n:02d}_{STEP_NAMES[n].replace(' ', '_').replace('&','and')}.py")

def source_note(text):
    st.caption("Basis / source: " + text)
