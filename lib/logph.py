from fluprodia import FluidPropertyDiagram
import matplotlib.pyplot as plt
import numpy as np
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
