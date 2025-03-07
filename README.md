# STADS_Datathon2025

## Installation
Python 3.13
```bash
pip install -r requirements.txt
```

## Loading OpenAI Key
```python

from dotenv import load_dotenv
import os


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
```

Was ist der Effekt auf die Infektionrate

Für jedes Bundesland


Prompt: Wir machen eine Impfkampanie. Auf Basis der folgenden Daten und deinem Wissen über die Region, schätze, wie sich dies auf die Infektionsrate auswirkt 
Eingabe: 
- Bundesland
- Woche und Year, Monat
- Infizierte Anzahl an Personen (auf BL Ebene)
- Daten über Impfungen nach Identifiern 
- Aktuelle Infektionsrate


Ausgabe Infektionsrate