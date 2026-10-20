from CoolProp.CoolProp import PropsSI


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
    calc_data = {
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
    return plot_data, calc_data
