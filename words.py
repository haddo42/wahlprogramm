import streamlit as st
import helper as hlp

st.set_page_config(
    page_title="Worte zur Wahl",
    layout="wide",
)

# ===================================================================== #
#          ----- Session State -----
# ===================================================================== #
if "basic_text" not in st.session_state:
    st.session_state["basic_text"] = hlp.load_basic_text()
    st.session_state["all_bullets"] = hlp.load_gliederung_text()
    st.session_state["info_text"] = hlp.load_info_text()
    st.session_state["word_frequency"] = hlp.load_word_frequency()
        
    st.session_state["search_words_input"] = ""
    st.session_state["words_wanted"] = []
    st.session_state["words_found"] = 0
    st.session_state["search_result"] = []
    st.session_state["msg_result"] = ""
    st.session_state["show_result"] = ""
    st.session_state["pre_show_result"] = ""
        
    st.session_state["word_start"] = False
    st.session_state["word_end"] = False
    st.session_state["case_insensitive"] = False
    st.session_state["words_together"] = True
    

# ===================================================================== #
#          ----- User Interface -----
# ===================================================================== #
st.write("Wortsuche im Wahlprogramm :green[Bündnis 90/Die Grünen]")
tab1, tab2, tab3, tab4 = st.tabs(["Suche", "Ergebnis", "Wahlprogramm", "Programminfo"])


# Tab 1: Sucheingaben
with tab1:
    with st.container(height=340, border=False):
        col1, col2 = st.columns([12, 5])
        with col1:
            with st.form("form_search", clear_on_submit=False):
                st.text_input(
                    "Suchvorgabe",
                    key="search_words_input",
                    help="Ein oder mehrere Worte oder Wortteile.",
                )
                
                form_cols = st.columns([4,5])
                with form_cols[0]:
                    st.checkbox(
                        "Wortanfang",
                        key="word_start",
                        help="Suchvorgabe wird nur an den Wortanfängen erkannt.",
                    )
                    st.checkbox(
                        "Kleinschreibung",
                        key="case_insensitive",
                        help="Die Großschreibung der Worte im Text wird `nicht` beachtet.",
                    )
                with form_cols[1]:
                    st.checkbox(
                        "Wortende",
                        key="word_end",
                        help="Suchvorgabe wird an den Wortenden erkannt.",
                    )
                    st.checkbox(
                        "Worte zusammen",
                        key="words_together",
                        help="Alle Suchwörter müssen in einem Satz vorkommen.",
                    )
                
                st.form_submit_button(
                    label="Suche starten",
                    type="primary",
                    on_click=hlp.get_result,
                )
                st.text_input("Anzahl Funde:", key="msg_result", disabled=True)

        with col2:
            # st.table(hlp.df_beispiel_suche,)
            st.dataframe(hlp.df_examples,
                hide_index=True,
                height=320,)
            
    # Vorschau in tab1, unterhalb von col1, col2
    preview = st.container(border=True)
    with preview:
        preview.html("<div style='font-size:14px;';>Vorschau Suchergebnis (maximal 10 Funde):</div>")
        if len(st.session_state["search_result"]) > 0:
            preview.html(hlp.show_result(st.session_state["search_result"][:10]))

    
# Tab 2: Suchergebnis
with tab2:
    if st.session_state["search_result"]:
        st.html(hlp.show_result(st.session_state["search_result"]))
    else:
        st.write("Keine Suchergebnisse")


# Tab 3: Wahlprogramm
with tab3:
    st.markdown(hlp.pre_content())
    tab3_left, tab3_right = st.columns(2)
    
    with tab3_left:
        with st.container(border=True):
            t = "Die hier verwendete Nummerierung der Gliederung ist "
            t += "gegenüber dem Original aus technischen Gründen "
            t += "leicht modifiziert und erweitert."
            st.markdown(t)

            @st.experimental_dialog("Inhaltsverzeichnis")
            def content_list():
                st.html(hlp.show_content())
            if st.button("Anzeige Inhaltsverzeichnis"):
                content_list()

    with tab3_right:
        with st.container(border=True):
            t = "Eine Häufigkeitsanalyse der im Textteil des Wahlprogramms gefundnene Wörter "
            t += "ist als Tabelle abrufbar."
            st.markdown(t)

            @st.experimental_dialog("Häufigkeit der Worte")
            def content_words():
                hlp.show_words()
            if st.button("Anzeige der Worthäufigkeiten"):
                content_words()
    

# Tab 4: Programminfo
with tab4:
    st.markdown(st.session_state["info_text"])
    
