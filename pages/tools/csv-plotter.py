import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit.runtime.uploaded_file_manager import UploadedFile

st.title("CSV Plotter")

st.markdown(
    """
    1. CSV-Datei (per Drag and Drop) hochladen und Tabelle anzeigen lassen
    2. Zum Plotten ggf. passende X-Achse wählen
    3. (Mehre) Spalten in der Tabelle links-klicken, um die Y-Achse zu besetzen
    """
)

st.divider()

uploaded_file = st.file_uploader("Datei wählen:", type="csv", accept_multiple_files=False)

# translates selectbox input to actual value
sep = {
    "Komma": ",",
    "Semikolon": ";",
    "Tabstopp": "\t",
}

decimal = {
    "Punkt": ".",
    "Komma": ",",
}

col1, col2 = st.columns(2)
with col1:
    sep_sel = st.selectbox(
        "Trennzeichen:",
        list(sep.keys()),
    )
with col2:
    decimal_sel = st.selectbox(
        "Dezimaltrennzeichen:",
        list(decimal.keys()),
    )

# continues if a file got uploaded into uploaded_file, excludes type None
if isinstance(uploaded_file, UploadedFile):

    dataframe = pd.read_csv(uploaded_file, sep=sep[sep_sel], decimal=decimal[decimal_sel], )

    # continues if dataframe is pd.DataFrame
    if isinstance(dataframe, pd.DataFrame):

        # shows dataframe as table
        event = st.dataframe(
            dataframe,
            key="data",
            on_select="rerun",
            selection_mode=["multi-row", "multi-column"],
        )

        # select colum for x-axis
        st.divider()
        x_column = st.selectbox(
            "Spalte auf der X-Achse:",
            dataframe.columns,
        )

        # plots dataframe if column selected
        if len(event.selection.columns) > 0:

            # creates fig object
            fig = go.Figure()

            # adds trace and data to fig
            for selected_col in event.selection.columns:
                fig.add_trace(
                    go.Scatter(
                        x=dataframe[x_column],
                        y=dataframe[selected_col],
                        name=selected_col
                    )
                )

            # shows plot in app
            st.plotly_chart(fig, config={'scrollZoom': False})
