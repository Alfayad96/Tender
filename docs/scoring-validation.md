# Scoring-Validierung

Stand: 24.08.2026

## Zweck und Datenbasis

Die Prüfung bewertet, ob die konservativen Kontextkorrekturen bestehende gute Entscheidungen erhalten, bekannte Fehlalarme reduzieren und abgelaufene Verfahren zuverlässig als nicht mehr aktiv behandeln.

Verwendet wurden die im privaten Repository vorhandenen Dateien `data/processed/erfolgreiche_tender.json` und `data/processed/teilweise_brauchbare_tender.json`. Die erwartete Granularität ist eine Ausschreibung pro Datensatz.

## Datenqualität

- 175 Datensätze und 41 beobachtete Felder
- 0 exakte Duplikate
- 163 eindeutige Ausschreibungs-IDs; 12 Datensätze ohne ID
- 14 Datensätze ohne strukturierten Detailstatus
- 33 Datensätze mit verwertbarer Frist; 142 ohne verwertbare Frist
- Die historischen Daten enthalten keine von Menschen bestätigte Ground Truth. Der Vergleich misst deshalb Regressionen und Regelplausibilität, nicht eine statistisch belegte Modellgenauigkeit.

## Änderungen mit fachlicher Begründung

1. `web app` löst nicht länger zusätzlich die Mobile-App-Gruppe über das Einzelwort `app` aus.
2. Kurze `AR`-/`VR`-Kürzel werden in eindeutigem Baukontext nicht als Extended Reality gewertet.
3. Allgemeine Wörter wie Support, Wartung, Betrieb, Lieferung, Beschaffung oder Einführung gelten allein nicht länger als schweres Ausschlusskriterium.
4. Ein Entwicklungs-/Relaunch-Projekt mit nachgeordnetem Hosting oder Support erhält eine kleine Betriebspönale; reine Betriebsleistungen bleiben klar negativ.
5. Konflikte aus stark positiven und stark negativen Gruppen gelangen nur bei einem ausreichend hohen Gesamtscore in die manuelle Prüfung.
6. Fristen werden anhand von Kalendertagen berechnet. Eine tatsächlich vergangene Frist hat Vorrang und führt zu `NICHT_AKTIV_BEREITS_VERGEBEN`; eine Frist am heutigen Tag bleibt prüfbar.
7. Relevante zusammengesetzte Begriffe und Pluralformen (`trainingssimulation`, `lernsimulation`, `laptops`, `notebooks`, `monitore`) sind abgedeckt.

## Vorher-/Nachher-Vergleich auf historischen Daten

| Bewertung | Vorher | Nachher |
| --- | ---: | ---: |
| PASSEND | 1 | 0 |
| MANUELL_PRUEFEN | 3 | 0 |
| NICHT_PASSEND | 35 | 11 |
| NICHT_AKTIV_BEREITS_VERGEBEN | 136 | 164 |

28 von 175 Entscheidungen änderten sich ausschließlich deshalb, weil ihre bekannte Frist am Stichtag bereits abgelaufen war. Alle 136 bereits als nicht aktiv erkannten Verfahren blieben unverändert. Bei 23 Datensätzen änderte sich der Score durch die präzisere Kontextbehandlung; die mittlere Veränderung unter diesen Fällen betrug +20 Punkte, bei einer Spannweite von -20 bis +46 Punkten.

## Repräsentative Regressionstests

Die automatisierten Tests decken unter anderem ab:

- eindeutig passende Besucher-App
- eindeutig passendes XR-Lernprojekt
- Website-Relaunch mit nachgeordnetem Support/Hosting
- reine Website-Betriebsleistung
- SAP-/ERP-Portal mit widersprüchlichen Signalen
- `VR` als Bauprojekt-Kürzel
- App-Beschaffung gegenüber echter Hardware-Beschaffung
- Software-Einführung gegenüber expliziter Beratung
- fehlende Informationen
- aufgehobene und bereits vergebene Verfahren
- abgelaufene Frist, Frist heute sowie die Fristgrenzen 21/10/5/4 Tage
- Wert `0` und fehlende Frontend-Felder

Ausführung:

```powershell
python -m unittest discover -v
```

## Validierungsurteil

Die Implementierung ist regressionsseitig bereit für die Live-Prüfung. Die Regeln bleiben erklärbar und deterministisch. Eine belastbare Precision-/Recall-Aussage ist ohne manuell gelabelte Referenzmenge nicht möglich; künftige fachlich bestätigte Fehlentscheidungen sollten als zusätzliche kleine Regressionstests ergänzt werden.
