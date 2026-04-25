# Web Interface Design — AI-Sopos

**Date:** 2026-04-25  
**Scope:** Aggiunta di un'interfaccia web Flask al progetto CLI esistente

---

## Contesto

AI-Sopos è un tool CLI Python che genera fiabe per bambini tramite OpenAI (gpt-4o-mini). Il codice esistente (`generator.py`, `output.py`, `config.py`, `main.py`) rimane invariato. Si aggiunge un layer web che riutilizza la stessa logica di generazione.

---

## Architettura

### Nuovi file

```
app.py                  # Flask app, routes, entry point web
templates/
  index.html            # unico template: form + fiaba + storico
static/
  style.css             # CSS minimale, nessun framework esterno
```

### File invariati

```
generator.py            # logica OpenAI, riutilizzata direttamente
output.py               # salvataggio .txt, riutilizzato direttamente
config.py               # costanti (MODEL, THEMES, LENGTHS)
main.py                 # CLI, continua a funzionare
```

### Dipendenze

Aggiungere `flask` a `requirements.txt`. Nessuna altra dipendenza nuova.

---

## Route e flusso dati

### `GET /`

- Legge la cartella `output/`, ordina i file `.txt` per data di modifica decrescente, prende i primi 10.
- Estrae il titolo di ogni file dalla prima riga (formato: `Titolo\n===...`).
- Se la query string contiene `?nuova=<filename>`, legge quel file e passa titolo + corpo al template per visualizzarli in cima.
- Renderizza `index.html`.

### `POST /genera`

- Riceve i parametri del form: `tema` (uno tra i temi o `random`), `lunghezza` (`corta`/`media`/`lunga`), `parole_chiave` (stringa opzionale).
- Se `tema == "random"` sceglie un tema a caso da `THEMES`.
- Chiama `generate_story(theme, keywords, lunghezza)`.
- Chiama `save_story(title, body, theme)`.
- Reindirizza a `/?nuova=<filename>` (PRG pattern).
- In caso di errore (es. API key mancante, timeout), mostra un messaggio di errore sulla stessa pagina senza perdere i parametri del form.

### `GET /storia/<filename>`

- Serve il contenuto grezzo del file `.txt` corrispondente da `output/`.
- Usato per aprire le fiabe dello storico.

---

## Layout UI

Pagina unica, struttura verticale, larghezza contenuto centrata (~700px), font leggibile.

1. **Header** — titolo "AI-Sopos", sottotitolo "Generatore di Fiabe"
2. **Form**
   - Tema: radio button (Animali / Fantasy / Avventura / Casuale)
   - Lunghezza: select (corta / media / lunga), default: media
   - Parole chiave: input testo opzionale, placeholder esplicativo
   - Pulsante "Genera"
3. **Fiaba generata** — visibile solo quando `?nuova=` è presente nella URL
   - Titolo in grande
   - Testo della storia
   - Nota: "Salvata in output/<filename>"
4. **Storico** — lista delle ultime 10 fiabe
   - Ogni voce: titolo + data/ora
   - Click apre la fiaba grezza (`/storia/<filename>`)
   - Se `output/` è vuota, messaggio "Nessuna fiaba ancora generata"

---

## Gestione errori

- API key mancante: messaggio visibile nella pagina, nessun crash del server.
- Errore OpenAI (timeout, quota): messaggio visibile, form mantenuto con i parametri precedenti.
- File non trovato in `/storia/<filename>`: risposta 404.

---

## Avvio

```bash
python app.py
# oppure
flask --app app run
```

Server locale su `http://localhost:5000`. La CLI (`python main.py`) continua a funzionare indipendentemente.

---

## Fuori scope

- Autenticazione
- Deploy su server remoto
- Funzionalità di rigenerazione (chi vuole una variante rimanda il form)
- Database (lo storico è basato sui file esistenti in `output/`)
