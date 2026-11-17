"""Item definitions. All effects are fictional game values, not equipment ratings."""
def item(name, kind, **stats):
    return dict(name=name, kind=kind, rarity=stats.pop('rarity', 'Gewöhnlich'), weight=stats.pop('weight', 1), **stats)


ITEMS = {
    'baguette': item('Bäckerkorb mit Griffbügel', 'weapon', attack=4),
    'spatula': item('Pfannenwender', 'weapon', attack=6),
    'tongs': item('Lange Gebäckzange', 'weapon', attack=8, rarity='Selten'),
    'clipboard': item('Sams Tourenmappe', 'weapon', attack=10, rarity='Selten'),
    'rolling': item('Rollbrett vom Getränkelager', 'weapon', attack=13, rarity='Episch'),
    'ladle': item('Suppenkelle', 'weapon', attack=5),
    'leek': item('Klappbare Gemüsesteige', 'weapon', attack=7),
    'stamp': item('Hubwagen aus der Materialspende', 'weapon', attack=16, rarity='Legendär'),
    'apron': item('Schürze', 'armor', defense=2),
    'helmet': item('Fahrradhelm', 'armor', defense=4),
    'vest': item('Warnweste', 'armor', defense=5, rarity='Selten'),
    'pot': item('Gefütterte Arbeitshose', 'armor', defense=7, weight=3, rarity='Episch'),
    'raincoat': item('Regenjacke', 'armor', defense=3),
    'gloves': item('Arbeitshandschuhe mit Polsterung', 'armor', defense=6, rarity='Selten'),
    'tote': item('Jutebeutel', 'gear', capacity=5),
    'cargo': item('Lastenrad-Anhänger', 'gear', capacity=16, weight=3, rarity='Episch'),
    'cooler': item('Kühlbox', 'gear', capacity=8, cooling=1, weight=2, rarity='Selten'),
    'thermos': item('Kühlrucksack', 'gear', capacity=6, cooling=1, rarity='Selten'),
    'rack': item('Gepäckträger', 'gear', capacity=10, rarity='Selten'),
    'banana': item('Banane', 'food', energy=17, fullness=18, risk=0, shelf=12),
    'bread': item('Vollkornbrot', 'food', energy=25, fullness=30, risk=0, shelf=14),
    'apple': item('Apfel', 'food', energy=12, fullness=14, risk=0, shelf=14),
    'carrot': item('Karotte', 'food', energy=10, fullness=12, risk=0, shelf=16),
    'yogurt': item('Joghurt', 'food', energy=22, fullness=20, risk=4, shelf=5, cold=True),
    'cheese': item('Käse', 'food', energy=30, fullness=24, risk=4, shelf=7, cold=True),
    'salad': item('Kartoffelsalat', 'food', energy=28, fullness=28, risk=8, shelf=4, cold=True),
    'soup': item('Linsensuppe', 'food', energy=35, fullness=32, risk=2, shelf=5),
    'cake': item('Sahnetorte', 'food', energy=32, fullness=26, risk=8, shelf=3, cold=True),
    'chili': item('Neles rote Chili', 'food', energy=15, fullness=8, risk=28, shelf=12),
    'pretzel': item('Brezel', 'food', energy=18, fullness=18, risk=0, shelf=10),
    'berries': item('Beerenmix', 'food', energy=14, fullness=12, risk=3, shelf=5),
    'water': item('Wasserflasche', 'consumable', water=35),
    'tea': item('Fencheltee', 'consumable', nausea=-30, water=15),
    'charcoal': item('Kamillentee in der Thermoskanne', 'consumable', nausea=-45, rarity='Selten'),
    'bandage': item('Erste-Hilfe-Päckchen', 'consumable', heal=28),
    'espresso': item('Espresso', 'consumable', energy=30, nausea=8),
    'mint': item('Pfefferminzbonbon', 'consumable', nausea=-12),
    'juice': item('Apfelschorle', 'consumable', water=25, energy=10),
    'medkit': item('Großes Erste-Hilfe-Set', 'consumable', heal=50, rarity='Episch'),
    'snack': item('Notfallriegel', 'food', energy=32, fullness=12, risk=0, shelf=50, rarity='Selten'),
    'sponge': item('Pausenset vom Treff', 'consumable', heal=10, nausea=-10),
}

SLOTS = {'weapon': 'Werkzeug / Duellgerät', 'armor': 'Arbeitskleidung', 'gear': 'Transport',
         'hands': 'Hände', 'face': 'Gesicht', 'feet': 'Füße', 'belt': 'Gürtel / Zubehör'}


def add(key, name, kind, flavour, **stats):
    if key in ITEMS:
        raise ValueError('Duplicate item: ' + key)
    ITEMS[key] = item(name, kind, flavour=flavour, **stats)


# Hand protection trades dexterity, durability and fictional handling protection.
ITEMS['gloves'].update(kind='hands', durability=35, handling=16, grip=2)
add('cotton_gloves', 'Dünne Baumwollhandschuhe', 'hands', 'Aus der Materialschublade. Angenehm an trockenen Kartons, schnell durchgescheuert.', defense=1, handling=5, dexterity=1, durability=18)
add('nitrile_gloves', 'Ungepuderte Nitrilhandschuhe', 'hands', 'Ein frisches Paar aus der Schachtel. Im Spiel kurzlebig, aber wenig hinderlich.', handling=20, dexterity=1, durability=8)
add('vinyl_gloves', 'Vinylhandschuhe', 'hands', 'Für kurze, ruhige Handgriffe. An rauen Kisten sind sie bald hinüber.', handling=16, durability=6)
add('latex_gloves', 'Latexfreie Untersuchungshandschuhe', 'hands', 'Die Beschriftung der Schachtel ist deutlich. Die Packung bleibt in der Treffküche.', handling=22, dexterity=1, durability=10)
add('rubber_gloves', 'Lange Gummihandschuhe', 'hands', 'Hannes nutzt sie zum Reinigen. Vor dem Umgang mit Lebensmitteln wechseln.', handling=30, dexterity=-1, durability=30, rarity='Selten')
add('cut_gloves', 'Schnittfeste Arbeitshandschuhe', 'hands', 'Für raue Materialkisten gedacht. Sie machen dich im Spiel belastbarer, nicht unverwundbar.', defense=3, grip=3, handling=12, durability=45, rarity='Selten')
add('thermal_gloves', 'Gefütterte Thermohandschuhe', 'hands', 'Gut an der kalten Rampe; beim Greifen kleiner Etiketten eher im Weg.', defense=4, dexterity=-1, durability=40, rarity='Selten')
add('grip_gloves', 'Handschuhe mit Noppenbesatz', 'hands', 'Die Kiste rutscht weniger, die Finger bleiben beweglich.', defense=2, strength=1, grip=4, handling=10, durability=32)
add('cycling_gloves', 'Fahrradhandschuhe', 'hands', 'Gelpolster an den Handflächen. Für die lange Fahrt, nicht zum Anfassen von Backwaren.', defense=2, dexterity=1, durability=35)
add('oven_mitts', 'Lange Ofenhandschuhe', 'hands', 'Rikes Ersatzpaar. Mit den dicken Fingern findest du keinen Klebestreifenanfang.', defense=5, dexterity=-2, handling=8, durability=35, rarity='Episch')
add('dish_gloves', 'Spülhandschuhe mit Baumwollfutter', 'hands', 'Innen trocken, außen abwaschbar. Im Spiel besonders ausdauernd bei Reinigungsarbeiten.', handling=26, grip=1, durability=45, rarity='Selten')

# Masks affect only the fictional dust/odour encounters, never food eligibility.
add('cloth_mask', 'Waschbare Stoffmaske', 'face', 'Aus der Fundkiste. Der kleine Staubbonus ist eine Spielabstraktion.', dust_guard=3, durability=20)
add('surgical_mask', 'Medizinische Einwegmaske', 'face', 'Einzeln aus der Schachtel genommen. Kein Bonus gegen Gerüche im Spiel.', dust_guard=6, durability=10)
add('ffp2_mask', 'FFP2-Maske', 'face', 'Für die staubige Materialkammer. Verändert weder Kühlkette noch Genießbarkeit.', dust_guard=12, durability=24, rarity='Selten')
add('ffp3_mask', 'FFP3-Maske', 'face', 'Liegt ungeöffnet im Materialschrank. Der Schutzwert ist kein reales Prüfsiegel.', dust_guard=18, durability=28, rarity='Episch')
add('carbon_mask', 'Maske mit Aktivkohleeinlage', 'face', 'Für die Spielszene an der Biotonne: weniger Geruchsbelastung, keine Freigabe für verdorbene Ware.', dust_guard=8, odor_guard=14, durability=22, rarity='Selten')
add('half_mask', 'Halbmaske aus der Werkstatt', 'face', 'Sperrig im Gesicht. Im Spiel ein hoher Staubwert gegen etwas weniger Auftreten.', dust_guard=22, presence=-1, durability=45, weight=2, rarity='Episch')
add('face_shield', 'Gesichtsschild', 'face', 'Die Scheibe ist frisch geputzt. Hilft im Spiel gegen Spritzer, nicht gegen Gerüche.', defense=2, handling=8, durability=35)
add('bandana', 'Tuch vom Straßenfest', 'face', 'Ein vertrautes Muster; Hannes erkennt dich damit schon von weitem.', presence=1, dust_guard=1, durability=25)

for key, name, desc, stats in [
 ('rain_boots','Gummistiefel','Für den nassen Hof; auf der langen Strecke etwas schwer.',dict(defense=3,grip=2,weight=2)),
 ('work_boots','Arbeitsschuhe mit fester Sohle','Robin hat die passende Größe in der Materialspende gefunden.',dict(defense=4,grip=3,weight=2,rarity='Selten')),
 ('trainers','Eingelaufene Turnschuhe','Leicht genug für die Bahnhofsrunde.',dict(dexterity=1,energy_save=1)),
 ('bike_shoes','Feste Radschuhe','Die Pedale fühlen sich weniger rutschig an.',dict(grip=2,energy_save=1,rarity='Selten')),
 ('hiking_boots','Wanderschuhe','Für Hofzufahrt und Kopfsteinpflaster.',dict(defense=2,grip=4,weight=2)),
 ('overshoes','Wasserdichte Überschuhe','Über die Schuhe gezogen, bevor der Regen richtig anfängt.',dict(defense=2,handling=4,durability=25)),
 ('safety_boots','Hohe Lagerstiefel','Schwer, aber auf der Rampe angenehm stabil.',dict(defense=5,grip=4,dexterity=-1,weight=3,rarity='Episch')),
 ('sandals','Treckingsandalen','Bequem auf trockenem Asphalt, kaum Entlastung beim Schleppen.',dict(energy_save=1,defense=1)),
]: add(key,name,'feet',desc,**stats)

for key, name, desc, stats in [
 ('headlamp','Stirnlampe','Du liest die Beschriftung auch hinter dem Rollregal.',dict(insight=1,dust_guard=1)),
 ('labels','Etikettenhalter am Gürtel','MHD und Abgabeort bleiben auf getrennten Zetteln.',dict(insight=2)),
 ('phone_mount','Handyhalter mit Tourenplan','Die letzte Nachricht aus dem Betriebsteam ist griffbereit.',dict(presence=1,insight=1)),
 ('tool_belt','Werkzeuggürtel','Die Zange liegt endlich nicht mehr unter dem Brot.',dict(capacity=3,attack=1)),
 ('carabiners','Karabinerleiste','Nur für Taschen und Handschuhe; kein Klettergerät.',dict(capacity=2,dexterity=1)),
 ('lumbar_belt','Gepolsterter Tragegurt','Im Spiel weniger Kraftverlust beim Schleppen.',dict(defense=3)),
 ('reflector_strap','Reflektorband vom Treff','Die Materialcrew kennt den Aufdruck.',dict(presence=1,defense=1)),
 ('thermometer','Digitales Kühlthermometer','Hilft beim Planen; ersetzt keinen Eintrag im Hygieneplan.',dict(insight=2,rarity='Selten')),
]: add(key,name,'belt',desc,**stats)

for key, name, desc, stats in [
 ('dough_scraper','Teigschaber mit Holzgriff','Ute hat die Kante glatt geschliffen.',dict(attack=5,dexterity=1)),
 ('crate_hook','Kistenhaken','Für die vorgesehenen Griffe an den Leerkisten.',dict(attack=9,strength=1)),
 ('folding_trolley','Klappbare Sackkarre','Eine Fahrt statt drei, wenn die Ladung passt.',dict(attack=11,strength=1,weight=2,rarity='Selten')),
 ('platform_trolley','Plattformwagen','Rikes Wagen darf nur im Hof bleiben. Im Spiel ein besonders kräftiges Werkzeug.',dict(attack=15,weight=3,dexterity=-1,rarity='Episch')),
 ('sorting_board','Sortierbrett','Saubere Fläche statt aufgerissener Karton.',dict(attack=7,insight=1)),
 ('portion_scoop','Portionierlöffel','Gleichmäßige Portionen für die Küfa.',dict(attack=7,dexterity=1)),
 ('bread_tongs','Breite Backwarenzange','Greift auch die flachen Teilchen, ohne sie zu zerdrücken.',dict(attack=9,dexterity=2,rarity='Selten')),
 ('clip_folder','Wasserfeste Betriebsmappe','Die Betriebs-Besonderheiten bleiben lesbar.',dict(attack=8,insight=2)),
 ('crate_lifter','Kistenheber mit Doppelgriff','Zu zweit greifen; hier als starker Parcoursgegenstand spielbar.',dict(attack=14,strength=2,weight=3,rarity='Episch')),
 ('foam_baton','Schaumstoff-Baguette','Für den freiwilligen Parcours. Keine Lebensmittel werden dabei als Waffe verschwendet.',dict(attack=6,dexterity=1)),
 ('sorting_rake','Sortiergreifer','Damit bewegst du Material, ohne tief in den Behälter greifen zu müssen.',dict(attack=8,handling=12)),
 ('route_board','Magnetischer Schichtplan','Sam hat die Vertretungen mit einer anderen Farbe markiert.',dict(attack=12,presence=2,weight=2,rarity='Episch')),
]: add(key,name,'weapon',desc,**stats)

for key, name, desc, stats in [
 ('fleece','Fleecejacke','Die Pause am Kanal fühlt sich weniger kalt an.',dict(defense=3)),
 ('waterproof_apron','Abwaschbare Arbeitsschürze','Für die Reinigung wechseln, danach Hände waschen.',dict(defense=2,handling=18,durability=50)),
 ('cargo_vest','Weste mit großen Taschen','Etiketten, Bonbons und Telefonnummern passen getrennt hinein.',dict(defense=3,capacity=3)),
 ('padded_jacket','Gefütterte Lieferjacke','Ein alter Aufnäher ist abgetrennt; die Polster sind noch gut.',dict(defense=6,weight=2,rarity='Selten')),
 ('hi_vis_suit','Warnschutz-Overall','Viel Stoff für eine lange Rampenschicht.',dict(defense=8,handling=8,weight=3,dexterity=-1,rarity='Episch')),
 ('work_overall','Lageroverall','Die verstärkten Nähte halten auch die Rollregalrunde aus.',dict(defense=5,grip=1,weight=2)),
 ('cool_bag','Kleine Kühltasche','Mit Kühlelementen bestückt. Leichter als die große Box.',dict(capacity=4,cooling=1)),
 ('cargo_crate','Stapelbare Lebensmittelkiste','Sauber, lebensmittelecht und mit passenden Griffen.',dict(capacity=9,weight=2)),
 ('insulated_box','Isolierbox mit Einsatz','Die Einsätze halten Schachteln auseinander.',dict(capacity=11,cooling=1,weight=3,rarity='Episch')),
 ('bike_panniers','Doppelte Fahrradtaschen','Links und rechts gleichmäßig packen.',dict(capacity=12,weight=2,rarity='Selten')),
 ('folding_cart','Faltbarer Handwagen','Hannes hat das klappernde Rad ersetzt.',dict(capacity=15,weight=3,rarity='Episch')),
 ('food_backpack','Abwaschbarer Lebensmittelrucksack','Getrennte Fächer für Kleinteile und verpackte Ware.',dict(capacity=8,handling=5)),
]: add(key,name,'gear' if 'capacity' in stats and key not in ('cargo_vest',) else 'armor',desc,**stats)

# Single-use supplies: effects refresh instead of stacking without limit.
for key, name, desc, stats in [
 ('soap','Kleine Handseife','Am Waschplatz zusammen mit Wasser benutzen.',dict(hygiene=50)),
 ('wash_kit','Mobiles Handwaschset','Wasser, Seife und sauberes Tuch für eine Spielrunde.',dict(hygiene=80)),
 ('clean_towel','Frisches Handtuch','Kommt sauber verpackt aus der Treffküche.',dict(hygiene=25)),
 ('cleaning_wipes','Reinigungstücher','Für Arbeitsmaterial und Hände im abstrakten Spielmodell.',dict(hygiene=35)),
 ('garbage_bags','Rolle Müllbeutel','Die Sortierrunde bleibt übersichtlich; für Lebensmittel ungeeignet.',dict(effect='handling',power=12,turns=5)),
 ('odor_sachet','Geruchsbeutel für die Pause','Eine erfundene Spielhilfe gegen Geruchsbelastung, kein Atemschutz.',dict(effect='odor_guard',power=10,turns=4)),
 ('ice_pack','Gefrorenes Kühlelement','Kühlt die Ladung im Spiel vier Runden. Macht eine unterbrochene Kühlkette nicht rückgängig.',dict(effect='cooling',power=1,turns=4)),
 ('cooling_set','Ersatz-Kühlakkus','Für eine längere Runde zwischen zwei Kühlschränken.',dict(effect='cooling',power=1,turns=8,rarity='Selten')),
 ('repair_tape','Gewebeklebeband','Im Spiel werden damit die gerade angelegten verschlissenen Teile ausgebessert.',dict(repair=12)),
 ('repair_kit','Näh- und Flickset','Ein paar Minuten Aufmerksamkeit für beanspruchtes Material.',dict(repair=25,rarity='Selten')),
 ('spare_filters','Verpackte Ersatzfilter','Im Spiel nur für den Gesichtsslot; keine echte Filterfreigabe.',dict(repair=30,repair_slot='face')),
 ('fresh_gloves','Frisches Paar Ersatzhandschuhe','Füllt im Spiel die Haltbarkeit des angelegten Handschuhpaars auf.',dict(repair=30,repair_slot='hands')),
 ('ginger_tea','Ingwertee','Scharf, warm und im Spiel beruhigend.',dict(nausea=-18,water=18,effect='digestion',power=1,turns=4)),
 ('still_water','Große Flasche stilles Wasser','Ein Liter, den du nicht erst am Laden suchen musst.',dict(water=55,weight=2)),
 ('sparkling_water','Sprudelwasser','Löscht Durst, bringt im Spiel aber auch etwas Bauchgas.',dict(water=35,gas=12)),
 ('fruit_tea','Ungesüßter Früchtetee','Eine zweite Thermoskanne aus der Treffküche.',dict(water=30,nausea=-8)),
 ('coffee_flask','Thermosbecher Kaffee','Für ein kurzes Hoch mit einem kleinen Preis am Magen.',dict(energy=20,nausea=10,effect='insight',power=1,turns=4)),
 ('route_note','Aktualisierter Tourenzettel','Du liest die Änderungen noch einmal; Übersicht für die nächsten Aufgaben.',dict(effect='insight',power=2,turns=5)),
 ('stretch_card','Kurze Dehnpause','Eine Karte mit einer freiwilligen Pausenroutine. Der Bonus ist reine Spielmechanik.',dict(effect='strength',power=2,turns=4)),
 ('breathing_break','Ruhige Atempause','Du setzt dich kurz abseits des Trubels hin.',dict(nausea=-10,effect='presence',power=2,turns=5)),
 ('grip_chalk','Griffhilfe für den Parcours','Nur am trockenen Übungsmaterial, nicht auf Lebensmitteln.',dict(effect='dexterity',power=2,turns=4)),
 ('rest_mat','Faltbares Pausenkissen','Eine kurze Sitzpause mit etwas mehr Erholung.',dict(heal=18,energy=12)),
 ('peppermint_tea','Pfefferminztee','Der Deckel der Kanne ist zugleich ein Becher.',dict(water=20,nausea=-22,gas=-15)),
 ('fennel_bag','Fenchel-Anis-Tee','Im Spiel eine besonders gute Pause bei vollem Bauch.',dict(gas=-35,nausea=-12)),
]: add(key,name,'consumable',desc,**stats)

# Nutrition adds delayed energy, salt load, belly gas and bowel urgency.
for key,name,desc,energy,fullness,risk,shelf,extra in [
 ('pear','Birne','Cems kleine Birnen geben beim Transport leicht nach.',16,18,1,9,dict(fiber=3,water=6)),
 ('orange','Orange','Schale erst am Pausenplatz entfernen.',15,16,2,15,dict(water=8,fiber=2)),
 ('melon','Melonenstück in geschlossener Box','Viel Saft, wenig Platz für weitere Portionen.',18,26,2,4,dict(water=18,cold=True,fiber=1)),
 ('grapes','Weintrauben','Eine kleine Schale aus Iris’ Obstkiste.',20,18,1,6,dict(water=6,fiber=2)),
 ('cucumber','Gurke','Die krumme Form passt diagonal in die Tasche.',10,20,0,12,dict(water=14,fiber=1)),
 ('tomato','Tomaten','Vor dem Einpacken jede einzelne prüfen.',12,16,1,7,dict(water=8,fiber=2)),
 ('pepper','Paprika','Ein etwas weicher Stiel macht noch keine ganze Kiste unbrauchbar.',14,18,1,10,dict(fiber=3)),
 ('oats','Haferflocken-Portion','Die Portion aus der Treffküche hält eine Weile vor.',32,28,0,18,dict(fiber=4)),
 ('porridge','Gekühlter Haferbrei','Von der Küfa, mit Deckel und Zutatenliste.',30,30,1,5,dict(fiber=4,cold=True,personal_only=True)),
 ('rice','Gekühlte Reisportion','Eine beschriftete Box aus der Kantine.',30,28,2,4,dict(cold=True,personal_only=True)),
 ('pasta','Gekühlte Nudeln mit Gemüse','Rike hat den Deckel mit dem Zubereitungsdatum versehen.',36,34,3,4,dict(cold=True,fiber=2,personal_only=True)),
 ('lentils','Linseneintopf','Eine ordentliche Portion aus der Küfa.',36,35,2,5,dict(fiber=6,personal_only=True)),
 ('beans','Bohnensalat','Macht satt; die Spielverdauung hat damit mehr zu tun.',28,30,3,4,dict(fiber=7,cold=True,personal_only=True)),
 ('nuts','Nussmischung in Originalpackung','Kleine Portion, viel Energie. Zutaten beachten.',38,16,1,30,dict(fat=6,fiber=2)),
 ('crackers','Salzcracker','Knuspern im Spiel mit zusätzlichem Durst.',25,16,0,35,dict(salt=12)),
 ('chips','Kartoffelchips','Jo stellt die verschlossene Restpackung neben die Abholkisten.',30,20,6,30,dict(salt=16,fat=7)),
 ('croissant','Croissant','Utes Buttergebäck braucht weniger Platz als sein Energiegehalt vermuten lässt.',34,24,2,9,dict(fat=6)),
 ('muffin','Blaubeermuffin','Aus der Backstube am Gleis 4, ohne Cremefüllung.',28,22,2,8,dict(fat=4)),
 ('quark','Quark in Originalpackung','Bleibt bis zur Verwendung in der Kühlbox.',26,24,3,5,dict(cold=True)),
 ('hummus','Hummus in geschlossener Dose','Die Zutatenliste klebt gut lesbar auf dem Deckel.',30,24,3,5,dict(fiber=4,fat=4,cold=True)),
 ('kefir','Kefir','Ein gekühlter Becher mit ungeöffneter Verpackung.',22,18,4,5,dict(cold=True,water=5)),
 ('pickles','Essiggurken im Originalglas','Salzig und im Spiel keine ganze Mahlzeit.',10,16,5,18,dict(salt=8)),
 ('chocolate','Tafel Schokolade','Eine geschlossene Packung aus dem Abholkorb.',35,14,2,35,dict(fat=5)),
 ('dates','Getrocknete Datteln','Ein kleines Päckchen für die lange Fahrt.',28,15,0,30,dict(fiber=4)),
 ('hot_sauce','Sehr scharfe Würzsauce','Nele hat dir das Warnschild auf dem Etikett extra gezeigt.',8,6,35,30,dict(salt=6)),
 ('potato','Gekochte Kartoffeln','Beschriftet aus der Kantine, für die persönliche Übergabe.',26,28,1,5,dict(fiber=2,personal_only=True)),
 ('sandwich','Gekühltes belegtes Brot','Der Belag macht Kühlung nötig.',32,28,3,4,dict(cold=True,personal_only=True)),
 ('pizza','Gekühlte Gemüsepizza','Ein letzter Karton aus der Kantine, fürs persönliche Gespräch reserviert.',38,35,5,4,dict(cold=True,fat=6,salt=10,personal_only=True)),
]: add(key,name,'food',desc,energy=energy,fullness=fullness,risk=risk,shelf=shelf,**extra)

FOOD_POOLS = [
 ['bread','pretzel','croissant','muffin','banana'],
 ['carrot','apple','pear','orange','tomato','pepper','cucumber'],
 ['yogurt','cheese','quark','kefir','hummus','nuts','crackers','chips'],
 ['cake','pretzel','muffin','croissant','chocolate'],
 ['soup','salad','rice','pasta','potato','pizza','sandwich'],
 ['apple','carrot','chili','pear','hot_sauce'],
 ['pretzel','bread','muffin','sandwich','dates'],
 ['berries','cheese','salad','grapes','oats','beans','porridge','lentils','melon','pickles'],
]
# Nutrition of legacy foods remains compatible, but now participates in digestion.
for key in ('apple','carrot','bread','berries'):
    ITEMS[key]['fiber'] = 2
ITEMS['pretzel']['salt'] = 7
ITEMS['cheese']['fat'] = 5
ITEMS['cake']['fat'] = 6
