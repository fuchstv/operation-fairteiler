# Regel- und Layoutquellen

Abgerufen am 12. November 2026. Die Spieltexte sind eigenständige
Zusammenfassungen, keine vollständige Wiedergabe der Regelwerke.

| Quelle | Im Spiel verwendete Aussagen |
| --- | --- |
| [Foodsaver, Version 12919](https://wiki.foodsharing.network/w/index.php?title=Foodsaver&oldid=12919) | Quiz, danach Rechtsvereinbarung, mindestens drei Einführungsabholungen; Verifizierung von Profildaten und Foto; Ausweisdokument vorzeigen, keine Kopie fordern; Zuverlässigkeit und gegebenenfalls Ersatz organisieren. |
| [Einführungsabholungen, Version 12633](https://wiki.foodsharing.network/w/index.php?title=Verhaltensregeln:Einführungsabholungen&oldid=12633) | Begleitung und Rückmeldung; gegebenenfalls weitere Einführungsabholungen; Pünktlichkeit, Teamfähigkeit und Lebensmittelrettung als Ziel. |
| [Hygieneregeln, Version 12162](https://wiki.foodsharing.network/w/index.php?title=Hygieneregeln&oldid=12162) | Saubere lebensmittelechte Behälter; jedes Stück vor Weitergabe prüfen; keine Weitergabe nach Verbrauchsdatum oder bei Schimmel; Kühltransport; Hackfleisch und Kühlware mit unterbrochener Kühlkette sind bei nicht-persönlicher Weitergabe ausgeschlossen. |
| [Fairteiler, Version 12434](https://wiki.foodsharing.network/w/index.php?title=Fairteiler:Fairteiler_und_Abgabestellen&oldid=12434) | Fairteiler als Ort zum Teilen; Abgrenzung zu persönlicher Übergabe. |

Das Spiel bildet ausgewählte Situationen ab. Die Übungsfragen sind kein
Nachbau des offiziellen Quiz. Drei erfolgreiche Spieltouren erzeugen keinen
realen Foodsaver-Ausweis. Die frühere pauschale Behauptung „Hackfleisch retten
ist verboten“ und die fiktive automatische Sperre nach drei gelben Karten
wurden entfernt.

Layoutreferenz: [foodsharing-Repository](https://gitlab.com/foodsharing-dev/foodsharing),
Branch `master`, insbesondere `client/src/scss/theme/light.scss`
(Braun #533a20, Grün #64ae24), `bootstrap-theme.scss` (Karten und Rundungen),
`navigation.scss` (responsive Navigation und Fokuszustände) und
`client/src/layouts/Default.vue` (Navigation, Meldungen, Inhaltsbereich).
Keine Logos, Fotos oder Audiodateien wurden aus dem Projekt übernommen.

## Satirischer Roguelike-Modus

Der separate Modus „Operation Restglück“ verwendet frei erfundene Waffen,
Gegner, Duelle, Werte für Verderb und Verdauung sowie Level und Permadeath.
Diese Zahlen sind keine Wiki-Regeln oder medizinischen Empfehlungen. Im
Spiel-Fairteiler werden verdorbene Lebensmittel und Kühlwaren ausgeschlossen;
dies ist eine vereinfachte Spielauswahl, keine vollständige Hygieneprüfung.
Das Hotseat-Duell ist lokales PvP für zwei Menschen, die Routenarena ein
explizit als NPC gekennzeichnetes Trainingsduell.

## BOTS und Vorfälle im RPG

BOTS bezeichnet die Botschafter*innen-Rolle. Die Figur Sam, ihr Postfach und
alle Vertrauenswerte sind erfunden. Die neuen Rückfragen verwenden ausschließlich
bereits oben belegte Regeln: keine nicht-persönliche Weitergabe von Kühlware
mit unterbrochener Kühlkette; einzelne Lebensmittel vor Weitergabe prüfen;
Abholzusagen zuverlässig erfüllen und rechtzeitig Ersatz organisieren.
Die Reaktionen im Spiel bilden weder das offizielle Meldesystem noch dessen
Sanktionen ab. Eine misslungene Probe wird nicht als Regelverstoß behandelt.

## Wording-Abgleich mit dem Wiki (12.11.2026)

Ausgehend von der [Hauptseite, Version 13166](https://wiki.foodsharing.network/w/index.php?title=Hauptseite&oldid=13166)
wurden folgende Artikel erneut gelesen und für die Begriffe im Spiel verwendet:

| Quelle | Verwendung im Spiel |
| --- | --- |
| [Botschafter*in, Version 12940](https://wiki.foodsharing.network/w/index.php?title=Bezirke:Botschafter*in&oldid=12940) | BOT / BOTs; Koordination im Bezirk und Erfahrungsaustausch, keine alleinige Entscheidungsgewalt. Sam übernimmt diese Rolle. |
| [Betriebsverantwortliche*r, Version 12312](https://wiki.foodsharing.network/w/index.php?title=Betriebsverantwortliche*r&oldid=12312) | BV als Ansprechpersonen für Kooperation, Abholtermine und Betriebsteam. Robin übernimmt diese Rolle. |
| [Betrieb, Version 12917](https://wiki.foodsharing.network/w/index.php?title=Betrieb&oldid=12917) | Kooperation, Betriebsteam, Betriebsseite, vereinbarte Abholtermine. |
| [Verhaltensregeln, Version 12198](https://wiki.foodsharing.network/w/index.php?title=Verhaltensregeln&oldid=12198) | B6: Rücksicht und ordentlicher Abholort; C1: Betriebs-Besonderheiten, Pinnwand, Teamchat; C3: unverzüglich austragen, Ersatz im Team suchen, unter 24 Stunden auch telefonisch, im Notfall BV anrufen. |
| [Fairteilung, Version 12317](https://wiki.foodsharing.network/w/index.php?title=Fairteilung&oldid=12317) | Bedingungslose, kostenlose Weitergabe, etwa persönlich, als Essenskorb oder über Fairteiler; keine Bezahlung oder Spende für Lebensmittel. |
| [Regelverletzungen – Konsequenzen und Bearbeitung, Version 12941](https://wiki.foodsharing.network/w/index.php?title=Regelverletzungen_-_Konsequenzen_und_Bearbeitung&oldid=12941) | Persönliche Klärung und Lösung im Einzelfall; Unterscheidung von MRV und persönlicher Gesprächsnotiz; grundsätzliche Zuständigkeit der LMG und Vertraulichkeit. |

Der bisherige Spielwert „Bezirksvertrauen“ heißt nun **Zusammenhalt (Spielwert)**.
Er ist keine Vertrauensbanane, Abholquote oder offizielle Bewertung. Die fünf
Abholtage finden im selben Stammbezirk statt; Stadtviertel sind keine fünf
verschiedenen Bezirke. Persönliche Notizen in dieser Spielsitzung sind kein
formelles Meldungsregister und bilden auch keine Aufbewahrungs- oder
Tilgungsregeln ab. Die acht Betriebsseiten sind erfundene lokale Absprachen;
sie werden ausdrücklich nicht als allgemeine Regeln ausgegeben.

## Spielbare Wiki-Abläufe: Vorbereitung und Weitergabe (12.11.2026)

Erneut gelesen wurden Verhaltensregeln (Version 12198), Hygieneregeln (12162),
Fairteilung (12317) und Fairteiler und Abgabestellen (12434), jeweils oben verlinkt,
sowie die [Checkliste für Einführungsabholungen, Version 12632](https://wiki.foodsharing.network/w/index.php?title=Verhaltensregeln:Einführungsabholung_-_Checkliste&oldid=12632).

- **Abholbriefing:** Ausweis mitführen (B1), gemeinsam eintreten und abholen
  (B3), Tragehilfen außerhalb des Betriebs (B5), Rücksicht und keine Diskussion
  im Betrieb (B6), Wartezeit bis 15 Minuten akzeptieren, danach höflich absagen
  können (B7), auch bei unfreundlichem Verhalten höflich bleiben und ggf. BV
  informieren (B8), aktuelle Besonderheiten, Pinnwand und Teamchat kennen (C1).
- **Material:** Hygieneregeln B1: saubere, lebensmittelechte Verpackungen;
  für unverpackte Backwaren Gebäckzange, geeignete Handschuhe oder sorgfältig
  gewaschene Hände. Die Vorbereitungs-Checkboxen sind eine Spielsimulation.
- **Datum:** Im Fairteiler-Artikel ist Weitergabe nach MHD grundsätzlich
  möglich, sofern die weiteren Voraussetzungen erfüllt sind. Nach
  Verbrauchsdatum ist sie verboten. Dies tragen zwei Wissenssituationen ins
  Spiel; die abstrakten Frische-Runden sind keine Datumsprüfung.
- **Wege der Fairteilung:** Der Artikel Fairteilung nennt persönliche
  Weitergabe, Essenskorb, Fairteiler und weitere Abgabestellen. Ein Essenskorb
  wird im Spiel ausschließlich mit persönlicher Abholabsprache abgebildet.
  Es wird weder eine echte Anzeige erstellt noch eine generelle Gleichsetzung
  aller Essenskörbe mit einer bestimmten Hygienestufe behauptet.
- **Weitergabestufen:** Hygieneregeln B2 und C1/C2: jedes Stück auf
  Genießbarkeit prüfen; zusätzliche Ausschlüsse bei nicht-persönlicher
  Weitergabe; bei persönlicher Übergabe verantwortungsvolle Behandlung im
  Einzelfall einschätzen, nötige Hinweise geben und keine Lebensmittel nach
  längerer Unterbrechung der Kühlkette weitergeben. Zubereitete warme oder
  kühlbedürftige Speisen im Spiel nur persönlich weitergeben.
- **Hygieneplan:** Fairteiler-Artikel: tägliche Kühlschranktemperaturkontrolle,
  etwa 5 °C; regelmäßige Kontrolle, mindestens alle zwei Tage, Reinigung bei
  Bedarf und Dokumentation im Hygieneplan. Die Spielmessung ist fest und
  fiktiv. Die wöchentliche Reinigung wird nicht zeitgetreu simuliert.

Ausgewählte, vereinfachte Fälle: Die Spiel-Itemliste enthält beispielsweise
keinen Alkohol und keine geöffneten Packungen. Ein positiver Itemstatus bildet
keine vollständige rechtliche oder hygienische Freigabe ab. Die Regeln gelten
unabhängig von Attributen und Würfelergebnissen; nur der RPG-Aufwand wird gewürfelt.

## Erweiterter Itemkatalog und Tonnenrunden

`catalog.py`, `physiology.py` und `salvage.py` erweitern die frei erfundenen
RPG-Mechaniken. Die neuen Handschuh-, Masken-, Reparatur-, Buff- und
Verdauungswerte werden nicht aus dem Wiki oder aus Produktzertifizierungen
abgeleitet. Sie sind weder medizinische Effekte noch Arbeitsschutzwerte.
Tonnenrunden sind fiktive, abgesprochene Sortieraktionen mit Material aus
freigegebenen Beständen. Es werden dort keine Lebensmittel als geeignet zur
Weitergabe bewertet. Die bisherigen Wiki-Regeln zur Weitergabe bleiben
unabhängig von Ausrüstung, temporären Boni und Stat-Checks wirksam.
