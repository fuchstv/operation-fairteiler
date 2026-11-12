"""Playable preparation and distribution based on selected Wiki passages."""
import streamlit as st
import rogue as game
import foodsharing as fs
from narrative import BUSINESS_NOTES


def briefing(r, scene):
    option = r['options'][r['pending_route']]
    name, icon, _, _ = game.BUSINESSES[option['venue']]
    scene(icon, 'Vor dem Abholtermin · ' + name)
    st.subheader('Abholbriefing: vorbereitet in den Betrieb')
    st.caption('Im Roguelike spielst du einen bereits verifizierten Foodsaver. Der Ausweis hier ist ein Spielgegenstand; du erhältst dadurch keine reale Verifizierung.')
    st.info(BUSINESS_NOTES[option['venue']])
    suffix = f"{r['seed']}_{r['day']}_{r['step']}_{option['venue']}"
    papers = st.checkbox('Foodsaver-Ausweis ist dabei; ich bin für den Termin eingetragen.', key='papers_'+suffix)
    notes = st.checkbox('Aktuelle Betriebs-Besonderheiten, Pinnwand und Teamchat sind gelesen.', key='notes_'+suffix)
    containers = st.checkbox('Saubere, lebensmittelechte Behälter sind eingepackt.', key='containers_'+suffix)
    hands = st.checkbox('Saubere Hände; für unverpackte Backwaren Zange, geeignete Handschuhe oder sorgfältig gewaschene Hände.', key='hands_'+suffix)
    data = fs.briefing(r)
    st.markdown('### ' + data['title'])
    st.write(data['text'])
    response = st.radio('Wie handelt das Abholteam?', range(len(data['options'])), format_func=lambda n: data['options'][n], index=None, key='brief_response_'+suffix)
    if r.get('briefing_feedback'):
        st.warning(r['briefing_feedback'])
    st.caption('Wissensentscheidung ohne Würfelwurf. Eine falsche Antwort lässt sich korrigieren und erzeugt keine Regelmeldung.')
    if st.button('Vorbereitung bestätigen & Abholung beginnen', type='primary', disabled=response is None or not all((papers, notes, containers, hands))):
        fs.finish_briefing(r, response, papers, notes, containers, hands)
        st.rerun()
    source = data.get('source', 'Verhaltensregeln')
    st.markdown(f"[Regeln zur Situation]({fs.WIKI + source}) · [Checkliste für Einführungsabholungen]({fs.WIKI}Einf%C3%BChrungsabholung_-_Checkliste)")


def distribution(r):
    fs.ensure(r)
    active = r['phase'] == 'map'
    st.subheader('Gerettet – und wie geht es weiter?')
    st.write('Was du nicht selbst verbrauchst, kannst du kostenlos und bedingungslos fairteilen: persönlich, mit einer Abholabsprache über einen Essenskorb oder über den Fairteiler.')
    st.caption('Hier wird nichts online veröffentlicht. Abholpersonen, Messwerte und Übergaben sind fiktiv. Frische-Runden sind Spielwerte; im Spiel gilt eine ungekühlte Runde bei Kühlware konservativ als längere Unterbrechung der Kühlkette.')
    if not active:
        st.info('Die Fairteilung planst du auf der Routenkarte zwischen zwei Stationen.')
    with st.expander('Hygieneplan · Fairteiler am Bezirkstreff', expanded=True):
        st.write('Der fiktive Fairteiler hat einen Kühlschrank. Vor der Nutzung: Temperatur prüfen, ungeeignete Lebensmittel entfernen, bei Bedarf reinigen und die Kontrolle dokumentieren.')
        today = any(e['day'] == r['day'] for e in r['hygiene_log'])
        if today:
            st.success('Heute dokumentiert: fiktive Messung 5 °C, Kontrolle und bedarfsgerechte Reinigung erledigt.')
        else:
            st.caption('Heute noch kein Eintrag. Kühlware bleibt bis zur Kontrolle für diesen Fairteiler gesperrt.')
        if st.button('Fairteiler kontrollieren & Hygieneplan führen', disabled=not active or today, key='maintain_fairteiler'):
            fs.maintain(r)
            st.rerun()
        st.caption('Wiki: Kühlschranktemperatur täglich ablesen; etwa 5 °C anstreben. Fairteiler regelmäßig kontrollieren und bei Bedarf reinigen, mindestens alle zwei Tage; Maßnahmen im Hygieneplan vermerken. Die Spielaktion kostet eine Runde.')
        if r['hygiene_log']:
            st.dataframe([{'Abholtag': e['day'], 'Temperatur (fiktiv)': f"{e['temperature']} °C", 'Kontrolliert / bei Bedarf gereinigt': 'Ja'} for e in r['hygiene_log']], hide_index=True, width='stretch')
    if r['basket']:
        basket = r['basket']
        st.markdown('### Dein reservierter Essenskorb')
        objects = [o for o in r['inventory'] if o['uid'] in basket['uids']]
        for obj in objects:
            ok, reason = fs.eligibility(r, obj, 'personal', for_basket=True)
            st.write(('✓ ' if ok else '⚠️ ') + game.ITEMS[obj['key']]['name'] + ' · ' + reason)
        ready = r['turn'] >= basket['ready_turn']
        st.write('Eine fiktive Abholperson hat die Abholung vereinbart.' if ready else 'Die fiktive Abholperson antwortet nach einer weiteren Runde. Deine Vorräte altern weiter.')
        if st.button('Eine Runde auf die Abholabsprache warten', disabled=not active or ready):
            fs.wait_for_basket(r)
            st.rerun()
        checked = st.checkbox('Vor dieser Übergabe erneut jedes Stück auf Genießbarkeit geprüft.', key='basket_checked')
        conversation = st.checkbox('Persönliches Gespräch möglich; verantwortungsvolle Behandlung zugetraut und nötige Hinweise gegeben.', key='basket_conversation')
        eligible = len(objects) == len(basket['uids']) and all(fs.eligibility(r, o, 'personal', for_basket=True)[0] for o in objects)
        if st.button('Essenskorb persönlich übergeben', disabled=not active or not ready or not checked or not conversation or not eligible):
            fs.deliver_basket(r, checked, conversation)
            st.rerun()
        if st.button('Fiktiven Essenskorb zurücknehmen', disabled=not active):
            fs.cancel_basket(r)
            st.rerun()
    st.markdown('### Übergabe planen')
    channel = st.selectbox('Weg der Fairteilung', list(fs.CHANNELS), format_func=fs.CHANNELS.get, key='sharing_channel')
    if channel == 'fairteiler':
        st.caption('Nicht-persönliche Weitergabe. Geprüfte ungeöffnete Kühlware ist nur mit erhaltener Kühlkette und kontrolliertem Kühlschrank geeignet. Zubereitete warme oder kühlbedürftige Speisen sind hier ausgeschlossen.')
    else:
        st.caption('Persönliche Weitergabe: Gespräch mit den Empfänger*innen muss möglich sein. Bei Bedarf auf schnellen Verbrauch, erneute Prüfung und Kühlung hinweisen; verantwortungsvolle Behandlung im Einzelfall einschätzen.')
    foods = [o for o in r['inventory'] if game.ITEMS[o['key']]['kind'] == 'food']
    available = []
    labels = {}
    for obj in foods:
        ok, reason = fs.eligibility(r, obj, 'personal' if channel == 'basket' else channel)
        label = f"#{obj['uid']} · {game.ITEMS[obj['key']]['name']}"
        labels[obj['uid']] = label
        st.caption(('✓ ' if ok else 'Nicht geeignet: ') + label + ' · ' + reason)
        if ok:
            available.append(obj['uid'])
    selected = st.multiselect('Lebensmittel auswählen', available, format_func=labels.get, key='share_selection_'+channel)
    checked = st.checkbox('Jedes ausgewählte Stück ist auf Genießbarkeit geprüft.', key='share_checked_'+channel)
    conversation = True
    if channel == 'personal':
        conversation = st.checkbox('Persönliche Übergabe und nötige Hinweise sind abgesprochen; verantwortungsvolle Behandlung ist zu erwarten.', key='share_conversation')
    disabled = not active or not selected or not checked or not conversation or (channel == 'basket' and r['basket'] is not None)
    label = 'Fiktiven Essenskorb anlegen' if channel == 'basket' else 'Kostenlos und bedingungslos fairteilen'
    if st.button(label, disabled=disabled, key='share_execute'):
        if channel == 'basket':
            fs.create_basket(r, selected, checked)
        else:
            fs.transfer(r, selected, channel, checked, conversation)
        st.rerun()
    st.caption('Jede Übergabe bzw. Essenskorb-Anlage kostet eine Runde. Weitergabe gibt +5 Kraft pro Posten als RPG-Bonus. Ein Essenskorb reserviert die Ware bis zur tatsächlichen Übergabe; erst dann zählt sie als fairteilt.')
    st.markdown(f'[Hygieneregeln]({fs.WIKI}Hygieneregeln) · [Fairteilung und Essenskörbe]({fs.WIKI}Fairteilung) · [Fairteiler und Hygieneplan]({fs.WIKI}Fairteiler_und_Abgabestellen)')
    with st.expander('Deine abgeschlossenen Fairteilungen'):
        for entry in reversed(r['distribution_log']):
            st.write(f"Abholtag {entry['day']} · {fs.CHANNELS[entry['channel']]}: " + ', '.join(entry['names']))
        if not r['distribution_log']:
            st.caption('Noch keine Übergabe dokumentiert.')
