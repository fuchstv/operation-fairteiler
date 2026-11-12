"""A small, source-backed Foodsaver adventure. Run with streamlit run app.py."""
import io
import math
import struct
import wave
from html import escape

import streamlit as st

WIKI = 'https://wiki.foodsharing.network/wiki/'
SOURCES = {
    'Foodsaver': WIKI + 'Foodsaver',
    'Einführungsabholungen': WIKI + 'Einf%C3%BChrungsabholungen',
    'Hygieneregeln': WIKI + 'Hygieneregeln',
    'Verhaltensregeln': WIKI + 'Verhaltensregeln',
    'Fairteilung': WIKI + 'Fairteilung',
    'Botschafter*innen': WIKI + 'Botschafter*in',
    'Betriebsverantwortliche': WIKI + 'Betriebsverantwortliche*r',
    'Fairteiler': WIKI + 'Fairteiler_und_Abgabestellen',
}
# These are original practice questions, not the official qualification quiz.
QUIZ = [
    ('Deine erste Zusage', 'Du stehst für morgen im Abholplan. Jetzt kommt etwas dazwischen. Was tust du?',
     ['Einfach nicht erscheinen.', 'Rechtzeitig austragen und gegebenenfalls Ersatz suchen.'], 1,
     'Abholungen brauchen Verlässlichkeit. Eine Zusage gilt, solange du dich nicht rechtzeitig ausgetragen und gegebenenfalls Ersatz gesucht hast.', 'Foodsaver'),
    ('Was darf in den Schrank?', 'Du hast Hackfleisch gerettet. Darfst du es zur nicht-persönlichen Weitergabe in einen Fairteiler legen?',
     ['Nein, Hackfleisch ist für diese Weitergabe ausgeschlossen.', 'Ja, jedes gerettete Lebensmittel darf hinein.'], 0,
     'Retten und Weitergeben sind verschiedene Dinge: Bei nicht-persönlicher Weitergabe ist Hackfleisch ausdrücklich ausgeschlossen.', 'Hygieneregeln'),
    ('Das Datum auf der Packung', 'Das Verbrauchsdatum ist überschritten. Darfst du das Lebensmittel weitergeben?',
     ['Ja, wenn die Verpackung gut aussieht.', 'Nein, nach dem Verbrauchsdatum nicht weitergeben.'], 1,
     'Lebensmittel nach dem Verbrauchsdatum dürfen nicht weitergegeben werden. Verbrauchsdatum und Mindesthaltbarkeitsdatum sind nicht dasselbe.', 'Hygieneregeln'),
]
PICKUPS = [
    {'title': 'Die Bäckerei erwacht', 'place': 'Krumme Kruste · 18:00 Uhr', 'icon': '🚲',
     'story': 'Deine Begleiterin Sam wartet vor der Bäckerei. Hinter der Scheibe stapeln sich Brote. „Wir retten gemeinsam. Hast du die Absprachen gelesen und passende Behälter dabei?“',
     'question': 'Wie bereitest du die Abholung vor?',
     'options': ['Absprachen lesen, pünktlich sein und saubere Lebensmittelbehälter mitnehmen.', 'Mit irgendeinem alten Müllsack losfahren.'],
     'correct': 0, 'why': 'Unverpackte Lebensmittel gehören in saubere, lebensmittelechte Verpackungen. Pünktlichkeit und die Absprachen mit dem Betrieb zählen ebenfalls.',
     'source': 'Hygieneregeln', 'loot': ['2 Vollkornbrote', '6 Brötchen'],
     'result': 'Ihr verpackt die Backwaren sorgfältig. Sam nickt: „So kommen die Brote gut an.“'},
    {'title': 'Sortieren statt wegsehen', 'place': 'Gemüseladen · 17:30 Uhr', 'icon': '🥕',
     'story': 'Zwischen knackigen Karotten liegt eine schimmelige Frucht. Sam schiebt dir eine leere Kiste zu. „Wir übernehmen Verantwortung für alles, was wir weitergeben.“',
     'question': 'Was kommt in deine Kiste zur Weitergabe?',
     'options': ['Alles zusammen. Gerettet ist gerettet.', 'Jedes Stück prüfen und schimmelige Lebensmittel aussortieren.'],
     'correct': 1, 'why': 'Vor der Weitergabe ist jedes einzelne Stück auf Genießbarkeit zu prüfen. Lebensmittel mit Schimmel dürfen nicht weitergegeben werden.',
     'source': 'Hygieneregeln', 'loot': ['1 Kiste geprüfte Karotten'],
     'result': 'Die geprüften Karotten landen getrennt in der sauberen Kiste. Die schimmelige Frucht wird nicht weitergegeben.'},
    {'title': 'Der kühle Kopf', 'place': 'Nachbarschaftsmarkt · 19:00 Uhr', 'icon': '🧊',
     'story': 'Bei der dritten begleiteten Tour gibt es gekühlte Ware. Du hast keine Kühltasche dabei. Sam fragt: „Wie organisieren wir den Transport?“',
     'question': 'Wie geht ihr mit der Kühlware um?',
     'options': ['Erst einen geeigneten gekühlten Transport organisieren.', 'Im warmen Rucksack mitnehmen und später entscheiden.'],
     'correct': 0, 'why': 'Für Kühlwaren sieht das Wiki den Transport in einer Kühltasche oder Kühlbox mit Kühlelementen vor. Kühlware mit unterbrochener Kühlkette ist für nicht-persönliche Weitergabe ausgeschlossen.',
     'source': 'Hygieneregeln', 'loot': ['Gekühlte Ware zur direkten Übergabe'],
     'result': 'Ein Teammitglied bringt eine Kühlbox. Ihr organisiert eine direkte Übergabe; diese Ware kommt im Spiel nicht in den ungekühlten Fairteiler.'},
]


def new_game():
    return dict(stage='intro', name='Alex', route='Lastenrad', quiz=0, pickup=0,
                inventory=[], log=['Ein neuer Weg beginnt.'], feedback=None,
                answered=False, mistakes=0, shared=0, sound=False, motion=True)


def go(stage):
    g['stage'] = stage
    g['feedback'] = None
    g['answered'] = False


def answer(index, correct, why, source):
    if g['answered']:
        return
    if index == correct:
        g['answered'] = True
        if g['stage'] == 'pickup':
            g['inventory'] = PICKUPS[g['pickup']]['loot'].copy()
        g['feedback'] = ('success', 'Gut entschieden. ' + why, source)
    else:
        g['mistakes'] += 1
        g['feedback'] = ('warning', 'Noch einmal überlegen. ' + why, source)


@st.cache_data
def chime():
    out = io.BytesIO()
    with wave.open(out, 'wb') as wav:
        wav.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
        samples = []
        for freq in (523.25, 659.25, 783.99):
            for i in range(2205):
                envelope = math.sin(math.pi * i / 2205) ** 2
                samples.append(struct.pack('<h', int(6500 * envelope * math.sin(2 * math.pi * freq * i / 22050))))
        wav.writeframes(b''.join(samples))
    return out.getvalue()


def feedback():
    if g['feedback']:
        kind, text, source = g['feedback']
        getattr(st, kind)(text)
        st.caption(f'Nachlesen: [{source}]({SOURCES[source]})')
        if kind == 'success' and g['sound']:
            st.audio(chime(), format='audio/wav', autoplay=True)


def choices(options, correct, why, source):
    for i, label in enumerate(options):
        st.button(label, key=f'choice_{i}', on_click=answer,
                  args=(i, correct, why, source), disabled=g['answered'], use_container_width=True)
    feedback()


def scene(icon, location, motion_enabled=None):
    enabled = g['motion'] if motion_enabled is None else motion_enabled
    motion = ' moving' if enabled else ''
    st.markdown(f'<div class="scene"><span class="scene-icon{motion}">{icon}</span>'
                f'<div class="scene-place">{escape(location)}</div><div class="scene-road"></div></div>', unsafe_allow_html=True)


st.set_page_config(page_title='Operation: Fairteiler', page_icon='🥕', layout='wide')
if 'adventure' not in st.session_state:
    st.session_state.adventure = new_game()
g = st.session_state.adventure
st.markdown('''<style>
:root {color-scheme: light;}
.stApp {background:#f5f6ed;color:#382b20;}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stSidebar"] {background:#e9eddf;color:#382b20;}
h1,h2,h3 {color:#533a20!important;letter-spacing:-.025em;}
.stButton>button {border-radius:6px;border:1px solid #bbc6aa;background:#fff;color:#382b20;min-height:3rem;text-align:left;}
.stButton>button:hover {border-color:#426e18;color:#315514;background:#edf5e5;}
.stButton>button:focus-visible {outline:3px solid #533a20;outline-offset:3px;}
.stButton>button[kind="primary"] {background:#426e18;color:white;border-color:#426e18;}
[data-testid="stVerticalBlockBorderWrapper"]>div {border-radius:12px;}
.eyebrow {font-size:.75rem;letter-spacing:.18em;text-transform:uppercase;color:#5c6b47;font-weight:700;}
.scene {background:linear-gradient(180deg,#e3edd7,#f5eedb);border-radius:12px;height:170px;position:relative;overflow:hidden;margin:1rem 0 1.5rem;display:flex;align-items:center;justify-content:center;gap:24px;}
.scene-icon {font-size:4rem;display:inline-block;z-index:1;}
.scene-place {font-size:1rem;color:#533a20;font-weight:600;z-index:1;}
.scene-road {position:absolute;bottom:25px;width:100%;border-top:2px dashed #b7bd9e;}
.moving {animation:arrive 1.2s ease-out both;}
@keyframes arrive {from {transform:translateX(-70px);opacity:0;}to {transform:translateX(0);opacity:1;}}
@media(prefers-reduced-motion:reduce){.moving{animation:none;}}
@media(max-width:640px){.scene{height:140px;gap:12px;}.scene-icon{font-size:3rem;}.scene-place{font-size:.9rem;}}
</style>''', unsafe_allow_html=True)

mode = st.sidebar.selectbox('Spielmodus', ['Roguelike', 'Lernabenteuer'], key='game_mode')
if mode == 'Roguelike':
    from rogue_ui import render
    render(lambda icon, location: scene(icon, location, st.session_state.get('rogue_motion', True)), chime)
    st.stop()

with st.sidebar:
    st.markdown('### 🥕 Dein Rettungsrucksack')
    st.write(f"**{g['name']}** · {g['route']}")
    progress = {'intro': 0, 'quiz': 1, 'agreement': 2, 'pickup': 3 + g['pickup'], 'verification': 6, 'finish': 7}
    st.progress(progress[g['stage']] / 7, text='Dein Weg zum Foodsaver')
    st.caption(f"Begleitete Abholungen: {g['pickup']}/3")
    st.divider()
    st.markdown('**Inventar**')
    if g['inventory']:
        for item in g['inventory']:
            st.write('• ' + item)
    else:
        st.caption('Noch Platz für gerettete Lebensmittel.')
    st.divider()
    st.toggle('Sounds einschalten', value=g['sound'], key='sound_setting', on_change=lambda: g.update(sound=st.session_state.sound_setting))
    st.toggle('Animationen', value=g['motion'], key='motion_setting', on_change=lambda: g.update(motion=st.session_state.motion_setting))
    if g['sound']:
        st.caption('Kurzer Erfolgston; die Wiedergabe kann vom Browser blockiert werden. Hier kannst du ihn auch selbst starten.')
        st.audio(chime(), format='audio/wav')
    with st.expander('Tagebuch', expanded=False):
        for entry in g['log']:
            st.write(entry)
    with st.expander('Regelquellen'):
        for label, url in SOURCES.items():
            st.markdown(f'[{label}]({url})')
        st.caption('Wiki geprüft am 12.11.2026. Szenen und Dialoge sind erfunden; Regeln sind zusammengefasst.')
    if st.button('Spiel zurücksetzen'):
        st.session_state.adventure = new_game()
        for key in ('sound_setting', 'motion_setting', 'player_name', 'travel', 'agreement_check'):
            st.session_state.pop(key, None)
        st.rerun()

st.markdown('<div class="eyebrow">Ein kleines Abenteuer gegen Lebensmittelverschwendung</div>', unsafe_allow_html=True)
st.title('Operation: Fairteiler')
st.caption('Ein inoffizielles Text-RPG · Entscheidungen statt Lebensmittelverschwendung')
left, right = st.columns([3, 1], gap='large')
with right:
    st.markdown('#### Dein nächster Schritt')
    missions = {'intro': 'Komm in der Nachbarschaft an.', 'quiz': 'Lerne die Grundlagen und beantworte drei Übungsfragen.',
                'agreement': 'Verstehe die Verantwortung beim Retten.', 'pickup': 'Erlebe drei begleitete Abholungen und teile die Lebensmittel.',
                'verification': 'Schließe deinen Lernweg ab.', 'finish': 'Geschafft. Die Nachbarschaft isst mit!'}
    st.write(missions[g['stage']])
    st.info('Das Spiel ersetzt weder das offizielle Quiz noch Einführungsabholungen oder eine echte Verifizierung.')
with left:
    with st.container(border=True):
        if g['stage'] == 'intro':
            st.subheader('01 · Ein Rucksack voller Möglichkeiten')
            scene('🚲', 'Deine Nachbarschaft · kurz vor Ladenschluss')
            st.write('Auf dem Heimweg siehst du eine Kiste Brot hinter der Bäckereitheke. „Zu gut für die Tonne“, sagt Sam aus dem lokalen foodsharing-Team. „Willst du lernen, wie wir gemeinsam Lebensmittel retten?“')
            name = st.text_input('Wie sollen wir dich nennen?', value=g['name'], max_chars=30, key='player_name')
            route = st.radio('Wie bist du unterwegs?', ['Lastenrad', 'Zu Fuß'], horizontal=True, key='travel')
            st.caption('Beide Wege führen durch dieselbe Geschichte. Hier geht es um Zusammenarbeit, nicht um die größte Ladung.')
            if st.button('Mein Abenteuer beginnen', type='primary'):
                g.update(name=name.strip() or 'Alex', route=route)
                g['log'].append(f"{g['name']} lernt das Team kennen.")
                go('quiz')
                st.rerun()
        elif g['stage'] == 'quiz':
            n = g['quiz']
            title, question, options, correct, why, source = QUIZ[n]
            st.subheader(f'02 · Lernstation {n + 1}/3: {title}')
            scene('📖', 'Mit Sam am Küchentisch')
            st.write(question)
            choices(options, correct, why, source)
            if g['answered'] and st.button('Weiter', type='primary'):
                g['quiz'] += 1
                g['log'].append(f'Lernstation {n + 1} verstanden.')
                go('agreement' if g['quiz'] == len(QUIZ) else 'quiz')
                st.rerun()
        elif g['stage'] == 'agreement':
            st.subheader('03 · Retten heißt Verantwortung übernehmen')
            scene('🤝', 'Vom Wissen zur Praxis')
            st.write('Im echten Werdegang folgt nach dem bestandenen Quiz die Rechtsvereinbarung. Anschließend lernst du bei mindestens drei begleiteten Einführungsabholungen die Praxis kennen.')
            st.markdown(f"Grundlage: [Werdegang eines Foodsavers]({SOURCES['Foodsaver']})")
            st.write('Hier bestätigst du nur, dass du diesen Spielhinweis gelesen hast. Du schließt keine Rechtsvereinbarung ab und musst keine persönlichen Daten eingeben.')
            understood = st.checkbox('Verstanden: Dies ist eine Simulation.', key='agreement_check')
            if st.button('Zur ersten Einführungsabholung', type='primary', disabled=not understood):
                go('pickup')
                st.rerun()
        elif g['stage'] == 'pickup':
            p = PICKUPS[g['pickup']]
            st.subheader(f"04 · Einführungsabholung {g['pickup'] + 1}/3")
            st.markdown(f"### {p['title']}")
            scene(p['icon'], p['place'])
            st.write(p['story'])
            st.markdown('**' + p['question'] + '**')
            choices(p['options'], p['correct'], p['why'], p['source'])
            if g['answered']:
                st.success(p['result'])
                if g['pickup'] < 2:
                    st.write('Die geprüften Backwaren bzw. Karotten bringst du zum Fairteiler. Sam zeigt dir, wie ihr den Platz sauber haltet und die Lebensmittel ordentlich ablegt.')
                else:
                    st.write('Die Kühlware übergebt ihr direkt aus der Kühlbox an eure verabredeten Empfänger*innen.')
                if st.button('Lebensmittel teilen & Tour abschließen', type='primary'):
                    g['shared'] += len(p['loot'])
                    g['inventory'] = []
                    g['pickup'] += 1
                    g['log'].append(f"Tour {g['pickup']}: {p['title']} – Lebensmittel geteilt.")
                    go('verification' if g['pickup'] == len(PICKUPS) else 'pickup')
                    st.rerun()
        elif g['stage'] == 'verification':
            st.subheader('05 · Bereit für den nächsten Schritt')
            scene('🍌', 'Rückblick mit dem Team')
            st.write(f"„Drei Touren, viele gute Entscheidungen, {g['name']}“, sagt Sam. „Im echten Leben prüft nun eine zuständige Person deine Eignung und deine Profildaten. Es können auch zusätzliche Einführungsabholungen nötig sein.“")
            st.write('Laut Wiki werden Name, Adresse, Geburtsdatum und Profilfoto überprüft. Das Vorzeigen eines Ausweisdokuments reicht; eine Kopie darf nicht gefordert werden. Im Spiel brauchen wir diese Daten nicht.')
            st.markdown(f"Nachlesen: [Foodsaver werden]({SOURCES['Foodsaver']})")
            if st.button('Kapitel abschließen', type='primary'):
                g['log'].append('Lernkapitel abgeschlossen. Der echte Weg beginnt in der lokalen Community.')
                go('finish')
                st.rerun()
        elif g['stage'] == 'finish':
            st.subheader('Geschafft · Gemeinsam bleibt mehr übrig')
            scene('🧺', 'Ein voller Tisch statt einer vollen Tonne')
            st.write(f"{g['name']}, du hast den Lernweg durchgespielt: Grundlagen, Verantwortung und drei begleitete Touren. Deine Nachbarschaft teilt die geretteten Lebensmittel.")
            a, b = st.columns(2)
            a.metric('Begleitete Spieltouren', g['pickup'])
            b.metric('Geteilte Lebensmittelposten', g['shared'])
            st.caption(f"Lernversuche mit Hinweis: {g['mistakes']}. Fehler waren Gelegenheiten zum Lernen, keine echten Regelmeldungen.")
            st.markdown(f"Lust auf die echte Welt? Lies [Wie man Foodsaver wird]({SOURCES['Foodsaver']}) und informiere dich über die Abläufe in deinem Bezirk.")
            st.download_button('Mein Tagebuch herunterladen', '\n'.join(g['log']), file_name='mein-rettungstagebuch.txt', mime='text/plain')
            st.caption('Für eine neue Runde nutze „Spiel zurücksetzen“ in der Seitenleiste.')
