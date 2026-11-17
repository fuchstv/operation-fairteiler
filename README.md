# 🥕 Operation: Fairteiler

Ein inoffizielles Text-RPG mit zwei Modi: eine satirische Roguelike-Rettungstour
und ein separates Lernabenteuer über den Weg zum Foodsaver. Wähle den Modus in
der Seitenleiste. Szenen und Dialoge sind erfunden; im Lernmodus verlinken die
Regelhinweise auf das Wiki. Das Spiel ersetzt keine echte Qualifizierung.

## Lokal im Browser starten – ohne Installation

1. Die Datei **index.html** herunterladen bzw. das Repository als ZIP entpacken.
2. **index.html per Doppelklick im Browser öffnen.** Es ist kein Server nötig.
3. Spielen. Das Spiel benötigt weder Python noch Streamlit, Node.js oder Internet.

Die einzelne HTML-Datei enthält alle 152 Items, Spieltexte, Styles und den
JavaScript-Spielkern. Sie kann allein in einen anderen Ordner kopiert werden.
Sounds werden nach Aktivierung lokal per WebAudio erzeugt; Wiki-Links sind
optionale externe Verweise. Es werden keine Daten übertragen.

Browser-Spielstände werden nach Aktionen automatisch in `localStorage`
gespeichert. **Spielstand exportieren** lädt eine JSON-Datei herunter;
**Spielstand importieren** stellt sie wieder her. Browser können lokale Daten
bei privaten Sitzungen, geänderten Dateipfaden oder restriktiven Einstellungen
anders behandeln. Für dauerhafte Sicherungen die Exportfunktion nutzen.
Ein ungültiger Import lässt den bisherigen Spielstand unverändert. Ein beim
Start unlesbarer Spielstand wird erst bei ausdrücklich bestätigtem Neustart
oder gültigem Import ersetzt.

Die Browser-Version enthält Charakterwürfe, Stat-Checks mit farbigen Tooltips,
Abholbriefings, Routen, Kämpfe, Tonnenrunden, alle Ausrüstungsplätze und
Verbrauchsgegenstände, Verdauung, BOT/BV-Interaktionen, Fairteilung inklusive
Essenskorb und Hygieneplan, Hotseat-PvP und das Lernabenteuer. Browser und Python
verwenden unterschiedliche Zufallsgeneratoren; gleiche Seeds erzeugen nicht
plattformübergreifend dieselben Würfe. Browser-Exporte sind keine
Streamlit-Spielstände. Online-PvP und echte Plattformaktionen sind nicht enthalten.

### Browser-Version weiterentwickeln

Die fertige `index.html` ist versioniert. Zum **Spielen** ist kein Build nötig.
Entwicklungsvorlagen liegen unter `web/`; die Daten werden aus den bestehenden
Python-Modulen übernommen. Zum Aktualisieren nach einer Änderung:

```bash
python3 scripts/build_web.py
node --test web/engine.test.cjs
```

Der Build braucht nur Python-Standardbibliothek und die vorhandenen
Projektmodule; Node.js wird ausschließlich für die JavaScript-Tests benötigt.
`web/data.json` und `index.html` werden deterministisch generiert. `web/engine.js`
enthält die portablen Regeln, `web/ui.js` die Browseroberfläche. Für Änderungen
zusätzlich den echten Offline-Start per `file://` in Desktop- und Mobilansicht
prüfen. Die Streamlit-Version kann weiterhin wie unten beschrieben gestartet
werden.

Die automatisierten Browserprüfungen lassen sich mit installiertem Playwright
und Chromium über `python3 scripts/test_web_browser.py` wiederholen (standardmäßig
per `file://`). Optional: `--chromium /pfad/zum/browser` und
`--url http://127.0.0.1:8877/index.html` für eine lokale Testadresse.
In der verwalteten Cloud wurde der direkte `file://`-Aufruf durch eine
Administratorrichtlinie blockiert. Geprüft wurden stattdessen die unveränderte
HTML über eine Loopback-Adresse, der eingebettete Inhalt bei vollständig
deaktiviertem Netzwerk sowie Speichern, Neuladen, Import/Export und Mobilansicht.

## Roguelike: Operation Feierabend

- Fünf Abholtage im selben Stammbezirk mit je vier Stationen, verzweigten Routen und acht Betrieben:
  Bäckerei, Wochenmarkt, Supermarkt, Café, Kantine, Hofladen, Bahnhofsbackstube
  und Bioladen. Die letzte Ausgabe in der Werkskantine wartet als Abschluss am Ende.
- Seed-basierte Zufallsrouten, Kämpfe, Ereignisse und Beute. Gleicher Seed plus
  gleiche Entscheidungen ergeben denselben Run. Tod beendet den Run;
  Neustart verwirft Charakter und Beute. Keine dauerhaften Meta-Upgrades.
- 152 Items: 20 Werkzeuge/Parcoursgeräte, 11 Kleidungsstücke, 11 Transport-/Kühlgegenstände,
  12 Handschuhe, acht Masken, acht Schuhe, acht Zubehörteile, 41 Nahrungsmittel
  und 33 Verbrauchsgegenstände. Vier Seltenheitsstufen,
  Traglast, Ausrüstungsslots, Beuteauswahl und Levelaufstiege.
- Rundenbegegnungen mit Weiterarbeiten, kräftigem Anpacken, Kräfteeinteilung
  und Ersatzanfrage. Jeder Betrieb hat eine eigene Aufgabe und Belastung. Itemeinsatz kostet eine Runde samt gegnerischem Zug.
- Magenfüllung, Übelkeit, Hunger/Energie und Wasser. Vorräte altern pro Runde;
  Kühlung verlangsamt den Verderb ab dem Anlegen. Überessen, reizende und
  verdorbene Nahrung erhöhen Spiel-Übelkeit. Tee, Wasser und Pausen helfen.
- Nachbarschaftstreffs zum Ausruhen oder Teilen geeigneter Lebensmittel;
  zufällige Ereignisse mit sicherem und riskantem Weg.
- Echtes **lokales Hotseat-PvP**: Zwei Menschen am selben Gerät wechseln sich
  ab. Symmetrische Ausrüstung, Ausdauer und je zwei Versorgungspausen im Abhol-Parcours.
  Kein Online-Multiplayer. Die NPC-Trainingsduelle auf der Karte sind separat
  gekennzeichnet und kein PvP. Hotseat-Duelle verändern den laufenden Run nicht.

Waffen, Duelle und Magenwerte sind satirische Spielregeln, keine Aussagen über
foodsharing, Lebensmittelhygiene oder medizinische Behandlung. Automatische
Sitzungsspeicherung im Browser oder ein Server für Online-Spieler sind nicht
enthalten. Fortschritt und lokales Duell leben in der Streamlit-Sitzung.

## Streamlit-Version spielen und entwickeln

Python 3.12 wurde getestet. Das Projekt benötigt ausschließlich Streamlit;
Datenbank, externe Mediendienste und Zugangsdaten sind nicht erforderlich.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.headless=true --browser.gatherUsageStats=false
```

Der Lernmodus bietet drei Übungsfragen, drei begleitete Abholungen, einen
Abschluss, Inventar und einen Tagebuch-Download. Falsche Entscheidungen liefern
Hinweise und können erneut versucht werden. Sounds sind zunächst aus und lassen
sich in der Seitenleiste aktivieren. Browser können automatische Audiowiedergabe
blockieren; ein manueller Player steht ebenfalls bereit. Animationen können
abgeschaltet werden und respektieren `prefers-reduced-motion`.

Der Fortschritt bleibt in der aktuellen Streamlit-Sitzung. Nach deren Ende
beginnt eine neue Runde; der Tagebuch-Download ist kein importierbarer Spielstand.

## Prüfungen

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pip check
```

Die Tests prüfen die Roguelike-Regeln und führen die echte Streamlit-Anwendung
mit AppTest aus: Seeds, Ausrüstung, Verderb/Kühlung, Überessen, Zugkosten,
Permadeath, Beute, Endboss, Hotseat-Züge sowie den vollständigen Lernspielbogen. Für Änderungen an Darstellung oder Audio zusätzlich
im Browser prüfen, auch bei schmalem Viewport.

## Quellen und Gestaltung

Siehe [SOURCES.md](SOURCES.md) für die geprüften Wiki-Versionen und die
Layoutreferenzen. Die Oberfläche orientiert sich an der braun-grünen Farbwelt
und Kartenstruktur des foodsharing-Projekts. Der kurze Erfolgston wird lokal
synthetisiert; es werden keine externen Sounddateien geladen.

Dieses Spiel steht in keiner offiziellen Verbindung zu foodsharing.
Lizenz: [AGPL-3.0](LICENSE).

## Erzählerisches Rework

Die Tour führt von Montag bis Freitag durch fünf benannte Viertel. Sam
koordiniert den Ersatz für den ausgefallenen Lieferwagen. Acht wiederkehrende
Ansprechpersonen stellen konkrete Aufgaben: Ute braucht ihre Brotkörbe zurück,
Cem Hilfe beim Sortieren unter der Plane und Rike einen freien Flur vor der
Spülküche. In betrieblichen Begegnungen steht die gegnerische Leiste für
Restaufwand, die eigene für Kraft. Werkzeuge erhöhen das Arbeitstempo;
Arbeitskleidung verringert die Belastung. Hotseat bleibt ein getrennter
Wettbewerb im Abhol-Parcours.

Alle 152 Items besitzen Herkunfts- und Gebrauchstexte. Beispielsweise ersetzt
ein Rollbrett das frühere „Nudelholz +3“. Gerettete Lebensmittel werden erst
beim tatsächlichen Einpacken gezählt. `narrative.py` enthält die Orte,
Begegnungen und Ereignisse. Der erweiterte Itemkatalog steht in `catalog.py`.

## Charaktererschaffung und Stat-Checks

Jede neue Roguelike-Tour beginnt mit vier gewürfelten Attributen:
**Muskelkraft, Geschick, Übersicht und Auftreten**. Pro Attribut werden vier
sechsseitige Würfel geworfen; die niedrigste Zahl entfällt. Zwei vollständige
Neuwürfe sind erlaubt. Ein Hintergrund gibt +2 auf ein passendes Attribut.
Nach dem Bestätigen sind die Werte für diesen Run fest. Muskelkraft verändert
zusätzlich die Traglast um zwei Einheiten je Attributsbonus.

Eine Probe lautet `W20 + Bonus >= Schwierigkeit`. Der Attributsbonus ist
`(Wert − 10) // 2`. Passende Werkzeuge helfen; Energie unter 25 und Übelkeit ab
50 geben jeweils −2. Natürliche 1 scheitert immer, natürliche 20 gelingt immer.
Die Vorschau berechnet exakt, wie viele der 20 möglichen Würfe erfolgreich
sind, ohne dabei den Zufallsgenerator weiterzuschalten. Gewürfelt wird erst bei
der Entscheidung, mit dem Zustand vor den Aktionskosten.

- **Grün (ab 70 %)**: gute Aussicht.
- **Gelb (40–65 %)**: offener Ausgang.
- **Rot (unter 40 %)**: riskant.

Die farbigen Hinweise zeigen beim Darüberfahren oder Tastaturfokus einen
Tooltip mit Formel, Bonusquellen und Konsequenzen. Dieselben Details stehen in
der Hilfe des jeweiligen Buttons. Nach dem Wurf erscheint die vollständige
Probe mit Erfolg oder Misserfolg.

Normales Weiterarbeiten nutzt das zum Betrieb passende Attribut: etwa Geschick
in der Bäckerei, Übersicht in der Kantine und Auftreten bei Iris. Ein Misserfolg
bringt halben Fortschritt statt eines Stillstands. Kräftiges Anpacken nutzt
Muskelkraft, bringt bei Erfolg ×1,8 Fortschritt und bei Misserfolg keinen;
12 zusätzliche Energie fallen in beiden Fällen an. Geschick entscheidet beim
Kräfteeinteilen über 9 statt 3 Punkte Entlastung. Auftreten entscheidet, ob eine
Ersatzanfrage gelingt. Auch die riskanten Umwege verwenden Stat-Checks; die
sichere Pause benötigt keinen Wurf. Das lokale Hotseat-PvP bleibt symmetrisch
und verwendet keine gewürfelten Charakterattribute.

Attribute werden aus dem Tour-Seed und der Anzahl der Neuwürfe bestimmt,
getrennt vom Zufallsgenerator für Route und Begegnungen. Für eine exakte
Wiederholung sind damit auch gleicher Hintergrund und gleiche Neuwürfe nötig.

## BOTs, Zusammenhalt (Spielwert) und Verantwortung

Der Reiter **Bezirk & Betriebsteams** führt zu Sam (BOT) und Robin (BV). BOTs meint hier
Botschafter*innen, nicht KI-Gegner. Die Beziehungen und Folgen sind erfundene
RPG-Mechanik; offizielle Verfahren oder Kartensysteme werden nicht simuliert.

- Abgeschlossene betriebliche Abholungen geben +2 Zusammenhalt. Nach zwei
  Abholungen beim selben Betrieb sinkt dort die Schwierigkeit beim
  Weiterarbeiten um 1, weil die Abläufe bekannt sind.
- Nach jeder zweiten betrieblichen Abholung folgt eine Rückfrage zur Kühlkette,
  zum Sortieren oder zu einer zeitlich kollidierenden Zusage. Das Finale bleibt
  davon ausgenommen. Eine verantwortliche Entscheidung kostet 5 Energie und
  gibt +5 Zusammenhalt. Eine Absprache mit Sam verwendet eine Auftreten-Probe:
  Erfolg kostet 2, Misserfolg 8 Energie; beide Lösungen sind regelkonform.
- Eine bewusst bestätigte Abkürzung spart 10 Energie, kostet 15 Zusammenhalt und
  hinterlässt einen Vorfall. Fragliche Lebensmittel werden nicht tatsächlich
  verteilt. Ein misslungener Würfelwurf ist kein Regelverstoß.
- Offene Vorfälle lassen sich auf der Karte mit Sam aufarbeiten: 8 Energie plus
  eine Runde, mindestens 11 Energie erforderlich; +7 Zusammenhalt. Der Eintrag
  bleibt als aufgearbeitet erhalten. Mehrfaches Aufarbeiten bringt keinen Bonus.
- Ab 70 Zusammenhalt gibt es +1 auf Auftreten-Proben, unter 25 gibt es −1.
  Robin organisiert mit dem Betriebsteam auf der Karte ab 40 Zusammenhalt einmal je Abholtag eine Ablösung:
  +12 Kraft, +30 Wasser und +20 Energie vor den Kosten einer Runde.
- Drei Aufträge belohnen tatsächlichen Fortschritt: drei geeignete Posten teilen
  (Kühlbox), drei betriebliche Abholungen (Tourenmappe), zwei verantwortliche
  Rückfragen (Erste-Hilfe-Set). Material und +5 Zusammenhalt sind je Auftrag einmal
  erhältlich; im Rucksack muss Platz sein.

Die Rückfragen stützen sich inhaltlich auf die in SOURCES.md aufgeführten
Hygieneregeln und Zuverlässigkeitsregeln. Zusammenhaltszahlen, Materialbelohnungen,
Unterstützung und Gesprächskosten sind frei erfunden. Alle Daten bleiben in der
Spielsitzung; es werden keine echten Personen kontaktiert oder Vorfälle gemeldet.

## Begriffe aus dem foodsharing-Wiki

Die Hauptseite und die dort verlinkten Rollen- und Regelartikel bilden die
sprachliche Grundlage. **BOTs** koordinieren den Bezirk; **BV** betreuen
Kooperationen mit Betrieben und organisieren die Abholungen mit dem
**Betriebsteam**. Auf den fiktiven Betriebsseiten stehen
**Betriebs-Besonderheiten** und Nachrichten aus dem Betriebsteam.
**Fairteilung** ist die bedingungslose, kostenlose Weitergabe der geretteten
Lebensmittel. Die Materialboni im RPG sind keine Gegenleistung für Lebensmittel.

Der Bereich „Bezirk & Betriebsteams“ enthält **persönliche Gesprächsnotizen**.
Sie sind keine Meldungen einer Regelverletzung (MRV). Für formelle Meldungen
ist grundsätzlich die **Lokale Meldungsgruppe (LMG)** zuständig; das Spiel
bildet diese Bearbeitung und ihre Konsequenzen nicht nach. Der Zusammenhalt
ist ein erfundener Spielwert, keine Vertrauensbanane oder Abholquote.
Die geprüften Wiki-Versionen und Zuordnungen stehen in SOURCES.md.

## Wiki-Erweiterung: Abholbriefing und Fairteilung

Vor jedem betrieblichen Abholtermin prüfst du im **Abholbriefing** deinen
fiktiven Foodsaver-Ausweis, die Betriebs-Besonderheiten samt Pinnwand und
Teamchat, saubere lebensmittelechte Behälter und den hygienischen Umgang mit
Backwaren. Acht Situationen behandeln Wartezeiten bis/über 15 Minuten,
Tragehilfen, höfliches Verhalten, aktuelle Absprachen, gemeinsame Aufteilung
sowie MHD und Verbrauchsdatum. Diese Wissensentscheidungen erfordern keinen
Würfelwurf: Eine falsche Antwort kann ohne Regelmeldung korrigiert werden.
Im Roguelike ist die Figur bereits verifiziert; echte Einführungsabholungen
und die echte Verifizierung bleiben außerhalb des Spiels.

Im Reiter **Fairteilen** entscheidest du zwischen:

- **Persönlicher Übergabe:** Genießbarkeit prüfen, Gespräch ermöglichen,
  verantwortungsvolle Behandlung einschätzen und nötige Hinweise geben.
- **Fiktivem Essenskorb mit Abholabsprache:** Ware reservieren, eine weitere
  Runde bis zur Antwort abwarten und vor der persönlichen Übergabe erneut
  prüfen. Reservierte Lebensmittel bleiben im Rucksack, können nicht parallel
  gegessen, abgelegt oder anders verteilt werden und altern weiter. Der Korb
  kann zurückgenommen werden. Erst die tatsächliche Übergabe zählt als fairteilt.
- **Fairteiler am Bezirkstreff:** Nicht-persönliche Weitergabe. Der Kühlschrank
  wird im fiktiven Hygieneplan kontrolliert (5 °C), ungeeignete Ware entfernt
  und bei Bedarf gereinigt. Geprüfte, ungeöffnete Kühlware darf bei erhaltener
  Kühlkette und dokumentierter Kühlschrankkontrolle hinein. Zubereitete warme
  oder kühlbedürftige Speisen bleiben für diesen Weg ausgeschlossen. Das
  ungekühlte Regal beim Pausen-Stopp nimmt weiterhin keine Kühlware an.

**Spielgrenze:** Eine Runde ist keine echte Temperatur- oder Zeitmessung.
Kühlware ohne angelegte Kühlung gilt nach einer Runde konservativ als länger
ungekühlt und ist dann für jede Weitergabe gesperrt. Spätere Kühlung stellt die
Kühlkette nicht wieder her. Die vereinfachte Itemprüfung ersetzt keine reale
Prüfung von Verpackung, Datum, Transport und Genießbarkeit.

Alle Übergaben sind kostenlos und bedingungslos. Der +5-Kraft-Bonus je Posten
ist eine RPG-Belohnung. Die Aufgabe für den Fairteiler zählt ausschließlich
Posten, die tatsächlich über einen der Spiel-Fairteiler weitergegeben wurden.
Es werden keine Essenskörbe veröffentlicht, Personen angeschrieben oder echte
Hygieneprotokolle erstellt. Der fiktive Verlauf bleibt in der Sitzung.

## Großer Item-Ausbau: Ausrüstung, Tonnen und Verdauung

**Sieben Ausrüstungsplätze:** Werkzeug/Duellgerät, Arbeitskleidung, Transport,
Hände, Gesicht, Füße und Gürtel/Zubehör. Neue Figuren haben einfache Handschuhe,
eine Stoffmaske und Seife im Rucksack; diese zusätzlichen Teile müssen selbst
angelegt werden. Rucksack und Lexikon lassen sich durchsuchen und nach Kategorie
filtern, das Lexikon auch nach Seltenheit. Neue Lebensmittel kommen aus zu den
Betrieben passenden Beutepools, Verbrauchsmaterial und Ausrüstung aus den
Materialangeboten nach einer Begegnung. Alle 152 Items sind im Spiel erreichbar.

Handschuhe unterscheiden sich in Griff, Beweglichkeit, Entlastung, Spiel-Hygieneschutz
und Haltbarkeit. Masken wirken auf die abstrakte Staub-/Geruchsbelastung der
Sortierszenen. Schuhe können den Energieverbrauch senken. Zubehör und einzelne
Werkzeuge verändern Proben; die Boni erscheinen in den Erfolgschancen.
Handschuhe, Masken und manche Kleidung verschleißen pro Runde. Bei Zustand 0
fallen ihre Boni aus. Reparaturmaterial wirkt auf die angelegten, passenden
Teile und kann den maximalen Zustand nicht überschreiten.

Verbrauchsgegenstände können heilen, trinken lassen, Hygiene erhöhen, Bauchgas
lindern, Teile reparieren oder zeitweilige Effekte geben. Gleiche Effekte
werden erneuert, nicht unbegrenzt gestapelt. Kühlakkus geben vier bzw. acht
Runden Spielkühlung; vergangene Unterbrechungen der Kühlkette bleiben bestehen.

**Magensimulation:** Nahrung liefert ein Drittel Energie sofort, den Rest
in einer Verdauungswarteschlange. Pro Runde werden aus der vordersten Mahlzeit
normalerweise vier Energie aufgenommen, bei fettreicher Nahrung drei.
Ballaststoffe erhöhen Spiel-Bauchgas, Salzlast erhöht ab 10 den Wasserverbrauch
um einen Punkt pro Runde. Schmutzige Hände erhöhen beim Essen den Magenreiz.
Hoher Toilettendrang kostet zusätzliche Energie. Bei sehr hoher Übelkeit
kann der Spielmagen rebellieren und Wasser verlieren. Waschplatz und
Toilettenpause sind eigene Aktionen zwischen den Stationen.

**Acht Tonnen-/Sammelplätze:** Papier, Wertstoffe, Restmüll, Bio, Altglas,
Rolltonne, Textilien und Werkstattmaterial. Eine freiwillige, abgesprochene
Sortierrunde ersetzt eine Station, nie das Finale. Eine passende Stat-Probe
entscheidet über zwei Materialangebote; Handschuhe, Masken und Griffwerte
verändern die Belastung. Es gibt dort keine Lebensmittelbeute, und die Runde
zählt nicht als betriebliche Lebensmittelabholung. Material kommt aus
freigegebenen Beständen und Spenden.

Alle Schutzwerte und Körperreaktionen sind RPG-Abstraktionen. Eine Maske
oder ein Paar Handschuhe macht weder unsichere Lebensmittel noch eine
unterbrochene Kühlkette sicher. Es werden keine realen Arbeitsschutzklassen,
medizinischen Behandlungen oder Herstellerversprechen simuliert.
