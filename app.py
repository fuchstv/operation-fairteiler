import streamlit as st
import random
import time

# --- Setup & Initialization ---
st.set_page_config(page_title="Operation: Fairteiler", page_icon="🍌")

# Initialize requested state variables
if 'hp' not in st.session_state:
    st.session_state['hp'] = 100

if 'inventory' not in st.session_state:
    st.session_state['inventory'] = []

if 'stage' not in st.session_state:
    st.session_state['stage'] = 'intro'

if 'warnings' not in st.session_state:
    st.session_state['warnings'] = 0

# Initialize other necessary state variables
if 'player_class' not in st.session_state:
    st.session_state['player_class'] = None

if 'log' not in st.session_state:
    st.session_state['log'] = ["Spiel gestartet."]

if 'turn' not in st.session_state:
    st.session_state['turn'] = 0

def add_log(message):
    st.session_state['log'].append(message)

def check_game_over():
    if st.session_state['warnings'] >= 3:
        st.session_state['stage'] = 'game_over'
        return True
    return False

# --- Scenes ---

def scene_intro():
    st.title("🍌 Operation: Fairteiler")
    st.markdown("*Die Bürokratie des Rettens*")
    st.write("Willkommen in der Welt der Lebensmittelrettung. Dein Ziel: Werde Orga-Bot.")

    if st.button("Spiel starten"):
        st.session_state['stage'] = 'character_creation'
        st.rerun()

def scene_character_creation():
    st.header("Wähle deine Klasse")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Lastenrad-Rambo")
        st.write("Tragekapazität: Hoch")
        st.write("Hygiene: Fragwürdig")
        if st.button("Wähle Rambo"):
            st.session_state['player_class'] = "Lastenrad-Rambo"
            st.session_state['inventory'] = ["Verschwitztes T-Shirt"]
            add_log("Klasse gewählt: Lastenrad-Rambo")
            st.session_state['stage'] = 'hub'
            st.rerun()

    with col2:
        st.subheader("Paragraphen-Reiter")
        st.write("Tragekapazität: Niedrig")
        st.write("Spezialität: Rechtsvereinbarung zitieren")
        if st.button("Wähle Reiter"):
            st.session_state['player_class'] = "Paragraphen-Reiter"
            st.session_state['inventory'] = ["Laminiergerät"]
            add_log("Klasse gewählt: Paragraphen-Reiter")
            st.session_state['stage'] = 'hub'
            st.rerun()

def scene_hub():
    st.header("Der Verteiler-Hub")
    st.write(f"Du bist ein {st.session_state['player_class']}.")

    # Status Display
    st.sidebar.title("Status")
    st.sidebar.write(f"Klasse: {st.session_state['player_class']}")
    st.sidebar.write(f"Magen-Resistenz (HP): {st.session_state['hp']}")
    st.sidebar.write(f"Gelbe Karten: {st.session_state['warnings']}/3")
    st.sidebar.write("Inventar:")
    for item in st.session_state['inventory']:
        st.sidebar.write(f"- {item}")

    st.subheader("Was willst du tun?")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Zur Bäckerei"):
            st.session_state['stage'] = 'bakery'
            st.rerun()

    with col2:
        if st.button("Zum Fairteiler"):
            st.session_state['stage'] = 'fairteiler'
            st.rerun()

    with col3:
        if st.button("Quiz machen"):
            st.session_state['stage'] = 'quiz'
            st.rerun()

    # Log Display
    st.divider()
    st.subheader("Logbuch")
    for msg in reversed(st.session_state['log'][-5:]):
        st.caption(msg)

def scene_bakery():
    st.header("Die Bäckerei 'Krumme Kruste'")
    st.write("Der Geruch von altem Brot liegt in der Luft.")

    if st.button("Rettung durchführen"):
        items = ["Sack Brötchen", "Vollkornbrot (Hart)", "Unbekanntes Teilchen"]
        found = random.choice(items)
        st.session_state['inventory'].append(found)
        add_log(f"Gefunden: {found}")
        st.success(f"Du hast {found} gerettet!")

    if st.button("Zurück zum Hub"):
        st.session_state['stage'] = 'hub'
        st.rerun()

def scene_fairteiler():
    st.header("Der Fairteiler")
    st.write("Ein Schrank an der Straßenecke. Jemand hat Müll daneben gestellt.")

    if st.button("Aufräumen"):
        if random.random() > 0.7:
            st.session_state['warnings'] += 1
            add_log("Oha! Du hast den Müll falsch getrennt. Gelbe Karte!")
            st.error("Jemand vom Orga-Team hat dich gesehen. Gelbe Karte!")
            if check_game_over():
                st.rerun()
        else:
            add_log("Fairteiler aufgeräumt. Karma +1.")
            st.success("Du hast den Fairteiler sauber gemacht. Vorbildlich!")

    if st.button("Alles ablegen"):
        count = len(st.session_state['inventory'])
        if count > 0:
            st.session_state['inventory'] = []
            add_log(f"{count} Items in den Fairteiler gelegt.")
            st.success("Rucksack ist jetzt leer.")
        else:
            st.warning("Dein Rucksack ist schon leer.")

    if st.button("Zurück zum Hub"):
        st.session_state['stage'] = 'hub'
        st.rerun()

def scene_quiz():
    st.header("Das Foodsaver-Quiz")
    st.write("Frage: Darf man Hackfleisch retten?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ja, klar!"):
            st.session_state['warnings'] += 1
            add_log("Falsch! Hackfleisch ist verboten. Gelbe Karte!")
            st.error("Falsch! Hackfleisch ist verboten.")
            if check_game_over():
                st.rerun()
    with col2:
        if st.button("Nein, niemals!"):
            add_log("Richtig! Hygiene-Regeln beachtet.")
            st.success("Korrekt! Du kennst die Regeln.")

    if st.button("Zurück"):
        st.session_state['stage'] = 'hub'
        st.rerun()

def scene_game_over():
    st.title("🚫 GAME OVER 🚫")
    st.write("Du hast 3 Gelbe Karten gesammelt.")
    st.write("Der Bezirksverantwortliche hat dich aus der Gruppe entfernt.")

    if st.button("Neues Spiel"):
        st.session_state.clear()
        st.rerun()

# --- Main Logic ---

pages = {
    'intro': scene_intro,
    'character_creation': scene_character_creation,
    'hub': scene_hub,
    'bakery': scene_bakery,
    'fairteiler': scene_fairteiler,
    'quiz': scene_quiz,
    'game_over': scene_game_over
}

current_stage = st.session_state['stage']
if current_stage in pages:
    pages[current_stage]()
else:
    st.error(f"Seite '{current_stage}' nicht gefunden.")
