"""Place-specific writing for the fictional evening pickup round."""
DISTRICTS = [
    ('Am Kanal', 'Montag, 17:10 Uhr. Sam stellt dir beim Bezirkstreffen Robin vor, die betriebsverantwortliche Person: „Der Lieferwagen fällt bis Freitag aus. Die Betriebsteams übernehmen die vereinbarten Abholtermine. Lies vor jeder Abholung die Betriebs-Besonderheiten, Pinnwand und Teamchat.“'),
    ('Rund um den Bahnhof', 'Dienstag, Feierabendverkehr. Die Bahnunterführung ist gesperrt. Auf dem Abholzettel hat jemand den Ersatzweg eingezeichnet – quer durch die Schiebestrecke.'),
    ('Im Gewerbehof', 'Mittwoch. Die Wege werden länger, die Kisten schwerer. Robin schreibt ins Betriebsteam: „In der Kantine bitte hinten klingeln. Vorne wartet ihr bis morgen.“'),
    ('Auf der Höhe', 'Donnerstag. Gegenwind auf der letzten Steigung. Am Treff wird schon Platz im Regal gemacht. Jetzt zählt, was du tatsächlich noch transportieren kannst.'),
    ('Die Schlussrunde', 'Robin ruft an: „In der Kantine steht noch eine ganze Lieferung. Danach machen sie übers Wochenende zu. Schau erst nach deinen Vorräten, bevor du zusagst.“'),
]
# Each location has its own obstacle, consequences, and breathing room.
ENCOUNTERS = [
    dict(name='Sechs Körbe, eine schmale Hintertür', opening='Bäckerin Ute hält die Tür mit dem Fuß auf. „Die blauen Körbe bleiben hier. Bitte umpacken, bevor der Fahrer kommt.“', pressure='Ute muss zum Lieferwagen. Der Durchgang muss frei werden.', recover='Ute nimmt ein Telefonat an. Du kannst ungestört weiterpacken.', hit='Ein Korb verkantet im Türrahmen. Das kostet Kraft.', done='Die Körbe stehen wieder im Regal. Ute zählt nach und gibt dir die Brote mit.'),
    dict(name='Sortieren unter der Marktplane', opening='Händler Cem klappt die Plane herunter. „Die Beeren bitte einzeln durchsehen. In der hinteren Kiste sind ein paar hinüber.“', pressure='Der Wind drückt Regen unter die Plane.', recover='Cem sichert die Plane. Du hast beide Hände zum Sortieren frei.', hit='Du musst die Kisten erneut umsetzen; dein Rücken meldet sich.', done='Die beschädigten Beeren sind aussortiert. Cem schiebt dir die geprüfte Ware zu.'),
    dict(name='Die Kühltheke macht Feierabend', opening='Mara aus der Spätschicht zeigt auf die Kühlwagen. „Ich brauche die Wagen zurück. Könnt ihr direkt hier in eure Boxen packen?“', pressure='Mara räumt den nächsten Wagen aus dem Gang.', recover='Die nächste Palette hängt noch an der Rampe. Kurz kein Nachschub.', hit='Du läufst noch einmal zur Abholtasche. Die zusätzliche Runde zehrt.', done='Die Wagen sind leer und die Ware ist verpackt. Mara schließt die Lagertür.'),
    dict(name='Eine Torte passt nicht quer', opening='Jo hat die Stühle schon hochgestellt. Die Tortenschachtel passt nicht durch die Öffnung deiner Tasche. „Bitte aufrecht. Das ist noch richtige Sahne.“', pressure='Jo braucht den Tresen für die Endreinigung.', recover='Die Kaffeemaschine spült. Du kannst in Ruhe neu packen.', hit='Du setzt die Schachteln ab und fängst noch einmal an.', done='Die Schachteln stehen sicher. Jo füllt dir Wasser nach: „Bis nächste Woche.“'),
    dict(name='Das Rollregal vor der Spülküche', opening='Küchenleiterin Rike schiebt ein Rollregal in den Flur. „Beschriftete Behälter rechts, leere zurück nach links. Und bitte den Fluchtweg freihalten.“', pressure='Aus der Spülküche kommt der nächste Wagen.', recover='Die Spülmaschine läuft. Für einen Moment gehört der Flur dir.', hit='Ein Deckel fehlt. Du musst zurück zur Ausgabe.', done='Die Behälter sind zugeordnet und das Rollregal ist frei. Rike hakt die Abholung ab.'),
    dict(name='Die unterste Kiste zuerst', opening='Auf dem Hof hat Nele die Ernte nach Größen gestapelt. Die aussortierten Äpfel stehen ganz unten. „Ich helfe kurz, dann muss ich zu den Tieren.“', pressure='Nele muss weiter. Der Stapel muss vorher wieder sicher stehen.', recover='Nele holt eine Sackkarre. Du kannst den Stapel vorbereiten.', hit='Eine Kiste lässt sich nur zu zweit anheben. Noch einmal umgreifen.', done='Der Stapel steht wieder. Nele stellt die aussortierten, geprüften Äpfel an dein Rad.'),
    dict(name='Abholung gegen den Pendlerstrom', opening='Am Seiteneingang wartet Deniz mit zwei Backblechen. „Nicht hier stehen bleiben. Hinter der Säule könnt ihr umpacken.“', pressure='Der nächste Zug ist angekommen; der Durchgang wird voll.', recover='Zwischen zwei Zügen ist der Gang für einen Moment leer.', hit='Du musst mit den Kisten ausweichen und den Weg doppelt gehen.', done='Die Bleche sind zurück im Laden. Deniz winkt dir durch die Seitentür.'),
    dict(name='Die Liste unter dem Leergut', opening='Iris sucht den Abholzettel. Er liegt unter den Leergutbons. „Die Ware auf dem grünen Tisch ist für euch, die anderen Kisten holt morgen der Lieferant.“', pressure='Ein weiterer Leergutwagen versperrt den Zugang.', recover='Iris sortiert die Bons. Du kannst die Abholkisten in Ruhe zuordnen.', hit='Du hast eine Lieferantenkiste erwischt. Zurückstellen und neu sortieren.', done='Nur die vereinbarte Ware ist eingepackt. Iris findet den Zettel und unterschreibt.'),
]
FINAL = dict(name='Die letzte Ausgabe vor dem Wochenende',
    opening='Rike schaut auf die Uhr: „Zwei Wagen, drei verschiedene Abholziele. Wenn wir das jetzt nicht aufteilen, bleibt es bis Montag hier.“ Robin wartet auf die Rückmeldung aus dem Betriebsteam.',
    pressure='Die Küche muss schließen. Noch ein Wagen blockiert den Flur.',
    recover='Robin bestätigt die nächste Abgabestelle. Du kannst die Behälter zuordnen.',
    hit='Eine Abgabestelle fällt aus. Du musst die Ladung neu aufteilen.',
    done='Der letzte Behälter ist zugeordnet. Rike zieht die Tür zu. Sam schreibt: „Alles unterwegs. Komm zum Treff, es gibt noch Tee.“')
EVENTS = {
    'rain': dict(title='Unter dem Vordach der Radwerkstatt', text='Der Regen läuft dir in die Ärmel. Die Werkstatt ist noch offen. Für den Treff liegt dort gespendetes Material bereit – du müsstest es über den nassen Hinterhof holen.', risk='Material über den Hof holen', safe='Unter dem Vordach warten', success='Die Werkstatt gibt dir ein Teil aus der Materialspende mit.', failure='Auf dem nassen Hof rutschst du weg. Die Abholung muss ohne das zusätzliche Material weitergehen.'),
    'crate': dict(title='Die Materialspende im Kellergang', text='Am Treff hängt ein Zettel: „Abholmaterial zur freien Verwendung“. Die guten Stücke stehen hinter einem Stapel leerer Kisten. Du könntest umräumen oder die Pause nutzen.', risk='Den Kellergang freiräumen', safe='Auf der Bank Pause machen', success='Hinter den Leerkisten findest du brauchbares Material für die Tour.', failure='Beim Umstapeln rutscht dir eine Kiste aus dem Griff. Du brichst die Suche ab.'),
    'stranger': dict(title='Hannes braucht eine zweite Hand', text='Hannes vom Treff steht vor dem Anhänger: „Fass mal mit an? Das Ersatzmaterial könnt ihr danach für eure Tour nehmen.“ Die Auffahrt ist steiler, als sie aussieht.', risk='Beim Anhänger mit anpacken', safe='Die eigene Ladung prüfen und kurz verschnaufen', success='Der Anhänger steht am Treff. Hannes überlässt dir ein Teil des Ersatzmaterials.', failure='Ihr müsst den Anhänger zweimal neu ansetzen. Danach fehlt dir die Kraft für die Materialsuche.'),
}
FLAVOUR = {
    'baguette': 'Der Griffbügel hält die Hand frei. Ute möchte den Korb bei der nächsten Tour zurück.',
    'spatula': 'Breite Kante, kurzer Stiel. Hilft beim Portionieren, ohne alles mit der Hand anzufassen.',
    'tongs': 'Vom Grillstand am Kanal. Damit bekommst du auch die letzten Brötchen vom tiefen Blech.',
    'clipboard': 'Abholzeiten vorne, Abgabeorte hinten. Die Ecke ist vom letzten Regen aufgequollen.',
    'rolling': 'Vier Rollen statt vier Wege. Auf Kopfsteinpflaster hört man dich schon um die Ecke.',
    'ladle': 'Der lange Stiel reicht bis auf den Grund von Rikes Suppentopf.',
    'leek': 'Passt gefaltet unter den Arm. Spart beim Gemüseholen mehrere Wege.',
    'stamp': 'Frisch gewartet, läuft geradeaus. Im engen Lager mehr wert als jede Heldentat.',
    'apron': 'Mehl in den Nähten, die Taschen voller Gummibänder.',
    'helmet': 'Die Schnalle klemmt ein wenig. Auf der Fahrt bleibt er trotzdem auf.',
    'vest': 'Von Sam mit dem Namen des Treffs beschriftet. Am Liefereingang wirst du damit erkannt.',
    'pot': 'Verstärkte Knie und eine Lage Stoff mehr für kalte Laderampen.',
    'raincoat': 'Hält den Nieselregen ab. Die Kapuze passt gerade über den Helm.',
    'gloves': 'Gegen raue Kistengriffe. Vor dem Anfassen unverpackter Lebensmittel ausziehen.',
    'tote': 'Vom Straßenfest übrig geblieben. Die Henkel sind doppelt vernäht.',
    'cargo': 'Der linke Reflektor ist neu. Die Kupplung vor dem Losfahren prüfen.',
    'cooler': 'Mit passenden Kühlelementen aus dem Treff. Schwerer als der Beutel, aber für Kühlware gedacht.',
    'thermos': 'Die freie Hand bezahlt man mit einem nassen Rücken.',
    'rack': 'Zwei breite Spanngurte gehören dazu. Erst verzurren, dann losfahren.',
    'banana': 'Ein paar braune Punkte. Sam nimmt sie für die Pause am Kanal mit.',
    'bread': 'Von gestern, noch gut schneidbar. Macht satt, braucht aber Platz im Bauch.',
    'apple': 'Klein und etwas schief. Nele sortiert solche aus, weil die Kundschaft die großen nimmt.',
    'carrot': 'Zwei Beine, keine Verkaufschance. Für den Topf ist die Form egal.',
    'yogurt': 'Ein Becher aus Maras Kühlwagen. Nicht für eine lange warme Radtour einplanen.',
    'cheese': 'Ein kleines Stück in der Originalverpackung. Gehört in deine Kühlbox.',
    'salad': 'Von Rike portioniert. Kühl halten und nicht zwischen den Brotkörben vergessen.',
    'soup': 'Die letzte Portion aus der Kantine. In der Spielpause eine ordentliche Mahlzeit.',
    'cake': 'Jo hat den Deckel mit zwei Streifen Klebeband gesichert. Aufrecht tragen.',
    'chili': 'Nele hat „scharf!“ auf die Tüte geschrieben. Das Ausrufezeichen ist verdient.',
    'pretzel': 'Deniz zählt die übrigen jeden Abend. Diese hat den Pendlerstrom verpasst.',
    'berries': 'Cem hat die weichen aussortieren lassen. Die übrigen halten trotzdem nicht lange.',
    'water': 'Am Treff frisch aufgefüllt. Einplanen, bevor der Durst die Tour bestimmt.',
    'tea': 'Aus Sams Thermoskanne. Für die Pause auf der Bank, nicht für den Fahrradlenker.',
    'charcoal': 'Eine zweite Kanne aus der Treffküche. Im Spiel beruhigt sie den Magen stärker als Fencheltee.',
    'bandage': 'Pflaster, Kompresse und eine kleine Rolle Verband aus dem Treff.',
    'espresso': 'Jo nennt ihn „den letzten“. Er hat das heute schon dreimal gesagt.',
    'mint': 'Eine Handvoll einzeln verpackter Bonbons aus der Schublade am Treff.',
    'juice': 'Aus dem Kasten neben Deniz’ Backblechen. Erst trinken, Pfand später sortieren.',
    'medkit': 'Das vollständige Ersatzset aus der Materialspende. Im Spiel mehr Erholung als das kleine Päckchen.',
    'snack': 'Lag in Sams Satteltasche für genau den Moment, in dem alle nur noch Hunger haben.',
    'sponge': 'Ein kühles Tuch und ein einzeln verpacktes Bonbon. Für fünf Minuten auf der Bank.',
}

# Fictional local agreements; they are not universal foodsharing rules.
BUSINESS_NOTES = [
    'Seiteneingang nutzen und gemeinsam eintreten. Saubere, lebensmittelechte Behälter mitbringen; die blauen Brotkörbe bleiben im Betrieb. Abholort ordentlich hinterlassen.',
    'Am vereinbarten Stand treffen. Jedes Stück vor der Weitergabe auf Genießbarkeit prüfen. Angefaulte Lebensmittel getrennt verpacken; Schimmeliges nicht weitergeben.',
    'Am Liefereingang melden. Für Kühlware Kühlbox und Kühlelemente einplanen. Rückfragen zum Ablauf gehen an Robin als BV; das Betriebsteam über Änderungen informieren.',
    'Die Abholung ist mit Jo am Seiteneingang vereinbart. Tortenschachteln aufrecht und gekühlt transportieren. Keine spontanen Zusatztermine ohne Absprache mit BV.',
    'Hinten an der Spülküche klingeln. Beschriftete Behälter zuordnen und den Durchgang freihalten. Lebensmittel vor der Weitergabe prüfen; bei Unklarheiten BV kontaktieren.',
    'Mit Nele am Hofverkauf treffen. Die Kisten nach dem Umpacken zurückstellen. Das Betriebsteam übernimmt die vereinbarte Menge gemeinsam; weitere Tragehilfe wartet außerhalb des Betriebs.',
    'Seiteneingang hinter der Säule nutzen. Gemeinsam eintreten und auf die Kundschaft Rücksicht nehmen. Backbleche nach dem Umpacken an Deniz zurückgeben.',
    'Nur die mit Iris vereinbarte Ware vom grünen Tisch abholen. Lieferantenkisten bleiben stehen. Mitteilungen aus dem Betrieb an Robin als BV weitergeben.',
]

# New items carry their own authored descriptions in the catalog.
from catalog import ITEMS as _ITEM_CATALOG
FLAVOUR.update({key: data['flavour'] for key, data in _ITEM_CATALOG.items() if 'flavour' in data})
