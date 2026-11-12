"""Optional, fictional cleanup rounds at agreed collection points."""
import rpg
import physiology

BINS = {
    'paper': dict(name='Blauer Papiercontainer', icon='📦', text='Am Treff soll der freigegebene Sammelplatz aufgeräumt werden. Zwischen trockenen Kartons liegt bereitgestelltes Verpackungsmaterial.', stat='insight', dc=12, dirt=14, dust=8, odor=0, loot=['labels','clip_folder','cotton_gloves','repair_tape','clean_towel']),
    'recycling': dict(name='Gelbe Wertstofftonne', icon='♻️', text='Hannes zeigt dir die leeren Verpackungen für die Sortieraktion. Sauberes Ersatzmaterial liegt daneben in einer gekennzeichneten Spendenbox.', stat='insight', dc=13, dirt=24, dust=3, odor=6, loot=['garbage_bags','carabiners','sorting_board','vinyl_gloves','tool_belt']),
    'residual': dict(name='Graue Restmülltonne', icon='🗑️', text='Die Umgebung der Tonne muss gereinigt werden. Aus dem Materialschrank gibt es dafür zurückgelegte Ausrüstung; Lebensmittel werden hier nicht geborgen.', stat='strength', dc=15, dirt=40, dust=7, odor=18, loot=['rubber_gloves','cleaning_wipes','work_boots','sorting_rake','repair_kit']),
    'organic': dict(name='Braune Biotonne', icon='🍂', text='Nele bittet um Hilfe am Kompostplatz. Die organischen Reste bleiben dort; als Dank stellt das Team Ersatzmaterial für weitere Touren bereit.', stat='strength', dc=14, dirt=35, dust=2, odor=26, loot=['dish_gloves','wash_kit','rubber_gloves','rain_boots','garbage_bags']),
    'glass': dict(name='Altglas-Sammelplatz', icon='🫙', text='Die vorgesehene Aufgabe ist das Aufräumen des Umfelds. Nicht in den Container greifen. Das nutzbare Material steht in einer separaten, freigegebenen Kiste.', stat='dexterity', dc=15, dirt=20, dust=10, odor=0, loot=['cut_gloves','work_boots','reflector_strap','headlamp','repair_tape']),
    'roll': dict(name='Große Rolltonne am Hof', icon='🛞', text='Die leere Rolltonne muss an ihren vereinbarten Platz. Der Hof ist eng, die Griffe sind rau. Robin gibt dir danach Material aus der Spende mit.', stat='strength', dc=16, dirt=20, dust=4, odor=8, loot=['grip_gloves','folding_trolley','cargo_crate','tool_belt','stretch_card']),
    'textile': dict(name='Textil-Sammelstelle', icon='🧥', text='Bei der abgesprochenen Sortierschicht am Treff werden freigegebene Textilien geordnet. Waschbare Ausrüstung ist fürs Team zurückgelegt.', stat='insight', dc=12, dirt=10, dust=14, odor=3, loot=['fleece','raincoat','cycling_gloves','bandana','cargo_vest']),
    'workshop': dict(name='Materialtonne der Radwerkstatt', icon='🔧', text='Die Werkstatt trennt ihren Materialbestand. Du sortierst die ausdrücklich freigegebenen Teile; der Rest bleibt bei der Werkstatt.', stat='dexterity', dc=14, dirt=26, dust=12, odor=5, loot=['repair_kit','bike_panniers','bike_shoes','carabiners','spare_filters']),
}


def choose(r, key):
    import rogue as game
    if r['phase'] != 'map' or key not in BINS or (r['day'] == 5 and r['step'] == 3):
        return False
    game.tick(r)
    if r['phase'] == 'dead':
        return False
    begin(r, key)
    return True


def begin(r, key=None):
    r['bin_key'] = key or r['rng'].choice(list(BINS))
    r['phase'] = 'bins'
    r['last_check'] = None
    r['bin_loot'] = []
    r['bin_result'] = ''


def preview(r):
    data = BINS[r['bin_key']]
    return rpg.preview(r, data['stat'], data['dc'])


def resolve(r):
    import rogue as game
    if r['phase'] != 'bins':
        return False
    physiology.ensure(r)
    data = BINS[r['bin_key']]
    spec = preview(r)
    protection = {key: physiology.bonus(r, key) for key in ('handling','dust_guard','odor_guard','grip')}
    game.tick(r)
    if r['phase'] == 'dead':
        return False
    passed = rpg.resolve(r, spec)
    dirt = max(0, data['dirt'] - protection['handling'])
    odor = max(0, data['odor'] - protection['odor_guard'])
    strain = max(0, data['dust'] - protection['dust_guard']) + (0 if passed else max(2, 12-protection['grip']))
    r['hygiene'] = max(0, r['hygiene'] - dirt)
    r['nausea'] = min(100, r['nausea'] + odor)
    r['hp'] -= strain
    r['bin_loot'] = r['rng'].sample(data['loot'], 2) if passed else []
    r['bin_result'] = f"{'Sortierrunde gelungen' if passed else 'Materialsuche abgebrochen'}: −{dirt} Hygiene, +{odor} Übelkeit, −{strain} Kraft."
    game.note(r, data['name'] + ': ' + r['bin_result'])
    game.note(r, rpg.summary(r['last_check']))
    r['phase'] = 'bin_loot'
    game.check_end(r)
    return True


def take(r, index):
    import rogue as game
    if r['phase'] != 'bin_loot' or index not in range(len(r['bin_loot'])):
        return False
    key = r['bin_loot'][index]
    if game.weight(r) + game.ITEMS[key]['weight'] > game.stats(r)['capacity']:
        return False
    game.add_item(r, key)
    r['bin_loot'].pop(index)
    game.note(r, 'Freigegebenes Material mitgenommen: ' + game.ITEMS[key]['name'])
    return True


def leave(r):
    import rogue as game
    if r['phase'] not in ('bins','bin_loot'):
        return False
    r['bin_loot'] = []
    game.advance(r)
    return True
