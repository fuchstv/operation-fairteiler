"""Fictional district relationships, accountability and BOTS requests."""
INCIDENTS = {
    'cold': dict(title='Die zusätzliche Tortenschachtel', text='Jo kommt dir nach: „Die hier stand seit dem Nachmittag draußen. Kann die noch in den Fairteiler?“ Du weißt, dass die Kühlkette unterbrochen war.', good='Nicht über den Fairteiler weitergeben', bad='Trotzdem für den Fairteiler einpacken', rule='Kühlpflichtige Lebensmittel mit unterbrochener Kühlkette sind von der nicht-persönlichen Weitergabe ausgeschlossen, auch über einen Fairteiler.', source='Hygieneregeln', item='cake'),
    'sorting': dict(title='Die Kiste unter der Plane', text='Cem zeigt auf eine zweite Kiste. Einige Früchte sind sichtbar schimmelig. „Schafft ihr die noch?“ Für diese Ladung ist noch nichts geprüft.', good='Die zusätzliche Kiste Stück für Stück prüfen', bad='Ungeprüft für die Weitergabe einpacken', rule='Vor der Weitergabe jedes Stück auf Genießbarkeit prüfen; Schimmeliges nicht weitergeben.', source='Hygieneregeln', item='apple'),
    'handoff': dict(title='Ein Abholtermin ohne Ersatz', text='Robin, die betriebsverantwortliche Person, ruft an: Für die zusätzliche Abholung, die du übernommen hast, müsstest du jetzt am anderen Ende des Bezirks sein. Du wirst es nicht rechtzeitig schaffen.', good='Aus dem Termin austragen, im Betriebsteam Ersatz suchen und BV anrufen', bad='Die zusätzliche Abholung kommentarlos ausfallen lassen', rule='Wer einen Abholtermin nicht wahrnehmen kann, trägt sich unverzüglich aus und sucht im Betriebsteam Ersatz. Bei weniger als 24 Stunden Vorlauf auch telefonisch suchen und im Notfall eine*n BV telefonisch informieren.', source='Verhaltensregeln', item=None),
}
REQUESTS = {
    'supply': dict(title='Lebensmittel für den Fairteiler', text='Hannes kümmert sich um den Fairteiler am Bezirkstreff. Bringe drei geeignete Lebensmittelposten zur kostenlosen Weitergabe vorbei.', target=3, counter='fairteiler_shared', reward='cooler'),
    'round': dict(title='Absprachen im Betriebsteam', text='Robin sammelt die Rückmeldungen aus den Betriebsteams. Schließe drei vereinbarte Abholungen bei kooperierenden Betrieben ab.', target=3, counter='business_pickups', reward='clipboard'),
    'care': dict(title='Erfahrungsaustausch beim Bezirkstreffen', text='Sam lädt zum Erfahrungsaustausch ein. Kläre zwei schwierige Abholsituationen regelkonform und bring deine Erfahrungen ein.', target=2, counter='responsible_choices', reward='medkit'),
}


def ensure(r):
    for key, value in dict(trust=50, fairteiler_shared=r.get('shared', 0), business_pickups=0, responsible_choices=0, violations=[], claimed=[], supported_days=[], standing={}).items():
        r.setdefault(key, value)


def adjust(r, amount):
    r['trust'] = max(0, min(100, r['trust'] + amount))


def completed_pickup(r):
    ensure(r)
    if r['encounter']['kind'] == 'business':
        r['business_pickups'] += 1
        venue = r['encounter']['venue']
        r['standing'][venue] = r['standing'].get(venue, 0) + 1
        adjust(r, 2)


def begin_incident(r):
    ensure(r)
    if r['encounter']['kind'] != 'business' or r['enemy']['boss'] or r['business_pickups'] % 2:
        return False
    venue = r['encounter']['venue']
    r['incident'] = 'cold' if venue in (2, 3) else 'sorting' if venue in (1, 5, 7) else 'handoff'
    r['phase'] = 'incident'
    r['last_check'] = None
    return True


def incident_choice(r, choice):
    import rogue as game
    import rpg
    if r['phase'] != 'incident' or choice not in ('good', 'bad', 'ask'):
        return
    ensure(r)
    data = INCIDENTS[r['incident']]
    if choice == 'bad':
        r['violations'].append(dict(title=data['title'], rule=data['rule'], day=r['day'], resolved=False))
        adjust(r, -15)
        r['energy'] = min(100, r['energy'] + 10)
        game.note(r, data['title'] + ': Regelverletzung im Spiel. +10 Energie, −15 Zusammenhalt (Spielwert). ' + ('Robin verhindert die ungeprüfte Weitergabe und sucht das persönliche Gespräch.' if data['item'] else 'Robin informiert das Betriebsteam über den ausgefallenen Abholtermin und sucht das persönliche Gespräch.'))
    else:
        if choice == 'ask':
            passed = rpg.resolve(r, rpg.preview(r, 'presence', 13))
            game.note(r, rpg.summary(r['last_check']))
            cost = 2 if passed else 8
        else:
            cost = 5
        r['energy'] = max(0, r['energy'] - cost)
        r['responsible_choices'] += 1
        adjust(r, 5)
        game.note(r, data['title'] + f': verantwortungsvoll geklärt. −{cost} Energie, +5 Zusammenhalt (Spielwert).')
    game.advance(r)


def support(r):
    import rogue as game
    ensure(r)
    if r['phase'] != 'map' or r['trust'] < 40 or r['day'] in r['supported_days']:
        return False
    r['supported_days'].append(r['day'])
    r['hp'] += 12
    r['water'] = min(100, r['water'] + 30)
    r['energy'] = min(100, r['energy'] + 20)
    game.tick(r)
    game.note(r, 'Robin organisiert mit dem Betriebsteam eine Vertretung: +12 Kraft, +30 Wasser, +20 Energie vor den Kosten einer Runde. Für diesen Abholtag einmalig.')
    return True


def repair(r, index):
    import rogue as game
    ensure(r)
    if r['phase'] != 'map' or index not in range(len(r['violations'])) or r['energy'] < 11:
        return False
    violation = r['violations'][index]
    if violation['resolved']:
        return False
    violation['resolved'] = True
    r['energy'] -= 8
    adjust(r, 7)
    game.tick(r)
    game.note(r, violation['title'] + ': im persönlichen Gespräch besprochen und Vorgehen für die nächste Abholung geklärt. +7 Zusammenhalt (Spielwert); die persönliche Gesprächsnotiz bleibt im Spieltagebuch.')
    return True


def claim(r, key):
    import rogue as game
    ensure(r)
    if r['phase'] != 'map' or key not in REQUESTS or key in r['claimed']:
        return False
    request = REQUESTS[key]
    if r[request['counter']] < request['target']:
        return False
    reward = request['reward']
    if game.weight(r) + game.ITEMS[reward]['weight'] > game.stats(r)['capacity']:
        return False
    r['claimed'].append(key)
    game.add_item(r, reward)
    adjust(r, 5)
    game.note(r, request['title'] + ': Rückmeldung gegeben; Material für weitere Abholungen bereitgestellt. ' + game.ITEMS[reward]['name'] + ' erhalten; +5 Zusammenhalt (Spielwert).')
    return True
