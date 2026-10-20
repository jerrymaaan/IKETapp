import streamlit as st
from lib import logph
from CoolProp.CoolProp import PropsSI

###########################
# constants, functions, etc
###########################
P_ATM = 1.0  # bar

# set init values
if "fluid" not in st.session_state:
    st.session_state.fluid = "R290"

if "pressure_abs" not in st.session_state:
    st.session_state.pressure_abs = 10

if "pressure_rel" not in st.session_state:
    st.session_state.pressure_rel = st.session_state.pressure_abs - P_ATM

if "temperature" not in st.session_state:
    st.session_state.temperature = PropsSI('T', 'P', st.session_state.pressure_abs * 1e5, 'Q', 1,
                                           st.session_state.fluid) - 273.15

if "error" not in st.session_state:
    st.session_state.error = None


# update functions
def update_with_fluid():
    update_with_pressure_abs()


def update_with_temperature():
    try:
        # try calc
        pressure_abs = PropsSI('P', 'T', st.session_state.temperature + 273.15, 'Q', 1, st.session_state.fluid) / 1e5
        pressure_rel = pressure_abs - P_ATM

        # writes state if PropsSI succeeded
        st.session_state.pressure_abs = pressure_abs
        st.session_state.pressure_rel = pressure_rel
        st.session_state.error = None

    except ValueError as err:
        st.session_state.error = f"Ungültige Temperatureingabe ({err})"


def update_with_pressure_abs():
    try:
        # try calc
        pressure_rel = st.session_state.pressure_abs - P_ATM
        temperature = PropsSI('T', 'P', st.session_state.pressure_abs * 1e5, 'Q', 1, st.session_state.fluid) - 273.15

        # writes state if PropsSI succeeded
        st.session_state.pressure_rel = pressure_rel
        st.session_state.temperature = temperature
        st.session_state.error = None

    except ValueError as err:
        st.session_state.error = f"Ungültige Druckeingaben ({err})"


def update_with_pressure_rel():
    try:
        # try calc
        pressure_abs = st.session_state.pressure_rel + P_ATM
        temperature = PropsSI('T', 'P', pressure_abs * 1e5, 'Q', 1, st.session_state.fluid) - 273.15

        # writes state if PropsSI succeeded
        st.session_state.pressure_abs = pressure_abs
        st.session_state.temperature = temperature
        st.session_state.error = None
    except ValueError as err:
        st.session_state.error = f"Ungültige Druckeingaben ({err})"


###########################
# UI
###########################
st.title("Kältemittelschieber")

# dropdown
fluid = st.selectbox(
    "Kältemittel",
    ("R290", "R717", "R744", "R134a", "R32"),
    key="fluid",
    on_change=update_with_fluid,
)

# inputs
col1, col2 = st.columns(2)
with col1:
    st.number_input("Druck (bar; absolut)", key="pressure_abs", on_change=update_with_pressure_abs)
with col2:
    st.number_input("Druck (bar; relativ)", key="pressure_rel", on_change=update_with_pressure_rel)
st.number_input("Temperatur (°C)", key="temperature", on_change=update_with_temperature)

# show error if smth went wrong
if st.session_state.error:
    st.error(st.session_state.error)

# more info
with st.expander(f'Log(p)-h-Diagramm für {fluid}'):
    if st.session_state.error is None:
        try:
            with st.spinner("Log(p)-h Diagramm wird berechnet..."):
                # plot base logph
                fig, ax, diagram = logph.draw_empty_logph(fluid)

                # plot logph with pressure in tpm
                logph.add_tpm_point_to_logph(ax, diagram, st.session_state.pressure_abs)

            st.pyplot(fig)
        except (ValueError, RuntimeError, KeyError) as e:
            st.error(f"Diagramm konnte nicht erstellt werden: {e}")
