# ai-sopos

Applicativo Python per la generazione di fiabe per bambini tramite API OpenAI. Disponibile sia come tool CLI che come interfaccia web Flask.

## Funzionalità principali

- Generazione casuale o guidata da parole chiave (usate come ispirazione, non letteralmente)
- Scelta del tema tra: `animali`, `fantasy`, `avventura`
- Lunghezza selezionabile: `corta` (~300 parole), `media` (~600), `lunga` (~1000)
- Titolo automatico generato dal modello e integrato nel nome del file di output
- Output su file `.txt` nella cartella `output/`
- **CLI**: anteprima in console con possibilità di rigenerare prima di salvare
- **Web**: storico delle ultime 10 fiabe, form per generare nuove storie

## Struttura

```
main.py             # CLI (argparse) ed entry point
generator.py        # Prompt OpenAI e parsing della risposta (titolo + corpo)
output.py           # Salvataggio su file con nome derivato dal titolo
config.py           # Costanti: modello, temi, lunghezze
app.py              # Flask app: route GET /, POST /genera, GET /storia/<filename>
templates/
  index.html        # Template unico: form + fiaba generata + storico
static/
  style.css         # CSS minimale senza framework esterni
tests/
  conftest.py       # Fixture client Flask con tmp_path
  test_app.py       # Test per tutte le route e get_history()
Dockerfile          # Immagine Python 3.12-slim + Gunicorn
docker-compose.yml  # Servizio con volume output/ e riavvio automatico
```

## Modello

`gpt-4o-mini` — economico, sufficiente per testi creativi brevi.

## Variabili d'ambiente

`OPENAI_API_KEY` — caricata da `.env` tramite `python-dotenv`. Il file `.env` non è versionato.

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

Il container si lega su `0.0.0.0:5000`. Con Tailscale attivo sul server host, l'app è raggiungibile dalla rete Tailscale all'indirizzo:

```
http://<tailscale-ip>:5000
```

Trovare l'IP Tailscale del server: `tailscale ip`

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
