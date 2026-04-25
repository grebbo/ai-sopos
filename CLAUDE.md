# ai-sopos

Applicativo Python per la generazione di fiabe per bambini tramite API OpenAI.

## Funzionalità principali

- Generazione casuale o guidata da parole chiave (usate come ispirazione, non letteralmente)
- Scelta del tema tra: `animali`, `fantasy`, `avventura`
- Lunghezza selezionabile: `corta` (~300 parole), `media` (~600), `lunga` (~1000)
- Titolo automatico generato dal modello e integrato nel nome del file di output
- Anteprima in console con possibilità di rigenerare prima di salvare
- Output su file `.txt` nella cartella `output/`

## Struttura

```
main.py        # CLI (argparse) ed entry point
generator.py   # Prompt OpenAI e parsing della risposta (titolo + corpo)
output.py      # Salvataggio su file con nome derivato dal titolo
config.py      # Costanti: modello, temi, lunghezze
```

## Modello

`gpt-4o-mini` — economico, sufficiente per testi creativi brevi.

## Variabili d'ambiente

`OPENAI_API_KEY` — caricata da `.env` tramite `python-dotenv`.
