import streamlit as st

# page config
st.set_page_config(
    page_title="IKETapp",
    page_icon="assets/iket.svg", )

# define pages
pages = {
    # "Your account": [
    #     st.Page("create_account.py", title="Create your account"),
    #     st.Page("manage_account.py", title="Manage your account"),
    # ],
    "Tools": [
        st.Page("pages/tools/fluid-cycle-calculator.py", title="Kältekreislauf-Rechner"),
        st.Page("pages/tools/csv-plotter.py", title="CSV Plotter"),
        st.Page("pages/tools/refrigerant-slider.py", title="Kältemittelschieber"),
    ],
    "Bibliothek": [
        st.Page("pages/libary/institutes.py", title="Institute"),
        st.Page("pages/libary/external-tools.py", title="Externe Tools"),
        st.Page("pages/libary/documents.py", title="Dokumente")
    ],
}

pg = st.navigation(pages)
pg.run()
