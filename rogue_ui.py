"""Streamlit presentation for the expedition and two-human hotseat modes."""
import random
from html import escape
import rpg
import physiology
import equipment_ui
import community
import foodsharing
from foodsharing_ui import briefing, distribution
import streamlit as st
import rogue as game
from narrative import DISTRICTS, EVENTS, FLAVOUR, BUSINESS_NOTES

KINDS = {'weapon': '🛠️ Werkzeug / Duellgerät', 'armor': '🧥 Arbeitskleidung', 'gear': '🎒 Transport',
         'hands': '🧤 Handschuhe', 'face': '😷 Masken / Gesicht', 'feet': '🥾 Schuhe', 'belt': '🔦 Zubehör',
         'food': '🍎 Nahrung', 'consumable': '🧪 Verbrauch'}
RARITY = {'Gewöhnlich': '⚪', 'Selten': '🔵', 'Episch': '🟣', 'Legendär': '🟠'}


def description(data):
    words = []
    for key, title in [('attack', 'Tempo'), ('defense', 'Entlastung'), ('capacity', 'Traglast'),
                       ('heal', 'HP'), ('energy', 'Energie'), ('water', 'Wasser'),
                       ('fullness', 'Sättigung'), ('nausea', 'Übelkeit'), ('risk', 'Magenreiz'),
                       ('handling','Hygieneschutz'), ('dust_guard','Staubschutz'), ('odor_guard','Geruchsschutz'), ('grip','Griff'),
                       ('strength','Muskelkraft-Proben'), ('dexterity','Geschick-Proben'), ('insight','Übersicht-Proben'), ('presence','Auftreten-Proben'),
                       ('hygiene','Handhygiene'), ('repair','Reparatur'), ('gas','Bauchgas'), ('fiber','Ballaststoffe'), ('fat','Fett'), ('salt','Salz'), ('energy_save','Energieersparnis')]:
        if data.get(key):
            words.append(f"{data[key]:+} {title}")
    if data.get('cooling'):
        words.append('Kühlung: Verderb ×⅓')
    if data.get('durability'):
        words.append(f"Haltbarkeit {data['durability']}")
    if data.get('effect'):
        labels = {'cooling':'Kühlung','handling':'Hygieneschutz','odor_guard':'Geruchsschutz','insight':'Übersicht','dexterity':'Geschick','strength':'Muskelkraft','presence':'Auftreten','digestion':'Verdauung'}
        words.append(f"{labels[data['effect']]} {data['power']:+} für {data['turns']} Runden")
    return ' · '.join(words)


def perform(fn, *args):
    fn(*args)
    st.rerun()


def check_hint(spec, consequence):
    percent = spec['chance']
    tone, word = ('good', 'Gute Aussicht') if percent >= 70 else ('mixed', 'Offener Ausgang') if percent >= 40 else ('risky', 'Riskant')
    text = (f"{rpg.ATTRIBUTES[spec['attribute']]} · W20 {spec['bonus']:+} gegen Schwierigkeit {spec['dc']}. "
            f"Attribut {spec['base']:+}, Werkzeug {spec['tool']:+}, Ausrüstung/Effekte {spec.get('equipment',0):+}, Erschöpfung {spec['fatigue']:+}, Magen {spec['stomach']:+}, Zusammenhalt (Spielwert) {spec.get('community', 0):+}. "
            f"Erfolg: {percent} %. Natürliche 1 scheitert, natürliche 20 gelingt immer. {consequence}")
    st.markdown(f'<span class="check-badge {tone}" tabindex="0" aria-label="{escape(text, quote=True)}">'
                f'{word} · {percent} % · {escape(rpg.ATTRIBUTES[spec["attribute"]])}'
                f'<span class="check-tooltip" role="tooltip">{escape(text)}</span></span>', unsafe_allow_html=True)
    return text


def creation(r, scene):
    scene('🎲', 'Montag · Vor der ersten Abholung')
    st.subheader('Wer übernimmt die Runde?')
    st.write('Sam legt den Abholzettel auf den Tisch. Du bringst Erfahrung mit – aber niemand kann alles. Vier Attribute bestimmen, wie du schwierige Situationen angehst.')
    st.caption('Je Attribut: 4W6, niedrigsten Würfel streichen, drei übrige addieren. Du darfst den gesamten Satz zweimal neu würfeln; der alte Satz wird dabei verworfen.')
    name = st.text_input('Name auf dem Abholzettel', value='Alex', max_chars=30, key='character_name')
    background = st.selectbox('Dein Hintergrund', list(rpg.BACKGROUNDS), key='character_background')
    attribute, story = rpg.BACKGROUNDS[background]
    st.write(story + ' **+2 ' + rpg.ATTRIBUTES[attribute] + '.**')
    cols = st.columns(2)
    for i, (key, title) in enumerate(rpg.ATTRIBUTES.items()):
        with cols[i % 2]:
            value = r['attributes'][key] + (2 if key == attribute else 0)
            st.metric(title, value, help='Attributsbonus = (Wert − 10) // 2. Dieser Bonus zählt bei passenden W20-Proben.')
            dice = sorted(r['attribute_dice'][key])
            st.caption(f"Würfel: ~~{dice[0]}~~ + {' + '.join(map(str, dice[1:]))} = {r['attributes'][key]} · Bonus {rpg.modifier(value):+}")
    st.caption(f"Noch {2-r['rerolls']} neue Würfelsätze verfügbar. Muskelkraft verändert die Traglast um 2 je Attributsbonus; Werkzeug und Zustand beeinflussen die späteren Proben zusätzlich.")
    if st.button('Attribute neu würfeln', disabled=r['rerolls'] >= 2):
        perform(game.reroll_character, r)
    if st.button('Charakter übernehmen & Tour beginnen', type='primary'):
        perform(game.confirm_character, r, name, background)


def inventory(r, combat=False):
    st.markdown('### Rucksack')
    prefix = 'combat_' if combat else 'bag_'
    s = game.stats(r)
    st.caption(f"Traglast {game.weight(r)}/{s['capacity']} · {s['attack']} Tempo · {s['defense']} Entlastung · Kühlung {'an' if s['cooling'] else 'aus'}")
    if not r['inventory']:
        st.info('Dein Rucksack ist leer.')
    category = st.selectbox('Rucksack-Kategorie', ['Alle']+list(KINDS.values()), key=prefix+'filter')
    search = st.text_input('Im Rucksack suchen', key=prefix+'search')
    for obj in list(r['inventory']):
        if category != 'Alle' and KINDS[game.ITEMS[obj['key']]['kind']] != category:
            continue
        if search.casefold() not in game.ITEMS[obj['key']]['name'].casefold():
            continue
        data = game.ITEMS[obj['key']]
        uid = obj['uid']
        worn = uid in r['equipped'].values()
        reserved = foodsharing.reserved(r, uid)
        with st.container(border=True):
            st.markdown(f"**{RARITY[data['rarity']]} {data['name']}**" + (' · angelegt' if worn else ''))
            st.write(FLAVOUR[obj['key']])
            if 'durability' in data:
                st.caption(f"Zustand: {obj.get('durability',data['durability'])}/{data['durability']}" + (' · verschlissen, keine Boni' if obj.get('durability',1)==0 else ''))
            if data['kind'] in game.SLOTS and not worn:
                current = next((o for o in r['inventory'] if o['uid']==r['equipped'].get(data['kind'])),None)
                st.caption('Ersetzt: '+(game.ITEMS[current['key']]['name'] if current else 'freier Platz')+' · Platz: '+game.SLOTS[data['kind']])
            if reserved:
                st.caption('Für deinen fiktiven Essenskorb reserviert. Zum Essen oder Ablegen erst den Essenskorb zurücknehmen.')
            if data.get('cold') and not obj.get('cold_chain_ok', True):
                st.warning('Kühlkette im Spiel länger unterbrochen: nicht zur Weitergabe geeignet, auch wenn das Item noch Frischepunkte besitzt.')
            st.caption(f"{KINDS[data['kind']]} · {data['rarity']} · Gewicht {data['weight']} · {description(data)}")
            if data['kind'] == 'food':
                fresh = game.freshness(r, obj)
                if fresh == 0:
                    st.warning('Verdorben: Essen erhöht den Magenreiz um weitere 50 Punkte. Nicht zum Fairteilen geeignet.')
                else:
                    st.caption(f"Frische: noch {fresh:.1f} ungekühlte Runden. " + ('Kühlpflichtig; persönliche Übergabe oder geeigneter gekühlter Fairteiler bei erhaltener Kühlkette.' if data.get('cold') else ''))
            cols = st.columns(2)
            if data['kind'] in game.SLOTS:
                if cols[0].button('Anlegen', key=f'{prefix}equip_{uid}', disabled=worn or r['phase'] != 'map', width='stretch'):
                    perform(game.equip, r, uid)
            else:
                if cols[0].button('Essen' if data['kind'] == 'food' else 'Benutzen', key=f'{prefix}use_{uid}',
                                  disabled=reserved or r['phase'] not in ('map', 'combat'), width='stretch'):
                    perform(game.consume, r, uid)
            if cols[1].button('Ablegen', key=f'{prefix}drop_{uid}', disabled=reserved or worn or r['phase'] != 'map', width='stretch'):
                perform(game.drop, r, uid)
    st.caption('Essen und Benutzen kosten je eine Runde. Im Kampf folgt ein gegnerischer Zug. Ausrüstung wechseln und Ablegen sind nur auf der Karte möglich.')


def status(r):
    a, b, c, d = st.columns(4)
    a.metric('Kraft', f"{r['hp']}/{100 + (r['level']-1)*8}")
    b.metric('Energie', r['energy'])
    c.metric('Wasser', r['water'])
    d.metric('Gerettet / geteilt', f"{r['rescued']} / {r['shared']}")
    x, y = st.columns(2)
    x.progress(r['fullness'] / 100, text=f"Magenfüllung {r['fullness']}/100")
    y.progress(r['nausea'] / 100, text=f"Übelkeit {r['nausea']}/100")
    st.markdown('**' + DISTRICTS[r['day']-1][0] + '**')
    st.caption(f"Zusammenhalt (Spielwert) {r.get('trust', 50)}/100 · offene Rücksprachen: {sum(not v['resolved'] for v in r.get('violations', []))}")
    st.caption(f"{r.get('character_name', 'Alex')} · {r.get('background') or 'Ohne Hintergrund'}")
    st.caption(' · '.join(f'{title} {r.get("attributes", {}).get(key, 10)} ({rpg.modifier(r.get("attributes", {}).get(key, 10)):+})' for key, title in rpg.ATTRIBUTES.items()))
    st.caption(f"Abholtag {r['day']}/5 · Station {r['step']+1}/4 · Level {r['level']} · XP {r['xp']} · Runde {r['turn']} · Seed {r['seed']}")
    if r['nausea'] >= 50:
        st.warning('Ab 50 Übelkeit: −5 Arbeitstempo. Ab 70: Magenkrämpfe kosten jede Runde 5 Kraft.')
    if r.get('hygiene',100) < 40:
        st.warning('Schmutzige Hände: Essen erhöht den Magenreiz. Waschplatz und Seife findest du unter Inventar & Magen.')
    if r.get('urgency',0) >= 80:
        st.warning('Dringende Toilettenpause nötig: zusätzlich −2 Energie pro Runde, bis du eine Pause einlegst.')
    if game.weight(r) > game.stats(r)['capacity']:
        st.warning('Du bist überladen. Lege Gegenstände ab oder rüste einen größeren Transport aus.')


def expedition(r, scene, chime):
    phase = r['phase']
    if r.get('last_check'):
        check = r['last_check']
        (st.success if check['success'] else st.warning)(rpg.summary(check))
    if phase == 'map':
        st.subheader('Wähle deine nächste Abholung')
        st.write(DISTRICTS[r['day']-1][1])
        st.caption('Vier Stationen je Abholtag im selben Stammbezirk. Die letzte Ausgabe in der Werkskantine schließt die Woche ab.')
        for i, option in enumerate(r['options']):
            with st.container(border=True):
                if option['kind'] == 'business':
                    name, icon, foods, story = game.BUSINESSES[option['venue']]
                    st.markdown(f'### {icon} {name}')
                    st.write(story)
                    with st.expander('Betriebs-Besonderheiten & Nachricht aus dem Betriebsteam'):
                        st.caption('Fiktive Betriebsseite im Spiel · BV: Robin · Nur für eingetragene Foodsaver und vereinbarte Abholtermine.')
                        st.write(BUSINESS_NOTES[option['venue']])
                    st.caption('Risiko ' + '🌶️' * option['danger'] + ' · mögliche Lebensmittel: ' + ', '.join(game.ITEMS[k]['name'] for k in foods))
                else:
                    name = {'camp': 'Nachbarschaftstreff', 'event': 'Unbekannter Umweg', 'arena': 'Trainingsduell gegen einen NPC', 'bins': 'Tonnenrunde am Sammelplatz'}[option['kind']]
                    st.markdown('### ' + {'camp': '🏕️', 'event': '❔', 'arena': '🥊', 'bins': '🗑️'}[option['kind']] + ' ' + name)
                    st.caption({'camp': 'Ausruhen oder geeignete Lebensmittel teilen.', 'event': 'Ein Fund oder ein Rückschlag? Du entscheidest über das Risiko.', 'bins': 'Sortierrunde mit Materialangeboten; Handschuhe und Masken verändern die Spielbelastung.', 'arena': 'Freiwilliger Abhol-Parcours mit einem simulierten Foodsaver. Bei Erfolg gibt es Material für weitere Abholungen. Für zwei echte Spieler nutze den PvP-Reiter.'}[option['kind']])
                if option['kind'] == 'business':
                    if r.get('standing', {}).get(option['venue'], 0) >= 2:
                        st.caption('Du kennst die Abläufe hier: −1 Schwierigkeit beim Weiterarbeiten.')
                    check_hint(rpg.action_spec(r, 'attack', option), 'Aussicht für Weiterarbeiten vor Ort. Die Route zu wählen erfordert noch keinen Wurf.')
                if st.button(f'Route {i+1}: {name}', key=f'visit_{i}', width='stretch'):
                    perform(game.visit, r, i)
    elif phase in ('bins','bin_loot'):
        equipment_ui.encounter(r,scene,check_hint,description)
    elif phase == 'briefing':
        briefing(r, scene)
    elif phase == 'combat':
        enemy = r['enemy']
        option = r['encounter']
        if option['kind'] == 'business':
            name, icon, _, story = game.BUSINESSES[option['venue']]
            scene(icon, name)
        else:
            scene('🥊', 'Trainingsarena · NPC-Begegnung')
        work = enemy.get('narrative')
        st.subheader(enemy['name'])
        if work:
            st.write(work['opening'])
        st.progress(enemy['hp']/enemy['max_hp'], text=f"{'Restaufwand' if work else 'Kondition des Trainingspartners'}: {enemy['hp']}/{enemy['max_hp']}")
        if enemy['boss']:
            st.caption('Letzte zugesagte Abholung: Für diese Ausgabe ist kein Ersatz mehr erreichbar.')
        st.info((work['pressure'] if enemy['intent'] == 'attack' else work['recover']) if work else ('Dein Trainingspartner legt vor.' if enemy['intent'] == 'attack' else 'Dein Trainingspartner braucht eine Pause.'))
        st.caption('Jede Aktion ist eine W20-Probe und kostet 3 Energie und Wasser. Die Farbe zeigt deine Chance mit dem aktuellen Werkzeug und Zustand. Details stehen im Tooltip; der Wurf wird vor den Ressourcenkosten berechnet.')
        cols = st.columns(2)
        for i, (key, label) in enumerate([('attack', '🛠️ Weiterarbeiten' if work else 'Parcours: Vorlegen'), ('heavy', '💪 Kräftig anpacken' if work else 'Parcours: Sprint'), ('defend', '🧥 Kräfte einteilen' if work else 'Parcours: Absichern'), ('flee', '📞 Ersatz im Betriebsteam suchen')]):
            with cols[i % 2]:
                blocked = (key == 'heavy' and r['energy'] < 15) or (key == 'flee' and enemy['boss'])
                consequence = {'attack': 'Erfolg: voller Fortschritt. Misserfolg: halber Fortschritt (mindestens 1).',
                               'heavy': 'Erfolg: 1,8-facher Fortschritt. Misserfolg: kein Fortschritt. Immer zusätzlich 12 Energie.',
                               'defend': 'Erfolg: 9 weniger Kraftverlust. Misserfolg: nur 3 weniger. Kein Fortschritt.',
                               'flee': 'Erfolg: Ersatz übernimmt; du nimmst keine Lebensmittel mit. Misserfolg: Du bleibst vor Ort.'}[key]
                if blocked:
                    st.caption('Nicht verfügbar: ' + ('kein Ersatz für das Finale' if key == 'flee' else 'mindestens 15 Energie nötig'))
                    hint = consequence
                else:
                    hint = check_hint(rpg.action_spec(r, key), consequence)
                if st.button(label, key='fight_'+key, width='stretch', disabled=blocked, help=hint):
                    perform(game.combat_action, r, key)
        for line in r['combat'][-6:]:
            st.caption(line)
        with st.expander('Verbrauchsgegenstand im Kampf einsetzen'):
            inventory(r, combat=True)
    elif phase == 'loot':
        scene('🎁', 'Die Abholung ist geschafft')
        st.subheader('Abholung einpacken')
        st.write(r['log'][-1])
        st.caption('Lebensmittel aus der Abholung, Ersatzmaterial vom Treff und Wasser für den Rückweg. Nur eingepackte Lebensmittel zählen als gerettet.')
        if st.session_state.get('rogue_sound'):
            st.audio(chime(), format='audio/wav', autoplay=True)
        st.caption(f"Rucksack: {game.weight(r)}/{game.stats(r)['capacity']}. Was nicht in deinen Rucksack passt, übernimmt im Spiel das Betriebsteam.")
        for i, key in enumerate(r['loot']):
            data = game.ITEMS[key]
            st.write(f"{RARITY[data['rarity']]} **{data['name']}** · {description(data)}")
            full = game.weight(r) + data['weight'] > game.stats(r)['capacity']
            if st.button('Mitnehmen' + (' · Rucksack voll' if full else ''), key=f'loot_{i}', disabled=full):
                perform(game.take_loot, r, i)
        if st.button('Zur nächsten Station', type='primary'):
            perform(game.finish_loot, r)
    elif phase == 'camp':
        scene('🏕️', 'Nachbarschaftstreff')
        st.subheader('Zeit für eine Pause')
        st.write('Eine Aktion, dann geht es weiter. Hier steht ein ungekühltes Regal: Nur geeignete, unreservierte Lebensmittel hineinlegen. Zubereitete warme/kühlbedürftige Speisen gehören nicht hinein. RPG-Bonus: +5 Kraft je Posten. Weitere Übergabewege und den gekühlten Fairteiler findest du zwischen den Stationen unter „Fairteilen“.')
        if st.button('Ausruhen · +30 HP, +35 Energie/Wasser, −35 Übelkeit', type='primary'):
            perform(game.camp, r, 'rest')
        if st.button('Geeignete Lebensmittel fairteilen'):
            perform(game.camp, r, 'share')
    elif phase == 'incident':
        data = community.INCIDENTS[r['incident']]
        scene('📋', 'Eine Rückfrage vor dem Weiterfahren')
        st.subheader(data['title'])
        st.write(data['text'])
        st.info(data['rule'])
        st.markdown(f"[Regel nachlesen: {data['source']}](https://wiki.foodsharing.network/wiki/{data['source']})")
        st.caption('Die folgenden Zusammenhaltswerte und Folgen sind erfundene RPG-Mechanik. Ein Würfelpech allein ist keine Regelverletzung.')
        if st.button(data['good'] + ' · −5 Energie, +5 Zusammenhalt', type='primary'):
            perform(community.incident_choice, r, 'good')
        hint = check_hint(rpg.preview(r, 'presence', 13), 'Erfolg: Klärung kostet 2 Energie. Misserfolg: 8 Energie. In beiden Fällen +5 Zusammenhalt, keine Regelverletzung.')
        if st.button('Mit Robin (BV) das weitere Vorgehen absprechen', help=hint):
            perform(community.incident_choice, r, 'ask')
        st.warning('Bewusste Abkürzung: +10 Energie, −15 Zusammenhalt und ein Eintrag in deinen Gesprächsnotizen. Fragliche Lebensmittel werden im Spiel nicht weitergegeben.')
        acknowledge = st.checkbox('Ich wähle bewusst die regelwidrige Abkürzung.', key=f"bad_choice_{r['business_pickups']}")
        if st.button(data['bad'], disabled=not acknowledge):
            perform(community.incident_choice, r, 'bad')
    elif phase == 'event':
        event = EVENTS[r['event']]
        scene('❔', event['title'])
        st.write(event['text'])
        hint = check_hint(rpg.action_spec(r, 'event'), 'Erfolg: ein Materialfund, falls Platz ist. Misserfolg: −15 Kraft, +10 Übelkeit.')
        if st.button(event['risk'], help=hint):
            perform(game.event, r, False)
        st.caption('🟢 Sicher · Ohne Probe: +8 Energie, kein Materialfund.')
        if st.button(event['safe'], type='primary', help='Kein Würfelwurf. Du erhältst sicher 8 Energie, verzichtest aber auf den Materialfund.'):
            perform(game.event, r, True)
    elif phase in ('dead', 'victory'):
        won = phase == 'victory'
        scene('🏆' if won else '💀', 'Run abgeschlossen' if won else 'Das Betriebsteam organisiert Ersatz')
        st.subheader('Am Treff brennt noch Licht' if won else 'Für heute reicht die Kraft nicht mehr')
        st.write(f"{r['wins']} Begegnungen gewonnen · {r['rescued']} Posten gerettet · {r['shared']} geteilt · Level {r['level']}.")
        st.write('Sam hat den Schlüssel am üblichen Haken gelassen. Die Kisten sind verteilt; morgen beginnt eine andere Runde.' if won else 'Du meldest dich am Treff. Robin klärt die offenen Abholtermine mit den Betriebsteams. Bei der nächsten Runde fängst du mit frischen Vorräten an.')
        open_cases = sum(not v['resolved'] for v in r['violations'])
        if open_cases:
            st.warning(f'Beim Bezirkstreffen gibt es Gesprächsbedarf: {open_cases} Situationen sind noch zu besprechen. Die Tour ist beendet; deine persönlichen Gesprächsnotizen bleiben sichtbar.')
        elif r['trust'] >= 70:
            st.success('Sam: „Auf deine Absprachen konnten wir uns verlassen. Für die nächste Runde würde ich dich wieder fragen.“')
        st.caption('Permadeath: Für die nächste Tour gibt es einen neuen Charakter und frische Vorräte. Dein Lernabenteuer bleibt davon getrennt.')
        st.download_button('Run-Tagebuch herunterladen', '\n'.join(r['log']), file_name=f"rettungsrun-{r['seed']}.txt", mime='text/plain')
        if st.button('Neue zufällige Rettungstour', type='primary'):
            st.session_state.rogue_run = game.make_run(random.randrange(2**31))
            st.rerun()


def pvp():
    st.subheader('🥊 PvP · Zwei Menschen, ein Bildschirm')
    st.write('Nach der Tour räumt ihr am Treff einen Abhol-Parcours auf: leere Kisten, ein enger Durchgang, gleiche Ausrüstung. Wer die andere Person zuerst aus der Puste bringt, gewinnt. Ihr spielt abwechselnd an diesem Gerät; der Wettbewerb zählt nicht zur Abholrunde.')
    if 'local_duel' not in st.session_state:
        with st.form('duel_setup'):
            a, b = st.columns(2)
            name_a = a.text_input('Spieler 1', value='Sam', max_chars=30)
            name_b = b.text_input('Spieler 2', value='Hannes', max_chars=30)
            # Identical weapons keep the match symmetrical.
            weapon = st.selectbox('Gleiches Parcoursgerät für beide', [k for k, v in game.ITEMS.items() if v['kind'] == 'weapon'], format_func=lambda k: game.ITEMS[k]['name'])
            if st.form_submit_button('Hotseat-Duell starten', type='primary'):
                st.session_state.local_duel = game.make_duel(name_a, name_b, weapon, weapon)
                st.rerun()
        return
    duel = st.session_state.local_duel
    cols = st.columns(2)
    for i, player in enumerate(duel['players']):
        with cols[i]:
            st.markdown('### ' + player['name'])
            st.progress(player['hp']/100, text=f"{player['hp']}/100 Kondition")
            st.caption(f"{game.ITEMS[player['weapon']]['name']} · {player['stamina']} Ausdauer · {player['potions']} Versorgungspausen · " + ('Block aktiv' if player['guard'] else 'kein Block'))
    if duel['winner'] is not None:
        st.success(duel['players'][duel['winner']]['name'] + ' gewinnt das Duell!')
    else:
        active = duel['players'][duel['turn']]
        st.info(f"{active['name']} ist am Zug. Danach Gerät weitergeben.")
        st.caption('Tempo: +3 Ausdauer. Sprint: −12 Ausdauer, ×1,7 Druck. Absichern: 12 weniger Konditionsverlust, +10 Ausdauer. Versorgungspause: +24 Kondition, zweimal pro Duell.')
        cols = st.columns(2)
        for i, (key, label) in enumerate([('attack', 'PvP: Tempo machen'), ('heavy', 'PvP: Sprinten'), ('defend', 'PvP: Absichern'), ('heal', 'PvP: Versorgungspause')]):
            disabled = key == 'heavy' and active['stamina'] < 12 or key == 'heal' and active['potions'] == 0
            if cols[i % 2].button(label, disabled=disabled, width='stretch'):
                perform(game.duel_action, duel, key)
    for line in duel['log'][-6:]:
        st.caption(line)
    if st.button('Duell zurücksetzen'):
        del st.session_state.local_duel
        st.rerun()


def district_board(r):
    st.subheader('Bezirkstreffen · Sam (BOT) & Robin (BV)')
    st.write('Sam ist Botschafterin (BOT) im Stammbezirk und organisiert den Austausch beim Bezirkstreffen. Robin ist betriebsverantwortliche Person (BV) und koordiniert Abholtermine mit den Betriebsteams. Bei Fragen zu einer Abholung wendest du dich zunächst an das Betriebsteam oder die zuständigen BV.')
    st.caption('BOTs = Botschafter*innen · BV = Betriebsverantwortliche. Der Zusammenhalt-Wert und Materialboni sind erfundene RPG-Mechanik, keine offizielle Bewertung oder Voraussetzung für Unterstützung bei foodsharing.')
    st.progress(r['trust'] / 100, text=f"Zusammenhalt (erfundener Spielwert): {r['trust']}/100")
    with st.expander('Begriffe aus dem foodsharing-Wiki'):
        st.markdown('**Betriebsteam:** Foodsaver, die beim Betrieb eingetragen sind. **BV:** koordinieren die Kooperation und Abholtermine. **BOTs:** koordinieren den Bezirk und den Austausch. **Betriebs-Besonderheiten:** Absprachen für den Betrieb; vor der Abholung zusammen mit Pinnwand und Teamchat lesen.')
        st.markdown('**Fairteilung:** Lebensmittel bedingungslos und kostenlos weitergeben, zum Beispiel persönlich, als Essenskorb oder über einen Fairteiler. **MRV / LMG:** Meldung einer Regelverletzung / Lokale Meldungsgruppe.')
        st.markdown('[Betrieb](https://wiki.foodsharing.network/wiki/Betrieb) · [BOTs](https://wiki.foodsharing.network/wiki/Botschafter*in) · [BV](https://wiki.foodsharing.network/wiki/Betriebsverantwortliche*r) · [Fairteilung](https://wiki.foodsharing.network/wiki/Fairteilung)')
    if r['trust'] >= 70:
        st.success('Sam: „Die Absprachen sitzen. Wenn du anrufst, wissen die Leute, woran sie sind.“ +1 auf Auftreten-Proben.')
    elif r['trust'] < 25:
        st.warning('Robin: „Lass uns die offenen Absprachen gemeinsam klären.“ −1 auf Auftreten-Proben. Unterstützung braucht mindestens 40 Zusammenhalt.')
    else:
        st.info('Sam: „Sag Bescheid, bevor eine Abholung kippt. Zusammen finden wir eher Ersatz.“')
    st.markdown('### Ersatz für einen Abholtermin suchen')
    st.write('Einmal je Abholtag (Spielbonus): +12 Kraft, +30 Wasser und +20 Energie, danach Kosten einer Runde. Verfügbar auf der Routenkarte ab 40 Zusammenhalt.')
    if st.button('Im Betriebsteam um Unterstützung bitten', disabled=r['phase'] != 'map' or r['trust'] < 40 or r['day'] in r['supported_days']):
        perform(community.support, r)
    st.markdown('### Mitmachen im Bezirk')
    st.caption('Fairteilen heißt bedingungslos und kostenlos weitergeben. Das Material aus dem Treff ist eine Spielbelohnung, keine Bezahlung oder Gegenleistung für Lebensmittel.')
    for key, request in community.REQUESTS.items():
        with st.container(border=True):
            st.markdown('**' + request['title'] + '**')
            st.write(request['text'])
            done = min(request['target'], r[request['counter']])
            st.progress(done / request['target'], text=f"{done}/{request['target']} · Material: {game.ITEMS[request['reward']]['name']} · +5 Zusammenhalt")
            if key in r['claimed']:
                st.caption('Rückmeldung gegeben; Material für weitere Abholungen erhalten.')
            else:
                full = game.weight(r) + game.ITEMS[request['reward']]['weight'] > game.stats(r)['capacity']
                if st.button('Rückmeldung geben' + (' · Rucksack voll' if full else ''), key='claim_'+key, disabled=r['phase'] != 'map' or done < request['target'] or full):
                    perform(community.claim, r, key)
    st.markdown('### Deine Gesprächsnotizen')
    st.caption('Persönliche Klärung im Spiel, keine Meldung einer Regelverletzung (MRV). Formelle Meldungen bearbeitet grundsätzlich die Lokale Meldungsgruppe (LMG); nicht eine BOT allein. Ziel ist Verständnis und eine tragfähige Lösung im Einzelfall.')
    st.markdown('[Umgang mit Regelverletzungen im Wiki](https://wiki.foodsharing.network/wiki/Regelverletzungen_-_Konsequenzen_und_Bearbeitung)')
    if not r['violations']:
        st.caption('Keine offenen Rücksprachen. Würfelpech ist keine Regelverletzung.')
    for i, violation in enumerate(r['violations']):
        with st.container(border=True):
            st.write(f"Abholtag {violation['day']}: **{violation['title']}**")
            st.write(violation['rule'])
            if violation['resolved']:
                st.caption('Gespräch geführt. Die persönliche Notiz bleibt im Spieltagebuch; dies ist keine formelle Meldungsbearbeitung.')
            else:
                st.caption('Offen. Du besprichst das Vorgehen mit den Beteiligten und Robin als BV. Kostet 8 Energie und eine Runde; +7 Zusammenhalt. Mindestens 11 Energie nötig.')
                if st.button('Persönliches Gespräch führen', key=f'repair_{i}', disabled=r['phase'] != 'map' or r['energy'] < 11):
                    perform(community.repair, r, i)
    with st.expander('Deine Betriebsteams'):
        for venue, count in sorted(r['standing'].items()):
            st.write(f"{game.BUSINESSES[venue][0]}: {count} Abholungen abgeschlossen" + (' · Abläufe bekannt (−1 SG beim Weiterarbeiten)' if count >= 2 else ''))
        if not r['standing']:
            st.caption('Deine erste betriebliche Abholung steht noch aus.')


def render(scene, chime):
    if 'rogue_run' not in st.session_state:
        st.session_state.rogue_run = game.make_run(random.randrange(2**31))
    r = st.session_state.rogue_run
    community.ensure(r)
    foodsharing.ensure(r)
    physiology.ensure(r)
    with st.sidebar:
        st.markdown('### ⚔️ Rettung auf Risiko')
        st.write('Der Lieferwagen fällt aus. Sam zählt auf deine Runde.')
        st.toggle('Roguelike-Sounds', key='rogue_sound')
        st.toggle('Roguelike-Animationen', value=True, key='rogue_motion')
        if st.session_state.rogue_sound:
            st.audio(chime(), format='audio/wav')
        with st.expander('Neue Tour / Seed'):
            seed = st.number_input('Seed', min_value=0, max_value=2**31-1, value=r['seed'], step=1, key='rogue_seed')
            st.caption('Gleicher Seed und gleiche Entscheidungen ergeben dieselbe Tour. Neustart verwirft den laufenden Run.')
            confirm = st.checkbox('Aktuellen Run verwerfen', key='confirm_restart')
            if st.button('Tour mit diesem Seed starten', disabled=not confirm):
                st.session_state.rogue_run = game.make_run(int(seed))
                st.rerun()
        with st.expander('Attribute und Proben'):
            st.write('W20 + Attributsbonus + Werkzeug − Zustandsabzüge gegen die Schwierigkeit (SG). Eine natürliche 1 scheitert immer, eine 20 gelingt immer. Grün: mindestens 70 %, Gelb: 40–65 %, Rot: unter 40 %. Die Chancen werden ohne Zufallswurf berechnet.')
            st.caption('Bei wenig Energie (unter 25) und starker Übelkeit (ab 50) jeweils −2 auf die Probe. Die Vorschau gilt vor den Kosten der gewählten Aktion. Hintergrundboni sind bereits in den Attributswerten enthalten.')
        with st.expander('So funktioniert der Run'):
            st.write('Lies vor dem Abholtermin die Betriebs-Besonderheiten und die Nachricht aus dem Betriebsteam. Bei der Abholung arbeitest du die Aufgaben rundenweise ab. Plane auch Pausen und die Fairteilung der geretteten Lebensmittel ein.')
            st.write('Jede Reise, jeder Kampfzug und jedes verbrauchte Item lassen Vorräte altern. Eine Pause am Bezirkstreff stellt Ressourcen wieder her. Der Ausfall von Energie oder Wasser kostet HP.')
            st.caption('Satirische Spielmechanik: Waffen, Duelle und die Magensimulation sind erfunden. Die Zahlen sind keine Lebensmittel- oder Gesundheitsempfehlungen. Keine echten Medikamente einsetzen.')
        with st.expander('Run-Tagebuch'):
            for line in reversed(r['log'][-20:]):
                st.write(line)
    st.markdown('<div class="eyebrow">Die Abholrunde · Zwischen Kanal und Nordtor</div>', unsafe_allow_html=True)
    st.title('Operation: Feierabend')
    st.caption('Prozedurale Rettungstouren · Permadeath · Lokales PvP')
    st.markdown('''<style>
.check-badge {display:inline-block;position:relative;margin:.4rem 0;padding:.35rem .6rem;border-radius:6px;font-size:.85rem;font-weight:600;border:1px solid;cursor:help;}
[data-testid="stElementContainer"]:has(.check-badge:hover),[data-testid="stElementContainer"]:has(.check-badge:focus) {position:relative;z-index:1001;overflow:visible;}
.check-badge.good {color:#225224;background:#e3f2e4;border-color:#82ae86;}
.check-badge.mixed {color:#674500;background:#fff1cb;border-color:#cba64e;}
.check-badge.risky {color:#812c25;background:#ffe7e1;border-color:#c98175;}
.check-tooltip {pointer-events:none;display:none;position:absolute;top:100%;left:0;z-index:99;width:280px;max-width:75vw;padding:.7rem;border:1px solid currentColor;border-radius:6px;background:inherit;box-shadow:0 3px 12px #0002;font-weight:400;line-height:1.5;}
.check-badge:hover .check-tooltip,.check-badge:focus .check-tooltip {display:block;}
.check-badge:focus-visible {outline:3px solid #533a20;outline-offset:2px;}
</style>''', unsafe_allow_html=True)
    if r['phase'] == 'creation':
        creation(r, scene)
        return
    route, bag, arena, codex, district, sharing, bins = st.tabs(['🗺️ Rettungstour', '🎒 Inventar & Magen', '🥊 PvP · Hotseat', '📚 Item-Lexikon', '📬 Bezirk & Betriebsteams', '🧺 Fairteilen', '🗑️ Tonnenrunde'])
    with route:
        status(r)
        expedition(r, scene, chime)
    with bag:
        st.markdown('### Erst eine Pause, dann die nächste Kiste')
        st.write('Pro Runde sinkt die Magenfüllung um 5. Essen über 85 Füllung erhöht die Übelkeit. Energie wird teilweise sofort und teilweise während der Verdauung frei. Hygiene, Salzlast, Bauchgas und Toilettendrang verändern, wie gut du durch die nächste Runde kommst.')
        st.caption('Kühlung wirkt nur während der Runden, in denen sie angelegt ist. Anlegen macht alte Nahrung nicht wieder frisch.')
        equipment_ui.body(r)
        equipment_ui.loadout(r)
        inventory(r)
    with arena:
        pvp()
    with codex:
        st.subheader(f'{len(game.ITEMS)} Fundstücke für deinen Run')
        selected = st.selectbox('Kategorie', ['Alle'] + list(KINDS.values()))
        search = st.text_input('Im Item-Lexikon suchen',key='codex_search')
        rarity = st.selectbox('Seltenheit', ['Alle']+list(RARITY),key='codex_rarity')
        rows = [dict(Item=v['name'], Kategorie=KINDS[v['kind']], Seltenheit=v['rarity'], Gewicht=v['weight'], Wirkung=description(v), Herkunft=FLAVOUR[k]) for k, v in game.ITEMS.items() if (selected == 'Alle' or KINDS[v['kind']] == selected) and (rarity=='Alle' or v['rarity']==rarity) and search.casefold() in v['name'].casefold()]
        st.caption(f'{len(rows)} Treffer')
        st.dataframe(rows, hide_index=True, width='stretch')
        st.caption('Der Roguelike-Modus ist Satire. Das separate Lernabenteuer enthält die belegten Wiki-Regeln.')

    with district:
        district_board(r)

    with sharing:
        distribution(r)
    with bins:
        if r['phase'] in ('bins','bin_loot'):
            equipment_ui.encounter(r,scene,check_hint,description,prefix='tab_')
        else:
            equipment_ui.collection_points(r)
