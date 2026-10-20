import streamlit as st
from lib import logph, calc_cp

###########################
# constants, functions, etc
###########################
FLUID_SLIDER_SETTINGS = {
    "R290": {
        "p_min": 1,
        "p_max": 42,
        "p_default_min": 4,
        "p_default_max": 15,
    },
    "R717": {
        "p_min": 1,
        "p_max": 113,
        "p_default_min": 5,
        "p_default_max": 20,
    },
    "R744": {
        "p_min": 6,
        "p_max": 73,
        "p_default_min": 10,
        "p_default_max": 30,
    },
    "R134a": {
        "p_min": 1,
        "p_max": 40,
        "p_default_min": 3,
        "p_default_max": 13,
    },
    "R32": {
        "p_min": 1,
        "p_max": 40,
        "p_default_min": 3,
        "p_default_max": 13,
    },
}

###########################
# UI
###########################
st.title("Kältekreislauf-Rechner")

# dropdown
fluid = st.selectbox(
    "Kältemittel",
    FLUID_SLIDER_SETTINGS.keys(),
)

# sliders for refrigerant cycle
# double slider
p_low, p_high = st.slider(
    "Niederdruck und Hochdruck (bar; absolut)",
    FLUID_SLIDER_SETTINGS[fluid]["p_min"], FLUID_SLIDER_SETTINGS[fluid]["p_max"],
    (FLUID_SLIDER_SETTINGS[fluid]["p_default_min"], FLUID_SLIDER_SETTINGS[fluid]["p_default_max"])
)

# sliders next to each other
col1, col2 = st.columns(2)
with col1:
    subcooling = st.slider("Unterkühlung (K)", 0, 10, 0)
with col2:
    superheat = st.slider("Überhitzung (K)", 0, 20, 5)

col3, col4 = st.columns(2, vertical_alignment="bottom")
with col4:
    use_hg = st.toggle("Stattdessen Heißgas Temperatur verwenden")
with col3:
    if use_hg:
        hg_pre = calc_cp.precalculate_hg(p_high, p_low, superheat, fluid)
        hot_gas_temp = st.slider("Heißgas Temperatur (°C)", hg_pre, hg_pre + 50, hg_pre)
        eta_s = None
    else:
        eta_s = st.slider("Isentroper Wirkungsgrad", 0.0, 1.0, 1.0, step=0.1, format="%.1f")
        hot_gas_temp = None

# more sliders
massflow = st.slider(r"Massenstrom ($\frac{kg}{h}$)", 5, 300, 150, step=5)

# do calculation for plots and more data
plot_data, calc_data = calc_cp.calc_cycle_data(p_high, p_low, subcooling, superheat, fluid, massflow, eta_s, hot_gas_temp)

# plot window and spinner
st.title(f'Log(p)-h-Diagramm für {fluid}')
try:
    with st.spinner("Log(p)-h Diagramm wird berechnet..."):
        # plot base logph
        fig, ax, diagram = logph.draw_empty_logph(fluid)

        # plot logph with refrigerant cycle
        logph.add_cycle_to_logph(ax, diagram, plot_data)
    st.pyplot(fig)
except (ValueError, RuntimeError, KeyError) as e:
    st.error(f"Diagramm konnte nicht erstellt werden: {e}")

# show more data
st.title(f'Ergebnisse für {fluid}')

col5, col6 = st.columns(2)
with col5:
    st.write('Verdampfungstemperatur $T_0$ =', round(calc_data["t_0"], 2), '°C')
with col6:
    st.write('Verflüssigungstemperatur $T_C$ =', round(calc_data["t_c"], 2), '°C')

st.write('Verdichterleistung = ', round(calc_data["p_compressor"], 2), 'kW')
col7, col8 = st.columns(2)
with col7:
    st.write('Kälteleistung = ', round(calc_data["q_evaporation"], 2), 'kW')
with col8:
    st.write('Wärmeleistung = ', round(calc_data["q_condensing"], 2), 'kW')

col9, col10 = st.columns(2)
with col9:
    st.write('EER = ', round(calc_data["eer"], 2))
with col10:
    st.write('COP = ', round(calc_data["cop"], 2))

with st.expander("Weitere Ergebnisse"):
    st.write(r"$\Delta h_0$ =", round(calc_data["delta_h_0"], 2), r"$\frac{kJ}{kg}$")
    st.write(r"$\Delta h_C$ =", round(calc_data["delta_h_c"], 2), r"$\frac{kJ}{kg}$")
    st.write("Heißgastemperatur =", round(calc_data["hot_gas_temp"], 2), "°C")
    st.write(r"Isentroper Wirkungsgrad $\eta_s$ =", round(calc_data["eta_s"], 2))
