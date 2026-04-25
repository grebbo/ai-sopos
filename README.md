# ai-sopos — Generatore di Fiabe

Applicazione da riga di comando per generare fiabe per bambini tramite l'API OpenAI.
Ogni fiaba viene salvata automaticamente su file di testo con un titolo generato dal modello.

## Requisiti

- Python 3.10+
- Un account OpenAI con API key

## Installazione

```bash
pip install -r requirements.txt
```

Copia il file `.env.example` in `.env` e inserisci la tua API key:

```bash
cp .env.example .env
```

Contenuto di `.env`:

```
OPENAI_API_KEY=sk-...
```

## Utilizzo

### Vedere i temi disponibili

```bash
python main.py --temi
```

Output:

```
Temi disponibili:
  animali      — protagonisti animali parlanti con caratteri distinti, ...
  fantasy      — magia, draghi, streghe buone o cattive, regni incantati ...
  avventura    — esplorazioni coraggiose, viaggi in terre lontane, ...
```

### Generare una fiaba

```bash
# Tema casuale, lunghezza media (default)
python main.py --random

# Tema specifico
python main.py --tema fantasy

# Con parole chiave di ispirazione
python main.py --tema avventura --parole-chiave "faro, tempesta, coraggio"

# Scegliere la lunghezza
python main.py --tema animali --lunghezza corta
python main.py --tema fantasy --lunghezza lunga

# Nome file personalizzato
python main.py --tema fantasy --output la_mia_fiaba.txt

# Solo file, senza anteprima in console
python main.py --tema animali --no-preview
```

### Opzioni disponibili

| Opzione | Valori | Default | Descrizione |
|---|---|---|---|
| `--random` | — | — | Tema scelto casualmente |
| `--tema` | `animali` `fantasy` `avventura` | — | Tema della fiaba |
| `--temi` | — | — | Mostra i temi ed esce |
| `--parole-chiave` | stringa | — | Ispirazione tematica, separate da virgola |
| `--lunghezza` | `corta` `media` `lunga` | `media` | Lunghezza approssimativa |
| `--output` | nome file | auto | Nome file nella cartella `output/` |
| `--no-preview` | — | — | Non mostra la fiaba in console |

## Output

Le fiabe vengono salvate nella cartella `output/` (creata automaticamente).

Il nome del file è derivato dal titolo generato dal modello:

```
output/il_drago_gentile_20260425_143022.txt
```

Il file contiene titolo e testo:

```
Il Drago Gentile
================

C'era una volta, in un regno lontano lontano...
```

## Flusso interattivo

Dopo la visualizzazione in console, l'applicazione chiede se si vuole rigenerare la fiaba.
Rispondendo `s` viene prodotta una nuova versione con gli stessi parametri.
Il file viene salvato solo al termine, sulla versione finale approvata.

```
──────────────────────────────────────────────────────────
  Il Drago Gentile
──────────────────────────────────────────────────────────
C'era una volta...
──────────────────────────────────────────────────────────

Vuoi rigenerare la fiaba? (s/n):
```

## Struttura del progetto

```
ai-sopos/
├── main.py          # Entry point e CLI
├── generator.py     # Chiamata OpenAI e parsing titolo/testo
├── output.py        # Salvataggio su file
├── config.py        # Modello, temi, lunghezze
├── requirements.txt
├── .env.example
└── output/          # Fiabe generate (creata al primo avvio)
```
