"""Deterministic, turn-based roguelike rules; no Streamlit dependency."""
import random
import rpg
import community
import foodsharing
from narrative import ENCOUNTERS, FINAL, EVENTS


from catalog import ITEMS, SLOTS, FOOD_POOLS
import physiology

BUSINESSES = [
    ('Krumme Kruste', '🥖', ['bread', 'pretzel', 'banana'], 'Der Ofen ist aus. Die Brotkörbe sind es nicht.'),
    ('Cems Stand am Kanal', '🥕', ['carrot', 'apple', 'berries'], 'Kistenweise krummes Gemüse wartet auf ein zweites Leben.'),
    ('Nahkauf an der Schleuse', '🛒', ['yogurt', 'cheese', 'banana'], 'Die Kühltheke brummt. Im Lager raschelt etwas.'),
    ('Café an der Drehbrücke', '☕', ['cake', 'espresso', 'pretzel'], 'Feierabend. Noch eine Torte und viel zu viel Espresso.'),
    ('Werkskantine am Nordtor', '🍲', ['soup', 'salad', 'bread'], 'Die Essensausgabe endet. Die Formularausgabe beginnt.'),
    ('Neles Hofverkauf', '🚜', ['apple', 'carrot', 'chili'], 'Der Traktor steht quer. Dahinter liegen die Gemüsekisten.'),
    ('Backstube am Gleis 4', '🥨', ['pretzel', 'bread', 'juice'], 'Gleisänderung! Auch deine Rettungstour nimmt einen Umweg.'),
    ('Iris’ Laden an der Ecke', '🌿', ['berries', 'cheese', 'salad'], 'Ein handgeschriebenes Schild: Auch krumme Karotten haben Würde.'),
]
BUSINESSES = [(name, icon, FOOD_POOLS[i], ENCOUNTERS[i]['opening'])
              for i, (name, icon, foods, _) in enumerate(BUSINESSES)]


def make_run(seed=42):
    r = dict(seed=seed, rng=random.Random(seed), phase='creation', day=1, step=0, turn=0,
             hp=100, energy=85, water=85, fullness=20, nausea=0, xp=0, level=1,
             rescued=0, shared=0, wins=0, inventory=[], equipped={}, serial=0,
             log=['Die fünftägige Rettungstour beginnt.'], options=[], enemy=None, loot=[], combat=[], guarded=False)
    for key in ['baguette', 'apron', 'tote', 'water', 'tea', 'bandage', 'banana', 'bread']:
        uid = add_item(r, key)
        if ITEMS[key]['kind'] in SLOTS:
            r['equipped'][ITEMS[key]['kind']] = uid
    for key in ('cotton_gloves','cloth_mask','soap'):
        add_item(r, key)
    r['attributes'], r['attribute_dice'] = rpg.roll_attributes(seed)
    community.ensure(r)
    foodsharing.ensure(r)
    physiology.ensure(r)
    r.update(rerolls=0, character_name='Alex', background=None, last_check=None)
    make_options(r)
    return r


def reroll_character(r):
    if r['phase'] == 'creation' and r['rerolls'] < 2:
        r['rerolls'] += 1
        r['attributes'], r['attribute_dice'] = rpg.roll_attributes(r['seed'], r['rerolls'])


def confirm_character(r, name='Alex', background='Radkurier*in'):
    if r['phase'] != 'creation' or background not in rpg.BACKGROUNDS:
        return
    attribute = rpg.BACKGROUNDS[background][0]
    r['attributes'][attribute] += 2
    r.update(character_name=name.strip()[:30] or 'Alex', background=background, phase='map')
    note(r, f"{r['character_name']} übernimmt als {background} die Runde.")


def add_item(r, key):
    r['serial'] += 1
    obj = dict(uid=r['serial'], key=key, age=0, cold_chain_ok=True)
    if 'durability' in ITEMS[key]:
        obj['durability'] = ITEMS[key]['durability']
    r['inventory'].append(obj)
    return r['serial']


def stats(r):
    result = dict(attack=7 + 2 * (r['level'] - 1), defense=0, capacity=18, cooling=0)
    muscle = rpg.modifier(r.get('attributes', {}).get('strength', 10))
    result['capacity'] += muscle * 2
    for key in result:
        result[key] += physiology.bonus(r, key)
    return result


def weight(r):
    return sum(ITEMS[o['key']]['weight'] for o in r['inventory'])


def note(r, message):
    r['log'].append(message)
    r['log'] = r['log'][-80:]


def tick(r):
    physiology.ensure(r)
    round_stats = stats(r)
    energy_save = physiology.bonus(r, 'energy_save')
    digestion_bonus = physiology.bonus(r, 'digestion')
    r['turn'] += 1
    r['energy'] = max(0, r['energy'] - max(1, 3 - energy_save))
    r['water'] = max(0, r['water'] - 3)
    r['fullness'] = max(0, r['fullness'] - 5)
    r['nausea'] = max(0, r['nausea'] - 2)
    for obj in r['inventory']:
        if ITEMS[obj['key']].get('cold') and not round_stats['cooling']:
            obj['cold_chain_ok'] = False
        obj['age'] += (1 / 3 if ITEMS[obj['key']].get('cold') and round_stats['cooling'] else 1)
    physiology.tick(r, digestion_bonus)
    if not r['energy'] or not r['water']:
        r['hp'] -= 6
        note(r, 'Erschöpfung oder Durst: −6 HP.')
    if r['nausea'] >= 70:
        r['hp'] -= 5
        note(r, 'Magenkrämpfe: −5 HP. Tee oder Pause könnten helfen.')
    if weight(r) > round_stats['capacity']:
        r['energy'] = max(0, r['energy'] - 5)
        note(r, 'Überladen: zusätzlich −5 Energie.')
    check_end(r)


def check_end(r):
    r['hp'] = min(100 + (r['level'] - 1) * 8, r['hp'])
    if r['hp'] <= 0:
        r['hp'] = 0
        r['phase'] = 'dead'
        note(r, 'Dein Run endet. Die nächste Route wird anders.')


def freshness(r, obj):
    data = ITEMS[obj['key']]
    age = obj['age']
    remaining = data.get('shelf', 999) - age
    return 0 if remaining < 1e-9 else remaining


def equip(r, uid):
    if r['phase'] != 'map':
        return
    obj = next((o for o in r['inventory'] if o['uid'] == uid), None)
    physiology.ensure(r)
    if obj and ITEMS[obj['key']]['kind'] in SLOTS:
        r['equipped'][ITEMS[obj['key']]['kind']] = uid
        note(r, ITEMS[obj['key']]['name'] + ' angelegt.')


def unequip(r, slot):
    if r['phase'] != 'map' or slot not in r['equipped']:
        return False
    del r['equipped'][slot]
    note(r, SLOTS.get(slot, slot) + ' freigemacht.')
    return True


def consume(r, uid):
    if r['phase'] not in ('map', 'combat'):
        return False
    obj = next((o for o in r['inventory'] if o['uid'] == uid), None)
    if not obj or foodsharing.reserved(r, uid):
        return False
    data = ITEMS[obj['key']]
    if data['kind'] not in ('food', 'consumable'):
        return False
    physiology.ensure(r)
    energy = data.get('energy', 0)
    if data['kind'] == 'food':
        energy = physiology.eat(r, obj, data, freshness(r, obj) == 0)
    else:
        r['nausea'] = max(0, min(100, r['nausea'] + data.get('nausea', 0)))
        physiology.apply_supply(r, data)
    r['hp'] += data.get('heal', 0)
    r['energy'] = min(100, r['energy'] + energy)
    r['water'] = min(100, r['water'] + data.get('water', 0))
    r['inventory'].remove(obj)
    note(r, data['name'] + ' verbraucht.')
    round_defense = stats(r)['defense']
    tick(r)
    if r['phase'] == 'combat':
        enemy_turn(r, defense=round_defense)
    check_end(r)
    return True


def drop(r, uid):
    if r['phase'] != 'map' or uid in r['equipped'].values() or foodsharing.reserved(r, uid):
        return
    r['inventory'] = [o for o in r['inventory'] if o['uid'] != uid]


def make_options(r):
    if r['day'] == 5 and r['step'] == 3:
        r['options'] = [dict(kind='business', venue=4, danger=3)]
        return
    venues = r['rng'].sample(range(len(BUSINESSES)), 2)
    r['options'] = [dict(kind='business', venue=v, danger=r['rng'].randint(1, 3)) for v in venues]
    r['options'].append(dict(kind=r['rng'].choice(['camp', 'event', 'arena', 'bins']), danger=1))


def visit(r, index):
    if r['phase'] != 'map' or index not in range(len(r['options'])):
        return
    option = r['options'][index]
    tick(r)
    if r['phase'] == 'dead':
        return
    kind = option['kind']
    if kind == 'camp':
        r['phase'] = 'camp'
        note(r, 'Du erreichst den Nachbarschaftstreff.')
    elif kind == 'event':
        r['phase'] = 'event'
        r['event'] = r['rng'].choice(['rain', 'crate', 'stranger'])
    elif kind == 'bins':
        import salvage
        salvage.begin(r)
    elif kind == 'business':
        r['pending_route'] = index
        r['briefing_feedback'] = None
        r['last_check'] = None
        r['phase'] = 'briefing'
    else:
        begin_encounter(r, option)


def begin_encounter(r, option):
    kind = option['kind']
    r['phase'] = 'combat'
    r['encounter'] = option
    boss = r['day'] == 5 and r['step'] == 3
    context = FINAL if boss else ENCOUNTERS[option['venue']] if kind == 'business' else None
    name = context['name'] if context else 'Abhol-Parcours am Bezirkstreff'
    if kind == 'arena' and not boss:
        name = r['rng'].choice(['Sam · Trainingspartnerin (NPC)', 'Hannes · Trainingspartner (NPC)', 'Deniz · Trainingspartner (NPC)'])
    hp = 26 + r['day'] * 9 + option['danger'] * 4 + (35 if boss else 0)
    r['enemy'] = dict(name=name, hp=hp, max_hp=hp, attack=7 + r['day'] * 2 + option['danger'], intent='attack', boss=boss, narrative=context)
    r['combat'] = [context['opening'] if context else 'Am Treff steht der Abhol-Parcours bereit. Dein Trainingspartner übernimmt die andere Bahn.']



def enemy_turn(r, defend=0, defense=None):
    e = r['enemy']
    if e['intent'] == 'recover':
        r['combat'].append(e['narrative']['recover'] if e.get('narrative') else e['name'] + ' holt Luft. Kein Gegenangriff.')
        e['intent'] = 'attack'
        return
    defense = stats(r)['defense'] if defense is None else defense
    hit = max(1, e['attack'] + r['rng'].randint(-2, 2) - defense - defend)
    r['hp'] -= hit
    r['combat'].append((e['narrative']['hit'] + f" −{hit} Kraft.") if e.get('narrative') else f"{e['name']}: {hit} Kondition verloren.")
    e['intent'] = r['rng'].choice(['attack', 'attack', 'recover'])
    check_end(r)


def combat_action(r, action):
    if r['phase'] != 'combat' or action not in ('attack', 'heavy', 'defend', 'flee'):
        return
    if action == 'heavy' and r['energy'] < 15:
        return
    if action == 'flee' and r['enemy']['boss']:
        return
    spec = rpg.action_spec(r, action)
    round_stats = stats(r)
    tick(r)
    if r['phase'] == 'dead':
        return
    passed = rpg.resolve(r, spec)
    note(r, rpg.summary(r['last_check']))
    e = r['enemy']
    if action == 'flee':
        if passed:
            note(r, 'Du gibst die Abholung ans Team zurück. Du nimmst nichts mit; diese Station endet.')
            advance(r)
            return
        r['combat'].append('Du erreichst niemanden. Noch musst du vor Ort bleiben.')
    elif action != 'defend':
        hit = round_stats['attack'] + r['rng'].randint(0, 4)
        if action == 'heavy':
            r['energy'] -= 12
            hit = int(hit * 1.8) if passed else 0
        elif not passed:
            hit = max(1, hit // 2)
        if r['nausea'] >= 50 and hit:
            hit = max(1, hit - 5)
        e['hp'] = max(0, e['hp'] - hit)
        r['combat'].append((f"Du {'packst mit voller Kraft an' if action == 'heavy' else 'arbeitest die nächste Aufgabe ab'}: −{hit} Restaufwand.") if e.get('narrative') else f'Dein Durchgang bringt {hit} Punkte Vorsprung.')
    if e['hp'] == 0:
        reward(r)
        return
    enemy_turn(r, 9 if action == 'defend' and passed else 3 if action == 'defend' else 0, defense=round_stats['defense'])
    r['combat'] = r['combat'][-8:]


def reward(r):
    community.completed_pickup(r)
    r['wins'] += 1
    r['xp'] += 12
    if r['xp'] >= r['level'] * 20:
        r['level'] += 1
        r['hp'] += 18
        note(r, f"Level {r['level']}! +18 HP und mehr Angriff.")
    option = r['encounter']
    food = FOOD_POOLS[option['venue']] if option['kind'] == 'business' else ['snack', 'water']
    # Weight rarities so exceptional drops are actually exceptional.
    pool = [key for key, data in ITEMS.items() if data['kind'] in SLOTS]
    weights = [{'Gewöhnlich': 8, 'Selten': 4, 'Episch': 2, 'Legendär': 1}[ITEMS[k]['rarity']] for k in pool]
    r['loot'] = [r['rng'].choice(food), r['rng'].choice(food), r['rng'].choices(pool, weights=weights)[0], r['rng'].choice([k for k, v in ITEMS.items() if v['kind'] == 'consumable']), 'water']
    r['phase'] = 'loot'
    note(r, r['enemy']['narrative']['done'] if r['enemy'].get('narrative') else 'Trainingsrunde gewonnen. Am Treff kannst du Material und Verpflegung mitnehmen.')


def take_loot(r, index):
    if r['phase'] != 'loot' or index not in range(len(r['loot'])):
        return False
    key = r['loot'][index]
    if weight(r) + ITEMS[key]['weight'] > stats(r)['capacity']:
        return False
    add_item(r, key)
    if ITEMS[key]['kind'] == 'food' and r['encounter']['kind'] == 'business':
        r['rescued'] += 1
    note(r, ITEMS[key]['name'] + ' eingepackt.')
    r['loot'].pop(index)
    return True


def advance(r):
    r['step'] += 1
    if r['step'] == 4:
        if r['day'] == 5:
            r['phase'] = 'victory'
            note(r, 'Freitag, kurz nach Ladenschluss. Die letzte Abholung ist unterwegs. Sam stellt am Treff die Teekanne auf.')
            return
        r['day'] += 1
        r['step'] = 0
        r['energy'] = min(100, r['energy'] + 25)
        r['water'] = min(100, r['water'] + 25)
        r['hp'] += 15
    r['phase'] = 'map'
    r['enemy'] = None
    r['loot'] = []
    make_options(r)
    check_end(r)


def finish_loot(r):
    if r['phase'] == 'loot':
        if not community.begin_incident(r):
            advance(r)


def camp(r, action):
    if r['phase'] != 'camp' or action not in ('rest', 'share'):
        return
    if action == 'share':
        # Cold food is not placed in the uncooled game Fairteiler.
        eligible = [o for o in r['inventory'] if foodsharing.eligibility(r, o, 'fairteiler', refrigerated=False)[0]]
        foodsharing.ensure(r)
        if eligible:
            foodsharing._handover(r, eligible, 'fairteiler')
        else:
            note(r, 'Für das ungekühlte Regal sind gerade keine geeigneten, unreservierten Lebensmittel dabei.')
    else:
        r['hp'] += 30
        r['energy'] = min(100, r['energy'] + 35)
        r['water'] = min(100, r['water'] + 35)
        r['nausea'] = max(0, r['nausea'] - 35)
        note(r, 'Pause: +30 HP, +35 Energie/Wasser, −35 Übelkeit.')
    advance(r)


def event(r, cautious):
    if r['phase'] != 'event':
        return
    passed = False
    if not cautious:
        passed = rpg.resolve(r, rpg.action_spec(r, 'event'))
        note(r, rpg.summary(r['last_check']))
    if cautious:
        r['energy'] = min(100, r['energy'] + 8)
        note(r, 'Du lässt den Umweg aus und verschnaufst kurz. +8 Energie.')
    elif passed:
        key = r['rng'].choice(['cooler', 'vest', 'rolling', 'medkit', 'cargo'])
        if weight(r) + ITEMS[key]['weight'] <= stats(r)['capacity']:
            add_item(r, key)
            note(r, EVENTS[r['event']]['success'] + ' Mitgenommen: ' + ITEMS[key]['name'])
        else:
            note(r, 'Der Fund bleibt zurück: dein Rucksack ist voll.')
    else:
        r['hp'] -= 15
        r['nausea'] = min(100, r['nausea'] + 10)
        note(r, EVENTS[r['event']]['failure'] + ' −15 Kraft, +10 Übelkeit.')
    check_end(r)
    if r['phase'] != 'dead':
        advance(r)


# Genuine local player-vs-player: two humans share a screen and alternate turns.
def make_duel(name_a, name_b, weapon_a='baguette', weapon_b='baguette'):
    return dict(players=[dict(name=name_a or 'Spieler 1', hp=100, weapon=weapon_a, stamina=40, potions=2, guard=False),
                         dict(name=name_b or 'Spieler 2', hp=100, weapon=weapon_b, stamina=40, potions=2, guard=False)],
                turn=0, winner=None, log=['Hotseat-Duell: Spieler 1 beginnt.'])


def duel_action(d, action):
    if d['winner'] is not None or action not in ('attack', 'heavy', 'defend', 'heal'):
        return
    turn = d['turn']
    a, b = d['players'][turn], d['players'][1-turn]
    if action == 'heavy' and a['stamina'] < 12 or action == 'heal' and not a['potions']:
        return
    a['guard'] = False
    if action == 'defend':
        a['guard'] = True
        a['stamina'] = min(40, a['stamina'] + 10)
        message = a['name'] + ' blockt und regeneriert 10 Ausdauer.'
    elif action == 'heal':
        a['potions'] -= 1
        a['hp'] = min(100, a['hp'] + 24)
        message = a['name'] + ' nutzt eine Versorgungspause: +24 Kondition.'
    else:
        damage = 8 + ITEMS[a['weapon']]['attack']
        if action == 'heavy':
            a['stamina'] -= 12
            damage = int(damage * 1.7)
        else:
            a['stamina'] = min(40, a['stamina'] + 3)
        damage = max(1, damage - (12 if b['guard'] else 0))
        b['hp'] = max(0, b['hp'] - damage)
        message = f"{a['name']} legt im Parcours vor. {b['name']} verliert {damage} Kondition."
    d['log'] = (d['log'] + [message])[-12:]
    if b['hp'] == 0:
        d['winner'] = turn
    else:
        d['turn'] = 1-turn
