# Chess AI Analyzer

## Übersicht

Chess AI Analyzer ist eine lokale Schachanalyse Anwendung, welche klassische Schachengines mit modernen Sprachmodellen kombiniert.

Die Software analysiert PGN Partien Zug für Zug mithilfe von Stockfish, erkennt kritische Momente wie Ungenauigkeiten, Fehler oder Blunder und generiert zusätzlich verständliche natürliche Kommentare zu den wichtigsten Stellungen.

Ziel des Projekts ist es, eine Analyseumgebung zu schaffen, die sowohl technisch präzise als auch für Menschen verständlich ist, ähnlich wie moderne Online-Schachplattformen, jedoch vollständig lokal und erweiterbar.


# Hauptfunktionen

##  Automatische Zuganalyse

Die Anwendung analysiert jede Stellung einer PGN-Partie mit der Stockfish-Engine und bewertet:

- beste Fortsetzung
- Bewertungsveränderungen
- Centipawn-Verlust
- kritische Fehler
- verpasste Chancen



##  Klassifikation von Fehlern

Züge werden automatisch klassifiziert als:

- Normaler Zug
- Ungenauigkeit (`?!`)
- Fehler (`?`)
- Blunder (`??`)
- Verpasste Chance


##  KI-gestützte Erklärungen

Zusätzlich zur Engineanalyse kann ein Sprachmodell genutzt werden, um Züge in natürlicher Sprache zu erklären.

Beispiele:

- Warum war ein Zug ein Fehler?
- Warum war die Alternative besser?
- Welche taktische Idee wurde übersehen?
- Erklärung für Anfänger oder Fortgeschrittene


## Interaktives Schachbrett

Die Anwendung enthält:

- vollständige Partienavigation
- Brettansicht jeder Stellung
- FEN-Anzeige
- Zugauswahl
- Anzeige kritischer Momente


## Kritische-Momente-Tabelle

Automatisch generierte Übersicht aller wichtigen Fehler der Partie inklusive:

- Symbol
- Klassifikation
- Kommentar
- Beste Fortsetzung
- Verpasste Chancen


# Architektur

Das Projekt ist modular aufgebaut.

## `app.py`

Streamlit-Weboberfläche.

Verantwortlich für:

- Benutzeroberfläche
- Navigation
- Brettdarstellung
- Tabellen
- Benutzerinteraktion


## `engine_service.py`

Kommunikation mit der Stockfish-Engine.

Verantwortlich für:

- Stellungsbewertung
- Berechnung bester Züge
- Principal Variation
- Centipawn-Verlust


## `analyzer.py`

Kernlogik der Partieanalyse.

Verarbeitet:

- PGN-Dateien
- Zugklassifikation
- Analyseobjekte
- Bewertungsketten


## `annotator.py`

Generiert natürlichsprachliche Kommentare und Klassifikationen.


## `llm_service.py`

Integration eines OpenAI-kompatiblen Sprachmodells.


## `models.py`

Dataclasses und Datenmodelle für Analyseobjekte.


# Verwendete Technologien

| Technologie | Zweck |
|---|---|
| Python 3.12 | Hauptsprache |
| Streamlit | Weboberfläche |
| python-chess | Schachlogik |
| Stockfish | Engineanalyse |
| OpenAI API | Sprachmodell |
| Pandas | Tabellendarstellung |



# Installation

## 1. Repository klonen

