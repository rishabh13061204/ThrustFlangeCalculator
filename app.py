
import streamlit as st
from core.state import init_state, STEP_NAMES

st.set_page_config(
    page_title="Thrust Joint Design Calculator",
    page_icon="🔩",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_state()

pg = st.navigation([
    st.Page("pages/00_Home.py", title="Home", icon="🏠"),
    st.Page("pages/01_Engine_Inputs.py", title="01 Engine Inputs", icon="🚀"),
    st.Page("pages/02_Pressure_and_Thrust.py", title="02 Pressure & Thrust", icon="📈"),
    st.Page("pages/03_Loads_and_FBD.py", title="03 Loads & FBD", icon="⚖️"),
    st.Page("pages/04_Thermal.py", title="04 Thermal", icon="🌡️"),
    st.Page("pages/05_Flange_Design.py", title="05 Flange Design", icon="⭕"),
    st.Page("pages/06_Seal_Design.py", title="06 Seal Design", icon="🛡️"),
    st.Page("pages/07_Bolt_Design.py", title="07 Bolt Design", icon="🔩"),
    st.Page("pages/08_EBW_vs_Bolted.py", title="08 EBW vs Bolted", icon="⚡"),
    st.Page("pages/09_Design_Review.py", title="09 Design Review", icon="✅"),
    st.Page("pages/10_Report.py", title="10 Report", icon="📄"),
])
pg.run()
