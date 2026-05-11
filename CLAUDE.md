# ai-sopos

Applicativo Python per la generazione di fiabe per bambini tramite API OpenAI. Disponibile sia come tool CLI che come interfaccia web Flask.

## Funzionalità principali

- Generazione casuale o guidata da parole chiave (chip interattive, usate come ispirazione non letteralmente)
- Scelta del tema tra quelli configurati (default: `animali`, `fantasy`, `avventura`) — modificabili da `/impostazioni`
- Lunghezza selezionabile: `corta` (~300 parole, default), `media` (~600), `lunga` (~1000)
- Titolo automatico generato dal modello e integrato nel nome del file di output
- Output su file `.txt` nella cartella `output/`
- **CLI**: anteprima in console con possibilità di rigenerare prima di salvare
- **Web**: storico delle ultime 10 fiabe, form per generare nuove storie, pagina impostazioni
- **Impostazioni web** (`/impostazioni`): modifica prompt di sistema, temi (label, prompt, aggiungi/elimina), preferenze lettore (font size, dark mode, scroll speed) — in-memory, reset al riavvio

## Struttura

```
main.py             # CLI (argparse) ed entry point
generator.py        # Prompt OpenAI e parsing della risposta (titolo + corpo)
output.py           # Salvataggio su file con nome derivato dal titolo
config.py           # Costanti statiche: modello, lunghezze (non modificabili a runtime)
settings.py         # SETTINGS dict runtime: system_prompt, themes, reader prefs, default_length
app.py              # Flask app: /, /genera, /storia/<filename>, /cronologia, /impostazioni
templates/
  index.html        # Form generazione con chips parole chiave
  impostazioni.html # Pagina impostazioni (prompt, temi, preferenze lettore)
  storia.html       # Visualizzatore fiaba con reader preferences da sessione
  cronologia.html   # Storico ultime 10 fiabe
static/
  style.css         # CSS minimale senza framework esterni
tests/
  conftest.py       # Fixture client Flask con tmp_path
  test_app.py       # Test per tutte le route e get_history()
Dockerfile          # Immagine Python 3.12-slim + Gunicorn (1 worker)
docker-compose.yml  # Servizio con volume output/ e riavvio automatico
```

## Modello

`gpt-4o-mini` — economico, sufficiente per testi creativi brevi.

## Variabili d'ambiente

| Variabile | Obbligatoria | Descrizione |
|---|---|---|
| `OPENAI_API_KEY` | Sì | Caricata da `.env` tramite `python-dotenv`. |
| `SECRET_KEY` | Raccomandata | Chiave per firmare i cookie di sessione Flask. Se assente usa un fallback hardcoded (accettabile solo in sviluppo locale). |
| `TS_AUTHKEY` | Solo Docker/Tailscale | Auth key per il container sidecar Tailscale. |

Il file `.env` non è versionato.

## Avvio

### CLI

```bash
python main.py --random
python main.py --tema animali --lunghezza lunga --parole-chiave "mare, conchiglia"
python main.py --temi   # mostra i temi disponibili
```

### Web (sviluppo locale)

```bash
python app.py
# oppure
flask --app app run
```

Server su `http://localhost:5000`.

### Web (produzione via Docker)

```bash
docker compose up -d
```

Richiede il file `.env` con `OPENAI_API_KEY` nella root del progetto. Le fiabe vengono persistite nel volume `./output` del server host. Per aggiornare l'immagine dopo modifiche al codice:

```bash
docker compose up -d --build
```

## Deploy su home server con Tailscale

Il `docker-compose.yml` usa il pattern sidecar: il container `tailscale` gestisce tutta la rete, e `app` condivide il suo stack di rete (`network_mode: service:tailscale`). Il servizio è esposto sulla rete Tailscale con hostname `ai-sopos` sulla porta 5000:

```
http://ai-sopos:5000
```

Il file `.env` deve contenere anche `TS_AUTHKEY` (auth key generata dalla Tailscale admin console).

## Test

```bash
pytest tests/
```

I test usano un client Flask con directory `output/` temporanea (`tmp_path`) e mockano `generate_story` e `save_story` per non chiamare OpenAI.

## Formato file output

Ogni fiaba è salvata in `output/<slug-titolo>_<timestamp>.txt` con il formato:

```
Titolo della fiaba
==================

Corpo della storia...
```

La prima riga è il titolo (usato dallo storico web), il corpo inizia dopo la riga vuota.
