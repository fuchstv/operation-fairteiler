"""Selected Wiki-backed pickup and distribution rules, separate from RPG stats."""
WIKI = 'https://wiki.foodsharing.network/wiki/'
BRIEFINGS = [
    dict(title='Die Ausgabe verzögert sich', text='Die Beschäftigten bitten euch, noch 15 Minuten zu warten. Der Abholtermin war gerade erst.',
         options=['Die gewünschte Wartezeit akzeptieren und Rücksicht auf den Betrieb nehmen.', 'Sofort auf der Ausgabe bestehen.'], correct=0,
         why='Eine vom Betrieb gewünschte Wartezeit bis 15 Minuten muss akzeptiert werden (Verhaltensregeln B7).'),
    dict(title='Nach 25 Minuten ist noch nichts bereit', text='Ihr wartet bereits 25 Minuten über die vereinbarte Uhrzeit hinaus. Jetzt ist die Ausgabe bereit und das Team möchte die Abholung noch durchführen.',
         options=['Streit anfangen und Lebensmittel einfordern.', 'Höflich bleiben und gemeinsam abholen; nach mehr als 15 Minuten hättet ihr auch höflich absagen dürfen.'], correct=1,
         why='Nach 15 Minuten kann höflich abgesagt werden (B7). In dieser Szene entscheidet ihr euch nach Rücksprache für die inzwischen mögliche Abholung.'),
    dict(title='Eine Freundin hilft beim Tragen', text='Eine Freundin ohne Foodsaver-Ausweis begleitet dich als Tragehilfe. Sie ist nicht für den Abholtermin eingetragen.',
         options=['Sie mit in den Betrieb nehmen.', 'Sie abseits des Betriebs warten lassen; das eingetragene Abholteam geht gemeinsam hinein.'], correct=1,
         why='Tragehilfen warten abseits des Betriebs. Wer hinein darf, regelt B5; das Abholteam betritt und verlässt den Betrieb gemeinsam (B3).'),
    dict(title='Ein unfreundlicher Empfang', text='Eine beschäftigte Person beschwert sich schroff über die Abholung. Die Kundschaft steht daneben.',
         options=['Höflich bleiben und anschließend BV informieren.', 'Die Diskussion vor der Kundschaft austragen.'], correct=0,
         why='Auch bei unfreundlichem Verhalten bleiben Foodsaver höflich und können anschließend BV informieren (B8). Diskussionen gehören nicht in die Abholung (B6).'),
    dict(title='Eine Kiste fehlt auf der alten Liste', text='Die Nachricht im Teamchat und die Betriebs-Besonderheiten wurden heute geändert. Der Ausdruck in deiner Tasche ist von gestern.',
         options=['Nur auf den alten Ausdruck vertrauen.', 'Aktuelle Besonderheiten, Pinnwand und Teamchat lesen; Unklarheiten mit BV klären.'], correct=1,
         why='Vor der Abholung muss die aktuelle Fassung der Betriebs-Besonderheiten samt Pinnwand und Teamchat bekannt sein (C1).'),
    dict(title='Mehr Brot als erwartet', text='Ihr holt zu zweit ab. Es sind viel mehr Backwaren übrig als gestern. Eine Person möchte alle Brezeln für sich.',
         options=['Die Lieblingsware zuerst für sich zurücklegen.', 'Gemeinsam alle übergebenen genießbaren Lebensmittel übernehmen und die Aufteilung einvernehmlich klären.'], correct=1,
         why='Grundsätzlich übernehmen die Abholenden gleich viel, außer alle sind mit einer anderen Aufteilung einverstanden (B4). Nicht tragbare Mengen übernimmt hier im Spiel das übrige Betriebsteam.'),
]
BRIEFINGS.extend([
    dict(title='MHD ist nicht Verbrauchsdatum', text='In der Ausgabe liegt eine ungeöffnete Packung mit überschrittenem Mindesthaltbarkeitsdatum. Die Aufbewahrung war korrekt.',
         options=['Nur wegen des MHD ungeprüft entsorgen.', 'Genießbarkeit prüfen und die übrigen Weitergaberegeln beachten; ein überschrittenes MHD ist kein pauschales Weitergabeverbot.'], correct=1,
         why='Lebensmittel nach MHD können weitergegeben werden. Nach Verbrauchsdatum ist die Weitergabe verboten. Jedes Stück ist vor Weitergabe zu prüfen.', source='Fairteiler_und_Abgabestellen'),
    dict(title='Das Verbrauchsdatum ist abgelaufen', text='Eine verschlossene Packung trägt ein überschrittenes Verbrauchsdatum. Jemand möchte sie ungeprüft mit in den Fairteiler nehmen.',
         options=['Nicht weitergeben; auch gutes Aussehen hebt das Verbrauchsdatum nicht auf.', 'Die Packung weitergeben, solange sie äußerlich unauffällig ist.'], correct=0,
         why='Lebensmittel nach dem Verbrauchsdatum dürfen nicht weitergegeben werden (Hygieneregeln B2). Das gilt auch bei persönlicher Übergabe.', source='Hygieneregeln'),
])
CHANNELS = {'personal': 'Persönliche Übergabe', 'basket': 'Essenskorb mit Abholabsprache', 'fairteiler': 'Fairteiler am Bezirkstreff'}
# Simplified item types in this game: prepared meals are only handed over personally.
PREPARED = {'salad', 'soup', 'cake'}


def ensure(r):
    import rogue as game
    r.setdefault('hygiene_log', [])
    r.setdefault('distribution_log', [])
    r.setdefault('basket', None)
    for obj in r['inventory']:
        obj.setdefault('cold_chain_ok', not (game.ITEMS[obj['key']].get('cold') and obj['age'] > 0))


def briefing(r):
    # Does not advance the encounter RNG when the page is viewed.
    option = r['options'][r['pending_route']]
    return BRIEFINGS[(option['venue'] + r['day'] + r['step']) % len(BRIEFINGS)]


def finish_briefing(r, response, papers, notes, containers, hands):
    import rogue as game
    if r['phase'] != 'briefing':
        return False
    data = briefing(r)
    if not all((papers, notes, containers, hands)):
        r['briefing_feedback'] = 'Prüfe erst Ausweis, Absprachen, Behälter und den hygienischen Umgang mit Backwaren.'
        return False
    if response != data['correct']:
        r['briefing_feedback'] = data['why'] + ' Du kannst deine Entscheidung korrigieren; ein Lernversuch ist keine Regelverletzung.'
        return False
    r['briefing_feedback'] = None
    r['last_check'] = None
    game.note(r, data['title'] + ': Absprachen geprüft. ' + data['why'])
    game.begin_encounter(r, r['options'][r['pending_route']])
    return True


def reserved(r, uid):
    return r.get('basket') is not None and uid in r['basket']['uids']


def eligibility(r, obj, channel, refrigerated=True, for_basket=False):
    import rogue as game
    data = game.ITEMS[obj['key']]
    if data['kind'] != 'food':
        return False, 'Kein Lebensmittel zur Fairteilung.'
    if reserved(r, obj['uid']) and not for_basket:
        return False, 'Für deinen Essenskorb reserviert.'
    if game.freshness(r, obj) <= 0:
        return False, 'Im Spiel nicht mehr genießbar; keine Weitergabe.'
    if data.get('cold') and not obj.get('cold_chain_ok', True):
        return False, 'Längere Unterbrechung der Kühlkette im Spiel; auch nicht persönlich weitergeben.'
    if channel == 'fairteiler':
        if obj['key'] in PREPARED or data.get('personal_only'):
            return False, 'Zubereitete warme/kühlbedürftige Speisen: hier nur persönliche Übergabe.'
        if data.get('cold'):
            if not refrigerated:
                return False, 'An diesem Ort gibt es keinen Kühlschrank.'
            if not any(entry['day'] == r['day'] for entry in r.get('hygiene_log', [])):
                return False, 'Erst Kühlschranktemperatur kontrollieren und Hygieneplan führen.'
    return True, 'Geeignet im vereinfachten Spielmodell; Genießbarkeit vor Übergabe prüfen.'


def maintain(r):
    import rogue as game
    ensure(r)
    if r['phase'] != 'map' or any(e['day'] == r['day'] for e in r['hygiene_log']):
        return False
    # A fixed, known scenario, not a live food-temperature measurement.
    r['hygiene_log'].append(dict(day=r['day'], temperature=5, cleaned=True))
    game.note(r, 'Fairteiler kontrolliert: fiktive Messung 5 °C; ungeeignete Ware entfernt, bei Bedarf gereinigt und im Hygieneplan dokumentiert.')
    game.tick(r)
    return True


def _selected(r, uids):
    ids = list(uids)
    if not ids or len(ids) != len(set(ids)):
        return []
    objects = [obj for obj in r['inventory'] if obj['uid'] in ids]
    return objects if len(objects) == len(ids) else []


def transfer(r, uids, channel, checked, conversation):
    import rogue as game
    ensure(r)
    if r['phase'] != 'map' or channel not in ('personal', 'fairteiler') or not checked:
        return False
    if channel == 'personal' and not conversation:
        return False
    objects = _selected(r, uids)
    if not objects or not all(eligibility(r, o, channel)[0] for o in objects):
        return False
    _handover(r, objects, channel)
    game.tick(r)
    return True


def _handover(r, objects, channel):
    import rogue as game
    names = [game.ITEMS[o['key']]['name'] for o in objects]
    for obj in objects:
        r['inventory'].remove(obj)
    r.setdefault('fairteiler_shared', r['shared'])
    r['shared'] += len(objects)
    if channel == 'fairteiler':
        r['fairteiler_shared'] += len(objects)
    r['hp'] += 5 * len(objects)
    r['distribution_log'].append(dict(day=r['day'], channel=channel, names=names))
    game.note(r, CHANNELS[channel] + ': ' + ', '.join(names) + '. Kostenlos und bedingungslos weitergegeben; RPG-Bonus +5 Kraft je Posten.')


def create_basket(r, uids, checked):
    import rogue as game
    ensure(r)
    if r['phase'] != 'map' or r['basket'] or not checked:
        return False
    objects = _selected(r, uids)
    if not objects or not all(eligibility(r, o, 'personal')[0] for o in objects):
        return False
    r['basket'] = dict(uids=list(uids), ready_turn=r['turn'] + 2)
    game.note(r, 'Fiktiven Essenskorb angelegt: Lebensmittel bleiben bis zur Abholung reserviert in deinem Rucksack. Es wurde nichts auf foodsharing.de veröffentlicht.')
    game.tick(r)
    return True


def wait_for_basket(r):
    import rogue as game
    if r['phase'] != 'map' or not r.get('basket') or r['turn'] >= r['basket']['ready_turn']:
        return False
    game.tick(r)
    return True


def deliver_basket(r, checked, conversation):
    import rogue as game
    ensure(r)
    if r['phase'] != 'map' or not r['basket'] or r['turn'] < r['basket']['ready_turn'] or not checked or not conversation:
        return False
    objects = _selected(r, r['basket']['uids'])
    if not objects or not all(eligibility(r, o, 'personal', for_basket=True)[0] for o in objects):
        return False
    _handover(r, objects, 'basket')
    r['basket'] = None
    game.tick(r)
    return True


def cancel_basket(r):
    import rogue as game
    if r['phase'] != 'map' or not r.get('basket'):
        return False
    r['basket'] = None
    game.note(r, 'Fiktiven Essenskorb zurückgenommen; die Lebensmittel sind nicht länger reserviert.')
    return True
