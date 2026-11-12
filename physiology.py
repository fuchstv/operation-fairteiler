"""Fictional digestion, temporary effects and equipment wear. No medical model."""
from catalog import ITEMS, SLOTS


def ensure(r):
    r.setdefault('hygiene', 100)
    r.setdefault('gas', 0)
    r.setdefault('urgency', 0)
    r.setdefault('salt_load', 0)
    r.setdefault('digestion', [])
    r.setdefault('effects', {})
    r.setdefault('last_retch', -10)
    # Preserve existing gear when a saved session predates the new hand slot.
    for slot, uid in list(r['equipped'].items()):
        obj = next((o for o in r['inventory'] if o['uid'] == uid), None)
        if obj and ITEMS[obj['key']]['kind'] != slot:
            new_slot = ITEMS[obj['key']]['kind']
            if new_slot in SLOTS:
                r['equipped'].setdefault(new_slot, uid)
            del r['equipped'][slot]
    for obj in r['inventory']:
        if 'durability' in ITEMS[obj['key']]:
            obj.setdefault('durability', ITEMS[obj['key']]['durability'])


def active_equipment(r):
    for obj in r['inventory']:
        if obj['uid'] in r['equipped'].values() and obj.get('durability', 1) > 0:
            yield obj, ITEMS[obj['key']]


def bonus(r, key):
    total = sum(data.get(key, 0) for _, data in active_equipment(r))
    effect = r.get('effects', {}).get(key)
    if effect and r['turn'] < effect['until']:
        total += effect['power']
    return total


def effect(r, key, power, turns):
    # Refresh this named effect, never add copies for unlimited stacking.
    r['effects'][key] = dict(power=power, until=r['turn'] + turns + 1)


def eat(r, obj, data, spoiled):
    risk = data.get('risk', 0) + (50 if spoiled else 0)
    if data.get('cold') and not obj.get('cold_chain_ok', True):
        risk += 20
    risk += max(0, (60 - r['hygiene']) // 3)
    overload = max(0, r['fullness'] + data['fullness'] - 85)
    r['fullness'] = min(100, r['fullness'] + data['fullness'])
    r['nausea'] = min(100, r['nausea'] + risk + overload)
    r['gas'] = min(100, r['gas'] + data.get('fiber', 0) * 3)
    r['salt_load'] = min(50, r['salt_load'] + data.get('salt', 0))
    energy = data.get('energy', 0)
    immediate = energy // 3
    if energy > immediate:
        r['digestion'].append(dict(name=data['name'], energy=energy-immediate, fat=data.get('fat', 0)))
    return immediate


def apply_supply(r, data):
    r['hygiene'] = min(100, r['hygiene'] + data.get('hygiene', 0))
    r['gas'] = max(0, min(100, r['gas'] + data.get('gas', 0)))
    if data.get('effect'):
        effect(r, data['effect'], data['power'], data['turns'])
    if data.get('repair'):
        for obj in r['inventory']:
            if obj['uid'] in r['equipped'].values() and 'durability' in ITEMS[obj['key']]:
                if data.get('repair_slot') and ITEMS[obj['key']]['kind'] != data['repair_slot']:
                    continue
                obj['durability'] = min(ITEMS[obj['key']]['durability'], obj.get('durability', 0) + data['repair'])


def tick(r, digestion_bonus=0):
    import rogue as game
    ensure(r)
    # Bonuses apply to this round before expiring / equipment wearing out.
    extra_water = int(r['salt_load'] >= 10)
    r['water'] = max(0, r['water'] - extra_water)
    r['salt_load'] = max(0, r['salt_load'] - 1)
    release = 4 + max(0, digestion_bonus)
    absorbed = 0
    if r['digestion']:
        meal = r['digestion'][0]
        amount = min(meal['energy'], max(1, release - int(meal['fat'] >= 5)))
        meal['energy'] -= amount
        absorbed += amount
        r['urgency'] = min(100, r['urgency'] + 3)
        if meal['energy'] <= 0:
            r['digestion'].pop(0)
    r['energy'] = min(100, r['energy'] + absorbed)
    r['gas'] = max(0, r['gas'] - 2)
    if r['gas'] >= 60:
        r['nausea'] = min(100, r['nausea'] + 2)
    if r['urgency'] >= 80:
        r['energy'] = max(0, r['energy'] - 2)
    if r['nausea'] >= 90 and r['fullness'] > 0 and r['turn'] - r['last_retch'] >= 4:
        r['fullness'] = max(0, r['fullness'] - 30)
        r['water'] = max(0, r['water'] - 12)
        r['nausea'] = max(0, r['nausea'] - 20)
        r['last_retch'] = r['turn']
        game.note(r, 'Der Spielmagen rebelliert: −30 Füllung, −12 Wasser, −20 Übelkeit. Zeit für eine Pause.')
    for obj, data in list(active_equipment(r)):
        if 'durability' in data:
            obj['durability'] = max(0, obj['durability'] - 1)
            if obj['durability'] == 0:
                game.note(r, data['name'] + ' ist verschlissen. Boni sind bis zur Reparatur ausgesetzt.')
    r['effects'] = {key: value for key, value in r['effects'].items() if value['until'] > r['turn']}


def wash(r):
    import rogue as game
    ensure(r)
    if r['phase'] != 'map' or r['water'] < 8 or r['hygiene'] == 100:
        return False
    r['water'] -= 5
    r['hygiene'] = 100
    game.note(r, 'Hände am Waschplatz gewaschen: Hygiene 100, −5 Wasser plus eine Runde.')
    game.tick(r)
    return True


def restroom(r):
    import rogue as game
    ensure(r)
    if r['phase'] != 'map' or not (r['urgency'] or r['gas'] or r['nausea']):
        return False
    r['urgency'] = 0
    r['gas'] = max(0, r['gas'] - 25)
    r['nausea'] = max(0, r['nausea'] - 10)
    game.note(r, 'Toilettenpause eingelegt: Drang 0, −25 Bauchgas, −10 Übelkeit; eine Runde.')
    game.tick(r)
    return True
