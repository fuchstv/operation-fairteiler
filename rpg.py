"""Character rolls and transparent d20 checks, shared by rules and UI."""
import random
import physiology

ATTRIBUTES = {'strength': 'Muskelkraft', 'dexterity': 'Geschick', 'insight': 'Übersicht', 'presence': 'Auftreten'}
BACKGROUNDS = {'Radkurier*in': ('dexterity', 'Enger Durchgang, voller Gepäckträger: Du bleibst beweglich.'),
               'Lagercrew': ('strength', 'Du weißt, wo man eine Kiste greift und wann man Hilfe braucht.'),
               'Schichtkoordination': ('insight', 'Du behältst Zeiten, Behälter und Abgabeorte im Blick.'),
               'Nachbarschaftsarbeit': ('presence', 'Du kennst die Leute und findest die richtigen Worte.')}
VENUE_STATS = ['dexterity', 'insight', 'insight', 'dexterity', 'insight', 'strength', 'dexterity', 'presence']
TOOL_BONUSES = {'tongs': ('dexterity', 2), 'clipboard': ('insight', 2), 'rolling': ('strength', 2),
                'ladle': ('dexterity', 1), 'leek': ('strength', 1), 'stamp': ('strength', 3)}


def roll_attributes(seed, attempt=0):
    rng = random.Random(f'character:{seed}:{attempt}')
    rolls = {key: [rng.randint(1, 6) for _ in range(4)] for key in ATTRIBUTES}
    return {key: sum(sorted(dice)[1:]) for key, dice in rolls.items()}, rolls


def modifier(value):
    return (value - 10) // 2


def chance(bonus, dc):
    # A natural 1 always fails; a natural 20 always succeeds.
    return sum(face == 20 or (face != 1 and face + bonus >= dc) for face in range(1, 21)) * 5


def preview(r, attribute, dc):
    base = modifier(r.get('attributes', {}).get(attribute, 10))
    tool = 0
    for obj in r['inventory']:
        if obj['uid'] == r['equipped'].get('weapon') and obj.get('durability', 1) > 0:
            stat, amount = TOOL_BONUSES.get(obj['key'], (None, 0))
            if stat == attribute:
                tool = amount
    equipment = physiology.bonus(r, attribute)
    fatigue = -2 if r['energy'] < 25 else 0
    stomach = -2 if r['nausea'] >= 50 else 0
    community_bonus = (1 if r.get('trust', 50) >= 70 else -1 if r.get('trust', 50) < 25 else 0) if attribute == 'presence' else 0
    bonus = base + tool + fatigue + stomach + community_bonus + equipment
    return dict(attribute=attribute, dc=dc, base=base, tool=tool, fatigue=fatigue, stomach=stomach,
                community=community_bonus, equipment=equipment, bonus=bonus, chance=chance(bonus, dc))


def resolve(r, spec):
    # Resolve exactly the displayed snapshot, before this action's resource costs.
    result = dict(spec)
    result['roll'] = r['rng'].randint(1, 20)
    result['total'] = result['roll'] + result['bonus']
    result['success'] = result['roll'] == 20 or (result['roll'] != 1 and result['total'] >= result['dc'])
    r['last_check'] = result
    return result['success']


def action_spec(r, action, option=None):
    option = option or r.get('encounter', {})
    danger = option.get('danger', 1)
    if action == 'attack':
        stat = VENUE_STATS[option['venue']] if option.get('kind') == 'business' else 'dexterity'
        familiarity = 1 if option.get('kind') == 'business' and r.get('standing', {}).get(option['venue'], 0) >= 2 else 0
        return preview(r, stat, 10 + danger - familiarity)
    if action == 'heavy':
        return preview(r, 'strength', 13 + danger)
    if action == 'defend':
        return preview(r, 'dexterity', 12)
    if action == 'flee':
        return preview(r, 'presence', 14)
    return preview(r, 'dexterity' if r.get('event') == 'rain' else 'strength', 14)


def summary(check):
    return (f"{ATTRIBUTES[check['attribute']]}: W20 {check['roll']} {check['bonus']:+} = {check['total']} "
            f"gegen SG {check['dc']} → {'Erfolg' if check['success'] else 'Misserfolg'}"
            + (' (natürliche 20)' if check['roll'] == 20 else ' (natürliche 1)' if check['roll'] == 1 else ''))
