import streamlit as st

st.title('Institute')

st.divider()

with st.container():
    st.image('assets/iket.png')
    st.markdown(
        '''
        ### Institut für Kälte- Klima- und Energietechnik GmbH        
        - Sicherheitstechnische Planungsprüfung gemäß kältetechnischem Regelwerk
        - Prüfungen gemäß:
            - § 29a Bundesimmissions­schutzgesetz (BImSchG)
            - § 15 und 16 Betriebssicherheitsverordnung (BetrSichV)
            - Wasserhaushaltsgesetz und § 46 Verordnung über Anlagen zum Umgang mit wassergefährdenden Stoffen (WHG und AwSV)
            - Bundesimmissions­schutzverordnung (42. BImSchV)
        - Gerichtsgutachten
        '''
    )
    st.link_button('Zum IKET', 'https://iket.de')

st.divider()

with st.container():
    st.image('assets/inekk.png')
    st.markdown(
        '''
        ### Institut für Energie, Kälte- und Klimatechnik GmbH
        - Gefährdungsbeurteilungen gemäß:
            - BetrSichV
            - 42. BImSchV
        - Betriebstagebücher für Verdunstungskühlanlagen
        - Explosionsschutzdokumente
        - Betriebliche Alarm- und Gefahrenabwehrpläne
        - Allgemeine Überprüfung von Kälteanlagen
        '''
    )
    st.link_button('Zum InEKK', 'https://inekk.de')
