
import streamlit as st
from core.state import init_state, STEP_NAMES

init_state()
st.title("Thrust Chamber / Nozzle Flange Design Calculator")
st.subheader("Release candidate — engineering screening and joint-pre-sizing tool")

st.warning(
    "This software is intentionally conservative about its claims: it is a traceable "
    "engineering pre-sizing tool. A final flight/qualification release still requires "
    "approved loads, material allowables, seal supplier data, detailed joint analysis/FEA, "
    "fastener qualification and applicable program standards."
)

st.markdown("""
### What changed in this final architecture

The calculator is organized around the physical load path:

**Engine geometry → pressure field → nozzle free body → thermal mismatch → flange → seal → bolt joint → EBW/bolted decision → review**

Every major output has four labels:

- **What it means physically**
- **Why it matters**
- **How it is calculated**
- **What it is being compared against**

### How to use it

1. Enter the engine and test configuration.
2. Enter or paste the pressure distribution at the joint and along the nozzle.
3. Validate the nozzle free-body.
4. Enter actual joint temperatures and material properties.
5. Size the two flange halves separately.
6. Select the seal family and enter supplier data.
7. Let the bolt model determine preload, bolt load, separation margin, torque and thermal effects.
8. Compare bolted vs qualified EBW.
9. Read the Design Review page. **Green does not mean flight-certified; it means the entered screening checks pass.**
""")

st.divider()
st.subheader("Current design chain")
for n in range(1, 11):
    status = "✅" if n in st.session_state.step_accepted else "○"
    st.write(f"{status} **{n:02d} — {STEP_NAMES[n]}**")

st.divider()
st.info(
    "Important convention: the flange/joint plane is X=Y=Z=0. +X is downstream. "
    "For the vertical ground-test configuration, +Y is downward with gravity. "
    "The nozzle is below the flange, so nozzle weight acts +Y and loads the flange in +Y."
)
