import streamlit as st

###########################
# UI
###########################
st.title('Dokumente')

with st.expander('Anträge Zertifizierung ChemKlimaschutzV'):
    with st.container(horizontal=True, vertical_alignment='center'):
        st.link_button('Antrag NRW ',
                       'https://www.arbeitsschutz.nrw.de/system/files/media/document/file/56-4_chemikaliensicherheit_antragsformular_6_chemklimaschutzv-4_0.pdf')
        st.link_button('Antrag Hessen ',
                       'https://rp-darmstadt.hessen.de/sites/rp-darmstadt.hessen.de/files/2026-04/antrag_betriebszertifizierung.pdf')
        st.link_button('Antrag Bayern',
                       'https://www.lfu.bayern.de/analytik_stoffe/verordnungen/chemklimaschutzv/doc/antragsformular_betriebszertifizierung_15_05_26_nbf.pdf')
        st.link_button('Antrag Bayern digital',
                       'https://formularserver-bp.bayern.de/intelliform/forms/bayernportal/bayernportal/Ministerien/stmuv/lfu_uzert_chemklimsv/index?caller=bpmntdaodbgmztqztcgntdgobrgupu6jikehdfr5oe4mefzoefe6tuuk3ylngkliroohgthymdp6b3s7hpbumraaoz4zfpkauoezomh7nxfshayrfkylwu7fahgdfruheanimb6orphu4nxqulmblwtordcor4b2f2tmdgrqacn4bdt7rdpxkb2brvklivfda5bju4ht5pap734888')
        st.write('More coming soon ...')
