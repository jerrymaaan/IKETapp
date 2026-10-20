from fluprodia import FluidPropertyDiagram
import matplotlib.pyplot as plt
import numpy as np
from CoolProp.CoolProp import PropsSI
import streamlit as st

FLUID_DIAGRAM_SETTINGS = {
    "R290": {
        "t_min": -40,
        "t_max": 80,
        "t_step": 20,
        "h_min": 0,
        "h_max": 800,
        "p_min": 1,
        "p_max": 100,
    },
    "R717": {
        "t_min": -20,
        "t_max": 120,
        "t_step": 20,
        "h_min": 0,
        "h_max": 2500,
        "p_min": 1,
        "p_max": 200,
    },
    "R744": {
        "t_min": -50,
        "t_max": 30,
        "t_step": 10,
        "h_min": 0,
        "h_max": 600,
        "p_min": 6,
        "p_max": 100,
    },
    "R134a": {
        "t_min": -20,
        "t_max": 120,
        "t_step": 10,
        "h_min": 100,
        "h_max": 500,
        "p_min": 1,
        "p_max": 100,
    }
}


@st.cache_resource
def _get_diagram(fluid):
    diagram = FluidPropertyDiagram(fluid)

    # sets units
    diagram.set_unit_system(
        temperature="degC", pressure="bar", pressure_difference="bar", enthalpy="kJ/kg",
        heat="kW", power="kW", mass_flow="kg/S"
    )

    # gets fluid diagram settings
    settings = FLUID_DIAGRAM_SETTINGS[fluid]

    # define and calculate isolines
    temp = np.arange(
        settings["t_min"],
        settings["t_max"] + 1,
        settings["t_step"]
    )
    diagram.set_isolines(T=temp)
    diagram.calc_isolines()

    # return (cached) object
    return diagram


def draw_empty_logph(fluid):
    # gets (cached) diagram object
    diagram = _get_diagram(fluid)

    # gets fluid diagram settings
    settings = FLUID_DIAGRAM_SETTINGS[fluid]

    # create fig (figure, plot window) and ax (axes, coordinate system)
    # plt is kinda the matplotlib api
    fig, ax = plt.subplots(1)

    # draw plot with isolines
    diagram.draw_isolines(
        fig, ax,
        "logph",
        settings["h_min"],
        settings["h_max"],
        settings["p_min"],
        settings["p_max"]
    )

    # change y-axis to p_abs
    ax.set_ylabel(r"$p_{abs}$ in bar")

    # return fig for streamlit
    # no caching for fig, ax because it will get modified
    # plt.tight_layout()
    # fig.tight_layout()
    return fig, ax, diagram


def calc_cycle_data(p_high, p_low, subcooling, superheat,
                    fluid, massflow, eta_s, hot_gas_temp):
    # convert unity
    p_high_si = p_high * 1e5  # bar to Pa
    p_low_si = p_low * 1e5  # bar to Pa
    massflow_si = massflow / 3600  # kh/h to kg/s

    # cycle point 1
    t_1_0_si = PropsSI('T', 'P', p_low_si, 'Q', 1, fluid)
    if superheat == 0:
        h_1_si = PropsSI('H', 'P', p_low_si, 'Q', 1, fluid)
        s_1_si = PropsSI('S', 'P', p_low_si, 'Q', 1, fluid)
    else:
        t_1_si = t_1_0_si + superheat  # in K
        h_1_si = PropsSI('H', 'P', p_low_si, 'T', t_1_si, fluid)
        s_1_si = PropsSI('S', 'P', p_low_si, 'T', t_1_si, fluid)

    # cycle point 2
    s_2_isentropic = s_1_si
    h_2s_si = PropsSI('H', 'P', p_high_si, 'S', s_2_isentropic, fluid)

    if hot_gas_temp:
        # hot_gas_temp given, eta_s is None
        hot_gas_temp_si = hot_gas_temp + 273.15  # °C to K
        h_2_si = PropsSI('H', 'P', p_high_si, 'T', hot_gas_temp_si, fluid)
        eta_s = (h_2s_si - h_1_si) / (h_2_si - h_1_si)
    else:
        # eta_s given, hot_gas_temp is None
        h_2_si = ((h_2s_si - h_1_si) / eta_s) + h_1_si
        hot_gas_temp_si = PropsSI('T', 'P', p_high_si, 'H', h_2_si, fluid)
        hot_gas_temp = hot_gas_temp_si - 273.15  # K to °C

    # cycle point 3
    t_3_0_si = PropsSI('T', 'P', p_high_si, 'Q', 0, fluid)
    if subcooling == 0:
        h_3_si = PropsSI('H', 'P', p_high_si, 'Q', 0, fluid)
    else:
        t_3_si = t_3_0_si - subcooling  # in K
        h_3_si = PropsSI('H', 'P', p_high_si, 'T', t_3_si, fluid)  # struggles if subcooling = 0 K

    # cycle point 4
    h_4_si = h_3_si

    # convert unity
    h_1 = h_1_si / 1000  # J/kg to kJ/kg (PropsSI to diagram)
    h_2 = h_2_si / 1000
    h_2s = h_2s_si / 1000
    h_3 = h_3_si / 1000
    h_4 = h_4_si / 1000
    t_1_0 = t_1_0_si - 273.15  # K to °C
    t_3_0 = t_3_0_si - 273.15  # K to °C

    # extra calculations for more data
    p_compressor = (h_2 - h_1) * massflow_si
    q_evaporation = (h_1 - h_4) * massflow_si
    q_condensing = (h_2 - h_3) * massflow_si
    eer = q_evaporation / p_compressor
    cop = eer + 1
    t_0 = t_1_0
    t_c = t_3_0
    delta_h_0 = h_1 - h_4
    delta_h_c = h_2 - h_3

    # generate plot data
    plot_data = {
        'isoline_data': {
            'isentropic_compression': {
                'isoline_property': 's',
                'isoline_value': s_1_si,
                'starting_point_property': 'h',  # or p?
                'starting_point_value': h_1,
                'ending_point_property': 'h',
                'ending_point_value': h_2s,
            },
            'condensing': {
                'isoline_property': 'p',
                'isoline_value': p_high,
                'starting_point_property': 'h',
                'starting_point_value': h_2,
                'ending_point_property': 'h',
                'ending_point_value': h_3
            },
            'decompression': {
                'isoline_property': 'h',
                'isoline_value': h_3,
                'starting_point_property': 'p',
                'starting_point_value': p_high,
                'ending_point_property': 'p',
                'ending_point_value': p_low
            },
            'evaporation': {
                'isoline_property': 'p',
                'isoline_value': p_low,
                'starting_point_property': 'h',
                'starting_point_value': h_4,
                'ending_point_property': 'h',
                'ending_point_value': h_1
            },
        },
        'x_y_data': {
            'real_compression': {
                'x_from': h_1,
                'x_to': h_2,
                'y_from': p_low,
                'y_to': p_high,
            },
        }
    }

    # generate more data to display
    more_data = {
        'eer': eer,
        'cop': cop,
        'p_compressor': p_compressor,
        'q_evaporation': q_evaporation,
        'q_condensing': q_condensing,
        't_0': t_0,
        't_c': t_c,
        'delta_h_0': delta_h_0,
        'delta_h_c': delta_h_c,
        'hot_gas_temp': hot_gas_temp,
        'eta_s': eta_s,
    }

    # return data for further processing
    return plot_data, more_data


def add_cycle_to_logph(ax, diagram, data):
    # loops through each plot_data item with isolines
    for name, specs in data['isoline_data'].items():
        # calculate data points for each data item
        datapoints = diagram.calc_individual_isoline(**specs)

        # add calculated datapoints in plot
        if name == 'isentropic_compression':
            ax.plot(datapoints['h'], datapoints['p'], label=name, color='red', linestyle='--')
        else:
            ax.plot(datapoints['h'], datapoints['p'], label=name, color='red')

    # loops through each plot_data item with (x, y) coordinates
    for name, specs in data['x_y_data'].items():
        ax.plot(
            [specs['x_from'], specs['x_to']],
            [specs['y_from'], specs['y_to']],
            label=name, color='red'
        )


def add_tpm_point_to_logph(ax, diagram, pressure):
    datapoints = diagram.calc_individual_isoline(**{
        'isoline_property': 'p',
        'isoline_value': pressure,
        'starting_point_property': 'Q',
        'starting_point_value': 0,
        'ending_point_property': 'Q',
        'ending_point_value': 1
    })

    # add calculated datapoints in plot
    ax.plot(datapoints['h'], datapoints['p'], color='red')


def precalculate_hg(p_high, p_low, superheat, fluid):
    # convert unity
    p_high_si = p_high * 1e5  # bar to Pa
    p_low_si = p_low * 1e5  # bar to Pa

    # cycle point 1
    t_1_0_si = PropsSI('T', 'P', p_low_si, 'Q', 1, fluid)
    t_1_si = t_1_0_si + superheat  # in K
    s_1_si = PropsSI('S', 'P', p_low_si, 'T', t_1_si, fluid)

    # cycle point 2
    s_2_isentropic = s_1_si
    t_2s_si = PropsSI('T', 'P', p_high_si, 'S', s_2_isentropic, fluid)
    t_2s = t_2s_si - 273.15  # K to °C

    return int(t_2s)
