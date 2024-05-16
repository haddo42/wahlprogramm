import streamlit as st
import pandas as pd
import re

CONSTANTS = {
    "basic_text_file": "./data/worktext.txt",
    "info_text_file": "./data/information.md",
    "inhalt_text_file": "./data/gliederung.txt",
    "words_frequency_file": "./data/semwords.csv",
}

# =====================================================================
#          ----- Funktionen zum Laden der Datenbasis -----
#
# @st.cache_resource
def load_basic_text(file=CONSTANTS["basic_text_file"]) -> str:
    """ Lädt den Basistext für den Tab 'Basistext' """
    with open(file, "r", encoding="utf-8") as f:
        return f.read()  

# @st.cache_resource
def load_info_text(file=CONSTANTS["info_text_file"]):
    """ Lädt den Text für den Tab 'Info' """
    with open(file, 'r', encoding="utf-8") as f:
        return f.read()

# @st.cache_resource
def load_gliederung_text(file=CONSTANTS["inhalt_text_file"]):
    """ Lädt den Text für den Tab 'Gliederung' """
    with open(file, 'r', encoding="utf-8") as f:
        buls = f.read()
        return buls.split('\n')

# @st.cache_resource
def load_word_frequency(file=CONSTANTS["words_frequency_file"]):
    """ Lädt die Liste Wortfrequenzen """
    df_word_frequency = pd.read_csv(file,)
    return df_word_frequency


# =====================================================================
#          ----- show_words() -----
#
def show_words():
    min = 10
    df = load_word_frequency().query(f'Anzahl > {min}').sort_values("Anzahl", ascending=False)
    st.write(f"{len(df)} Wörter der Häufigkeit > {min}")
    st.dataframe(df, hide_index=True)


# =====================================================================
#          ----- pre_content() -----
#
def pre_content():
    text = """
        Der im Programm verwendete Text wurde dem Europawahlprogramm 2024 
        der Partei Bündnis 90/Die Grünen entnommen und stimmt mit diesem im Textteil 
        vollständig überein. Das originale Programm ist
        [hier](https://cms.gruene.de/uploads/assets/20240306_Reader_EU-Wahlprogramm2024_A4.pdf) zu finden.
        """
    return text

# =====================================================================
#          ----- show_content() -----
#
def show_content():
    """ Lädt das Inhaltsverzeichnis für den Tab 'Wahlprogramm' """
    buls = st.session_state["all_bullets"]
    html = "<table style='font-size:14px;'>"
    for bul in buls:
        first_space = bul.index(" ")
        html = html + "<tr>"
        html +=  "<td>" + bul[0:first_space] + "</td>"
        html += "<td>&nbsp;&nbsp;&nbsp;&nbsp;</td>"
        html += "<td>" + bul[first_space:]
        html += "</td></tr>"
        html += "</tr>"
    html += "</table>"
    return html

# =====================================================================
#          ----- df_beispiel_suche -----
#
df_examples = pd.DataFrame(
    {"Beispiele Suchvorgabe": [
        "EU",
        "Energie",
        "Europa braucht",
        "wollen",
        "soll", 
        "muss müss", 
        "darf nicht",
        "*in",
        "brauch",
        ],}
)

# =====================================================================
#          ----- build_pattern() -----
#
def build_pattern() -> str:
    """ Erzeugt aus den in 'words_wanted' gegebenen Suchworten
        einen regulären Ausdruck für die Suche im Text.
    """ 
    if len(st.session_state["words_wanted"]) == 0:
        return ""
    
    pattern = ""
    for w in st.session_state["words_wanted"]:
        w = w.replace('*', r'\*')  #  wegen der Genderworte Arbeitnehmer*innen u.a.
        w = r"\b" + w if st.session_state["word_start"] else w
        w = w + r"\b" if st.session_state["word_end"] else w
        pattern += w + '|'
    pattern = pattern.strip('|')
    pattern = f"(?i){pattern}" if st.session_state["case_insensitive"] else pattern

    # print(f"words_wanted: {st.session_state["words_wanted"]}")
    # print(f"pattern: {pattern}")
    
    return pattern

# =====================================================================
#          ----- get_record() -----
#
def get_record(word_start) -> str:
    """ Liefert den zu word_start gehörenden Satz aus basic_text
        word_start - die Startposition eines im basic_text gefundnene Worts
        basic_text - der Text, der der ganzen Analyse zu Grunde liegt 
    """
    basic_text = st.session_state["basic_text"]
    # Suche nach links, Suche in [basic_text, word_start][::-1], d.i. umgekehrte Reihenfolge
    match = re.search(r"[\.!?π]", basic_text[0:word_start][::-1])
    rec_begin = match.span()[0] if match else word_start
    
    # Suche nach rechts bis zum nächsten .!?π
    match = re.search(r"[\.!?π]", basic_text[word_start:])
    rec_end = match.span()[1] if match else word_start

    record = basic_text[word_start - rec_begin : word_start + rec_end]
    record = record.replace("\n\n", " ").replace("\n", " ").strip()

    return record

# =====================================================================
#          ----- get_page() -----
#
def get_page(word_start_pos) -> str:
    """ Ermittelt die Seite, auf der das Wort mit der Position
        word_start_pos im Text liegt.
    """
    basic_text = st.session_state["basic_text"]
    if word_start_pos > len(basic_text):
        return 0
    res = re.search(r"\n\d+\n", basic_text[word_start_pos:])
    if res:
        page = int(res.group().strip())
    return page

# =====================================================================
#          ----- get_bullet() -----
#
def get_bullet(word_start_pos) -> str:
    """ Ermittelt den Gliederungspunkt, innerhalb dessen das Wort
        mit der Positiom 'word_start_pos' im Text liegt.
        Im Text sind die Gliederungspunkte nur als Dummies vorhanden und durch
        Zeichenfolgen 'ππππππ...' dargestellt. Sie bewahren so die Struktur
        der Textgliederung und ermöglichen das Bestimmen der konkrete Texte 
        aus der Datei 'inhalt_text_file'.
    """
    basic_text = st.session_state["basic_text"]
    all_bullets = st.session_state["all_bullets"]
    if word_start_pos > len(basic_text):
        return ""

    # sucht alle pseudo gliederungspunkte vor der Startposition word_start_pos
    bullets_in_front_of_word = re.findall(r"\nπ+", basic_text[0 : word_start_pos])
        
    if bullets_in_front_of_word:
        # die Nummer des letzten gefundenen pseudo gliederungspunkts ist die des realen aus all_bullets
        bullet = all_bullets[len(bullets_in_front_of_word) - 1]
    else:
        # Position word_start_pos liegt vor der ersten gliederungsposition
        bullet = ""

    return bullet

# =====================================================================
#          ----- search_it() -----
#
def search_it(pattern: str) -> list:
    """ Sucht das Muster im Text. Gibt die Position eines Fundes,
        das Suchmuster, den zugehörigen Satz, die Seite und den Gliederungspunkt
        pro Fund zurück. Die zurückgegebene Datenstruktur ist:
        [ [postion, [words_wanted], record, page_nr, bullet],... ]
    """
    if len(pattern) == 0:
        return []
    
    found = re.finditer(
    pattern,
    st.session_state["basic_text"],
    )
    list_found = list (found)
    # print({f"Gefunden: {len(list_found)}"})
    
    words_wanted = st.session_state["words_wanted"]
    st.session_state["words_found"] = len(list_found)
    result = []
    last_record = ""
    for item in list_found:
        pos = item.span()[0]
        record = get_record(pos)
        rec_list = [
            pos,  # position
            words_wanted,  # words_wanted
            record,  # record
            get_page(pos),  # page_nr
            get_bullet(pos),  # bullet
        ]
        if record != last_record:
            last_record = record
            result.append(rec_list)
    
    if st.session_state["words_together"]:
        result = select_words_together(result)
    
    return result

# =====================================================================
#          ----- select_words_together() -----
#
def select_words_together(result: list) -> list:
    """ Erhält das Resultat einer Suche
        Struktur: [ [postion, [words_wanted], record, page_nr, bullet],... ]
        Selektiert daraus die Einträge, die alle Wörter
        aus words_wanted enthalten.
    """
    words_wanted = st.session_state["words_wanted"]
    new_result = []
    words_wanted_pattern = []
    for w in words_wanted:
        w = w.replace('*', r'\*')
        w = r"\b" + w if st.session_state["word_start"] else w
        w = w + r"\b" if st.session_state["word_end"] else w
        words_wanted_pattern.append(w)
    
    for item in result:
        item_ok = True
        for w in words_wanted_pattern:
            # print(w)
            if not re.search(w, item[2]):
                item_ok = False
                break
        # for w in words_wanted:
        #     if w not in item[2]:
        #         item_ok = False
        #         break
        if item_ok:
            new_result.append(item)
    
    return new_result


# =====================================================================
#          ----- show_result() -----
#
def show_result(search_result) -> str:
    """ Erhält als Argument das search_result
        Struktur: [ [postion, [words_wanted], record, page_nr, bullet],... ]
        Gitb eine HTML-Struktur über alle Elemente des Arguments zurück.
        Benutzt die Funktion mark_words
    """
    text = ""
    for record in search_result:
        text += f"<span style='font-size:12px;font-family:courier;'>Seite {record[3]}</span>"
        if len(record[4]) > 0:
            text += f"<span style='font-size:12px;font-family:courier;'>, Abschnitt \"{record[4]}\"</span>"
        text += "<br>" + mark_words(record)
        text += "<br><br>"

    text = "<div style='font-size:16px';font-family:arial;>" + text + "</div>" 
    return text

def mark_words(record):
    """ Erhält jeweils einen kompletten Satz aus search_result zur Markierung 
        [ [postion, [words_wanted], record, page_nr, bullet],... ]
        Markiert die words_wanted, die im record enthalten sind 
        Gibt nur den markierten record zurück  
    """
    words_wanted = record[1]
    rec_to_marked = record[2]
    
    for word in words_wanted:
        word = word.replace('*', r'\*')
        # pattern = r"\b" + word if st.session_state["word_start"] else r"(\b[a-zA-Z\*äÄöÖüÜß]*?)" + word
        # pattern = pattern +  r"\b" if st.session_state["word_end"] else pattern + r"[a-zA-Z\*äÄöÖüÜß]*?\b"
        pattern = word
        match = re.finditer(pattern, rec_to_marked)
        for item in match:
            marked_found = f'<span style="color:#de7802;"><b><u>{item.group()}</u></b></span>'
            rec_to_marked = re.sub(pattern, marked_found, rec_to_marked)

    return rec_to_marked


# =====================================================================
#          ----- get_result() -----
#
def get_result():
    """ Erzeugt mit Hilfe der Funktionen 'build_pattern()' und 'search_it()'
        das Resultat der Suche und legt es in st.session_state["search_result"] ab.
        Die Struktur des Resultats ist:
        [ [postion, pattern, record, page_nr, bullet],... ]
    """
    st.session_state["msg_result"] = ""
    st.session_state["show_result"] = ""
    st.session_state["pre_show_result"] = ""
    st.session_state["search_result"] = []
    st.session_state["words_wanted"] = []

    if len(st.session_state["search_words_input"]) == 0:
        st.toast("###### Suchvorgabe fehlt. :worried:")
        return
        

    # Prüfen der Argumente aus dem Eingabefeld st.text_input key='search_words_input'
    # Es wird ein Wort oder eine Folge von Wörtern eerwartet, die durch Leerzeichen
    # getrennt sind.
    # Die minimal erlaubte Länge eines Wortes beträgt 2 Zeichen.
    word_list = st.session_state["search_words_input"].split(" ")
    wanted = []
    for word in word_list:
        word = word.strip(" .,:;!?")
        match = re.search(r"^[a-zA-Z\*äÄöÖüÜß-]{2,}$", word)
        if match:
            wanted.append(match[0])
    
    st.session_state["words_wanted"] = wanted
    # print(wanted)

    # create search pattern
    pattern = build_pattern()
    # print(f"{'-'*20}\nwanted: {wanted}\npattern: {pattern}")

    # searching
    result = search_it(pattern)
    st.session_state["search_result"] = result
    
    if len(result) > 0:
        # print(
        #     f"result: {result[0]} \ncase_insensitive: {st.session_state["case_insensitive"]}")
        words_found = st.session_state["words_found"] 
        rec_clause = "Sätze" if len(result) > 1 else "Satz"
        st.session_state["msg_result"] = f"{words_found} Wörter, {len(result)} {rec_clause} gefunden."
        st.session_state["show_result"] = show_result(st.session_state["search_result"])
    
    else:
        st.session_state["msg_result"] = "Kein Fund."
        st.toast("###### Kein Fund. :-1:")
    return

