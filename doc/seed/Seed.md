# Seed Prompt für GitHub Copilot (Extended Thinking)

## Kontext
Du bist **GitHub Copilot** in einem Modus für **Extended Thinking**, strukturierte Softwareplanung und systematische Architekturarbeit. Deine Aufgabe ist **NICHT die Implementierung**, sondern die **strukturierte, tiefgehende Planung** eines professionellen Softwareprojekts.

Das Zielprojekt ist die Entwicklung eines **professionellen Digitalen Produktpasses (DPP)** basierend auf der **Verwaltungsschale (Asset Administration Shell, AAS)** gemäß den Konzepten von:
- https://industrialdigitaltwin.org/dpp4-0

Für die Backend-Implementierung soll das folgende Framework als Grundlage berücksichtigt werden:
- https://github.com/eclipse-basyx/basyx-python-sdk

Das System soll zusätzlich eine **Web-basierte Frontend-Anwendung** mit unterschiedlichen **Nutzerrollen und Sichten** enthalten.

---

## Ziel deiner Aufgabe

Erstelle eine **vollständige, strukturierte Projektplanung** für dieses System.

Die Planung soll:
- technisch fundiert
- architektonisch konsistent
- umsetzungsnah
- modular strukturiert
sein.

Du sollst dabei:
- Annahmen explizit machen
- Alternativen diskutieren
- sinnvolle Technologien vorschlagen
- Domänenlogik sauber modellieren
- Risiken und Entscheidungen transparent machen

Nutze dein Extended Thinking, um:
- implizite Anforderungen zu erkennen
- Systemgrenzen sauber zu definieren
- langfristige Skalierbarkeit zu berücksichtigen

---

## Zentrale Anforderungen an das Zielsystem

### Funktionale Ziele
- Abbildung eines **Digitalen Produktpasses** entlang des gesamten Lebenszyklus
- Nutzung der **Verwaltungsschale (AAS)** als Datenmodell
- Unterstützung von:
  - Produktdaten
  - Nachhaltigkeitsinformationen
  - Herkunft / Traceability
  - Zertifikate
  - Lifecycle Events

### Backend
- Nutzung des **BaSyx Python SDK**
- Bereitstellung von:
  - AAS-konformen APIs
  - Submodel-Handling
  - robuster Persistenz für Produktpassdaten, AAS, Submodelle, Benutzer- und Freigabedaten
- Planung einer geeigneten Persistenzstrategie, einschließlich:
  - Datenbankauswahl und Begründung
  - Datenmodellierung
  - Migrationsstrategie
  - Trennung von fachlichem Modell und Persistenzmodell
- Erweiterbarkeit für:
  - zusätzliche Submodelle
  - Integrationen (z. B. ERP, MES, IoT)
  - Import-/Export-Schnittstellen

### Frontend
- Web-Anwendung
- Rollenbasierte Sichten, z. B.:
  - Hersteller
  - Lieferant
  - Auditor
  - Endkunde
- Funktionen:
  - Visualisierung des Produktpasses
  - Bearbeitung von Daten (je nach Rolle)
  - Validierung / Freigabeprozesse

### Nicht-funktionale Anforderungen
- Skalierbarkeit
- Sicherheit & Compliance (z. B. EU DPP Anforderungen)
- Interoperabilität
- Wartbarkeit
- Erweiterbarkeit
- containerisierte Deploybarkeit mit Docker
- reproduzierbare lokale Entwicklungs- und Testumgebungen

---

## Vorgehensweise

1. Analysiere die Problemstellung tiefgehend
2. Leite strukturierte Anforderungen ab
3. Entwickle ein konsistentes Domänenmodell
4. Entwerfe eine Systemarchitektur
5. Definiere Module und Schnittstellen
6. Plane Umsetzung, Tests und Betrieb

Arbeite systematisch und nachvollziehbar.

---

## Ausgabeformat (WICHTIG)

Die Projektplanung muss in **mehrere Markdown-Dateien** aufgeteilt werden.

Alle Dateien sind im folgenden Verzeichnis abzulegen:

```
/doc/planning
│
├── 00_executive_summary.md
├── 01_stakeholder_roles.md
├── 02_requirements.md
├── 03_user_journeys.md
├── 04_domain_model.md
├── 05_system_architecture.md
├── 06_security_compliance.md
├── 07_modules.md
├── 08_backlog_roadmap.md
├── 09_testing_quality.md
├── 10_operations_observability.md
├── 11_risks_decisions.md
└── README.md
```

---

## Inhaltliche Anforderungen je Datei

### 00_executive_summary.md
- Zielbild des Systems
- Nutzenversprechen
- High-Level Architektur

### 01_stakeholder_roles.md
- Stakeholder-Analyse
- Rollenmodell
- Berechtigungen

### 02_requirements.md
- Funktionale Anforderungen
- Nicht-funktionale Anforderungen
- Priorisierung

### 03_user_journeys.md
- Use Cases
- User Flows
- Interaktionen

### 04_domain_model.md
- Entitäten
- Beziehungen
- Mapping zur AAS

### 05_system_architecture.md
- Architektur (z. B. Microservices vs. Monolith)
- Backend (BaSyx Integration)
- Frontend Architektur
- Persistenzarchitektur
- Schnittstellen
- Deployment-Topologie mit Docker

### 06_security_compliance.md
- Authentifizierung & Autorisierung
- Datenschutz
- DPP-relevante Regularien

### 07_modules.md
- Modulstruktur
- Verantwortlichkeiten
- Abhängigkeiten

### 08_backlog_roadmap.md
- MVP Definition
- Roadmap
- Meilensteine

### 09_testing_quality.md
- Teststrategie
- Qualitätssicherung

### 10_operations_observability.md
- Deployment mit Docker
- lokale Entwicklungsumgebung mit Docker Compose oder vergleichbarer Container-Orchestrierung für Entwicklung/Test
- Monitoring
- Logging
- Konfigurations- und Secrets-Management

### 11_risks_decisions.md
- Risiken
- Architekturentscheidungen
- Trade-offs

### README.md
- Überblick über die Planung
- Navigationshilfe

---

## Wichtige Leitlinien

- Schreibe die Planung so, dass sie **optimal mit GitHub Copilot** weiterverarbeitet werden kann
- Formuliere klar, eindeutig und umsetzungsnah
- Benenne empfohlene Verzeichnisstrukturen, Module, Schnittstellen und Artefakte explizit
- Denke **systemisch und langfristig**
- Vermeide unnötige Komplexität
- Begründe Architekturentscheidungen
- Nutze etablierte Patterns
- Stelle klare Schnittstellen sicher
- Berücksichtige durchgehend Persistenz, Deployment und Betriebsaspekte

---

## GitHub-Copilot-spezifische Arbeitsanweisungen

Erstelle die Planung so, dass sie von GitHub Copilot in einem Repository unmittelbar weiterverwendet werden kann. Das bedeutet insbesondere:
- konsistente Benennung von Modulen, Services, Verzeichnissen und Schnittstellen
- explizite Vorschläge für Backend-, Frontend- und Infrastrukturstruktur
- klare Abgrenzung zwischen Muss-, Soll- und Kann-Anforderungen
- konkrete Annahmen zu Technologien, wenn mehrere Optionen bestehen
- bei Alternativen: kurze Entscheidungsmatrix und empfohlene Wahl
- Formulierungen so präzise, dass daraus im nächsten Schritt Tickets, Issues, ADRs oder Codegerüste abgeleitet werden können

Berücksichtige zusätzlich:
- Backend-Persistenz ist **Pflichtbestandteil** der Planung
- Deployment mit **Docker** ist **Pflichtbestandteil** der Planung
- Es soll beschrieben werden, welche Container sinnvoll sind (z. B. Frontend, Backend, Datenbank, Reverse Proxy, optionale Observability-Komponenten)
- Es soll beschrieben werden, wie lokale Entwicklung, Test und Deployment mit Containern unterstützt werden

## Erwartetes Ergebnis

Eine **vollständig ausgearbeitete, professionelle Projektplanung**, die direkt als Grundlage für ein reales Softwareprojekt verwendet werden kann und optimal für die Weiterarbeit mit **GitHub Copilot** vorbereitet ist.

---

## Start

Beginne mit der Erstellung aller Dateien in der vorgegebenen Struktur.
Arbeite Schritt für Schritt und konsistent über alle Dokumente hinweg.

