# Web Interface — AI-Sopos Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aggiungere un'interfaccia web Flask che permette di configurare e lanciare la generazione di fiabe dal browser, visualizzare la fiaba generata e consultare lo storico delle ultime 10.

**Architecture:** Flask app con 3 route (GET /, POST /genera, GET /storia/<filename>), singolo template Jinja2, CSS minimale. Il codice esistente (generator.py, output.py, config.py) viene riutilizzato senza modifiche. Lo storico è basato sui file .txt nella cartella output/ esistente.

**Tech Stack:** Python, Flask, Jinja2, pytest

---

## File Map

| File | Azione | Responsabilità |
|------|--------|----------------|
| `requirements.txt` | Modifica | Aggiungere `flask>=3.0.0` |
| `app.py` | Crea | Flask app, 3 route, helper `get_history()` |
| `templates/index.html` | Crea | Unico template: form + fiaba + storico |
| `static/style.css` | Crea | CSS minimale, nessun framework |
| `tests/__init__.py` | Crea | Marker package pytest |
| `tests/test_app.py` | Crea | Test delle route e degli helper |

---

### Task 1: Flask dependency e skeleton app

**Files:**
- Modify: `requirements.txt`
- Create: `app.py`
- Create: `tests/__init__.py`
- Create: `tests/test_app.py`

- [ ] **Step 1: Aggiungere flask a requirements.txt**

Il file diventa:

```
openai>=1.0.0
python-dotenv>=1.0.0
flask>=3.0.0
```

- [ ] **Step 2: Installare flask**

Run: `pip install flask`
Expected: `Successfully installed flask-...`

- [ ] **Step 3: Creare tests/__init__.py**

File vuoto — crea il package pytest.

- [ ] **Step 4: Scrivere il primo test (import dell'app)**

Contenuto di `tests/test_app.py`:

```python
import os
import pytest
from unittest.mock import patch


@pytest.fixture
def client(tmp_path):
    with patch('app.OUTPUT_DIR', str(tmp_path)):
        import app as flask_app
        flask_app.app.config['TESTING'] = True
        with flask_app.app.test_client() as c:
            yield c, tmp_path


def test_app_importabile():
    import app
    assert app.app is not None
```

- [ ] **Step 5: Eseguire il test — deve fallire**

Run: `pytest tests/test_app.py::test_app_importabile -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 6: Creare app.py minimale**

```python
import os
import random
from flask import Flask, render_template, request, redirect, url_for, abort

from config import THEMES, LENGTHS
from generator import generate_story
from output import save_story, OUTPUT_DIR

app = Flask(__name__)


if __name__ == '__main__':
    app.run(debug=True)
```

- [ ] **Step 7: Eseguire il test — deve passare**

Run: `pytest tests/test_app.py::test_app_importabile -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add requirements.txt app.py tests/__init__.py tests/test_app.py
git commit -m "feat: add Flask dependency and app skeleton"
```

---

### Task 2: Helper get_history() e route GET /

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app.py`
- Create: `templates/index.html`

- [ ] **Step 1: Aggiungere test per get_history() e GET /**

Aggiungere a `tests/test_app.py` dopo `test_app_importabile`:

```python
def test_get_history_vuota(tmp_path):
    with patch('app.OUTPUT_DIR', str(tmp_path)):
        import app
        assert app.get_history() == []


def test_get_history_ritorna_ultimi_10(tmp_path):
    for i in range(12):
        f = tmp_path / f"fiaba_{i:02d}.txt"
        f.write_text(f"Titolo {i}\n{'=' * 7}\n\nCorpo {i}", encoding='utf-8')
        os.utime(f, (i, i))

    with patch('app.OUTPUT_DIR', str(tmp_path)):
        import app
        history = app.get_history()

    assert len(history) == 10
    assert history[0]['filename'] == 'fiaba_11.txt'
    assert history[0]['title'] == 'Titolo 11'


def test_get_route_ritorna_200(client):
    c, _ = client
    response = c.get('/')
    assert response.status_code == 200


def test_get_route_contiene_form(client):
    c, _ = client
    html = c.get('/').data.decode('utf-8')
    assert 'action="/genera"' in html
    assert 'method="post"' in html
    assert 'name="tema"' in html
    assert 'name="lunghezza"' in html
    assert 'name="parole_chiave"' in html
```

- [ ] **Step 2: Eseguire i test — devono fallire**

Run: `pytest tests/test_app.py -v`
Expected: FAIL — `AttributeError: module 'app' has no attribute 'get_history'`

- [ ] **Step 3: Implementare get_history() in app.py**

Aggiungere dopo le import, prima di `app = Flask(__name__)`:

```python
def get_history():
    if not os.path.exists(OUTPUT_DIR):
        return []
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.txt')]
    files.sort(key=lambda f: os.path.getmtime(os.path.join(OUTPUT_DIR, f)), reverse=True)
    result = []
    for filename in files[:10]:
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, encoding='utf-8') as fh:
            title = fh.readline().strip()
        result.append({
            'filename': filename,
            'title': title,
            'mtime': os.path.getmtime(path),
        })
    return result
```

- [ ] **Step 4: Implementare route GET / in app.py**

Aggiungere dopo `app = Flask(__name__)`:

```python
@app.route('/')
def index():
    return render_template('index.html',
                           themes=THEMES,
                           lengths=list(LENGTHS.keys()),
                           history=get_history(),
                           story=None,
                           error=None,
                           form={})
```

- [ ] **Step 5: Creare la cartella templates/ e il file templates/index.html**

```html
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI-Sopos</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <div class="container">
    <header>
      <h1>AI-Sopos</h1>
      <p class="subtitle">Generatore di Fiabe</p>
    </header>

    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}

    <section class="form-section">
      <form action="/genera" method="post">
        <fieldset>
          <legend>Tema</legend>
          {% for key, desc in themes.items() %}
          <label>
            <input type="radio" name="tema" value="{{ key }}"
              {% if form.get('tema') == key %}checked{% endif %}>
            {{ key|capitalize }} — <small>{{ desc }}</small>
          </label>
          {% endfor %}
          <label>
            <input type="radio" name="tema" value="random"
              {% if not form.get('tema') or form.get('tema') == 'random' %}checked{% endif %}>
            Casuale
          </label>
        </fieldset>

        <div class="field">
          <label for="lunghezza">Lunghezza</label>
          <select name="lunghezza" id="lunghezza">
            {% for l in lengths %}
            <option value="{{ l }}" {% if form.get('lunghezza', 'media') == l %}selected{% endif %}>
              {{ l|capitalize }}
            </option>
            {% endfor %}
          </select>
        </div>

        <div class="field">
          <label for="parole_chiave">Parole chiave <small>(opzionale)</small></label>
          <input type="text" name="parole_chiave" id="parole_chiave"
            placeholder="es. mare, conchiglia, amicizia"
            value="{{ form.get('parole_chiave', '') }}">
        </div>

        <button type="submit">Genera</button>
      </form>
    </section>

    {% if story %}
    <section class="story-section">
      <h2>{{ story.title }}</h2>
      <div class="story-body">{{ story.body }}</div>
      <p class="saved-note">Salvata in <code>output/{{ story.filename }}</code></p>
    </section>
    {% endif %}

    <section class="history-section">
      <h3>Ultime fiabe generate</h3>
      {% if history %}
      <ul>
        {% for item in history %}
        <li>
          <a href="/storia/{{ item.filename }}">{{ item.title }}</a>
        </li>
        {% endfor %}
      </ul>
      {% else %}
      <p class="empty">Nessuna fiaba ancora generata.</p>
      {% endif %}
    </section>
  </div>
</body>
</html>
```

- [ ] **Step 6: Eseguire tutti i test**

Run: `pytest tests/test_app.py -v`
Expected: PASS per tutti i test scritti finora

- [ ] **Step 7: Commit**

```bash
git add app.py templates/index.html tests/test_app.py
git commit -m "feat: add get_history helper and GET / route"
```

---

### Task 3: GET / con parametro ?nuova= (visualizzazione fiaba appena generata)

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app.py`

- [ ] **Step 1: Aggiungere test per il parametro ?nuova=**

Aggiungere a `tests/test_app.py`:

```python
def test_get_route_con_nuova_mostra_storia(client):
    c, tmp_path = client
    f = tmp_path / "fiaba_test.txt"
    f.write_text(
        "Il drago biscottino\n====================\n\nC'era una volta un drago.",
        encoding='utf-8'
    )
    html = c.get('/?nuova=fiaba_test.txt').data.decode('utf-8')
    assert 'Il drago biscottino' in html
    assert "C'era una volta un drago." in html


def test_get_route_con_nuova_inesistente_non_crasha(client):
    c, _ = client
    response = c.get('/?nuova=file_inesistente.txt')
    assert response.status_code == 200
```

- [ ] **Step 2: Eseguire i test — devono fallire**

Run: `pytest tests/test_app.py::test_get_route_con_nuova_mostra_storia tests/test_app.py::test_get_route_con_nuova_inesistente_non_crasha -v`
Expected: FAIL — la storia non appare perché la route non gestisce ?nuova=

- [ ] **Step 3: Aggiornare GET / in app.py**

Sostituire la route `index()` con:

```python
@app.route('/')
def index():
    history = get_history()
    nuova = request.args.get('nuova')
    story = None
    if nuova:
        path = os.path.join(OUTPUT_DIR, nuova)
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                content = f.read()
            parts = content.split('\n', 2)
            story = {
                'title': parts[0].strip(),
                'body': parts[2].strip() if len(parts) > 2 else '',
                'filename': nuova,
            }
    return render_template('index.html',
                           themes=THEMES,
                           lengths=list(LENGTHS.keys()),
                           history=history,
                           story=story,
                           error=None,
                           form={})
```

- [ ] **Step 4: Eseguire tutti i test**

Run: `pytest tests/test_app.py -v`
Expected: tutti PASS

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_app.py
git commit -m "feat: show newly generated story via ?nuova= query param"
```

---

### Task 4: POST /genera

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app.py`

- [ ] **Step 1: Aggiungere test per POST /genera — caso successo**

Aggiungere a `tests/test_app.py`:

```python
def test_post_genera_redirect(client):
    c, tmp_path = client
    with patch('app.generate_story', return_value=('Titolo Test', 'Corpo test')), \
         patch('app.save_story', return_value=str(tmp_path / 'titolo_test.txt')):
        response = c.post('/genera', data={
            'tema': 'animali',
            'lunghezza': 'corta',
            'parole_chiave': '',
        })
    assert response.status_code == 302
    assert 'nuova=titolo_test.txt' in response.headers['Location']


def test_post_genera_passa_parametri_corretti(client):
    c, tmp_path = client
    with patch('app.generate_story', return_value=('T', 'B')) as mock_gen, \
         patch('app.save_story', return_value=str(tmp_path / 't.txt')):
        c.post('/genera', data={
            'tema': 'avventura',
            'lunghezza': 'lunga',
            'parole_chiave': 'mare, conchiglia',
        })
    mock_gen.assert_called_once_with('avventura', ['mare', 'conchiglia'], 'lunga')


def test_post_genera_tema_random_non_passa_random_alla_api(client):
    c, tmp_path = client
    with patch('app.generate_story', return_value=('T', 'B')) as mock_gen, \
         patch('app.save_story', return_value=str(tmp_path / 't.txt')), \
         patch('app.random.choice', return_value='fantasy'):
        c.post('/genera', data={'tema': 'random', 'lunghezza': 'media', 'parole_chiave': ''})
    called_theme = mock_gen.call_args[0][0]
    assert called_theme != 'random'
```

- [ ] **Step 2: Aggiungere test per POST /genera — casi errore**

Aggiungere a `tests/test_app.py`:

```python
def test_post_genera_environment_error_mostra_messaggio(client):
    c, _ = client
    with patch('app.generate_story', side_effect=EnvironmentError('API key mancante')):
        response = c.post('/genera', data={
            'tema': 'animali',
            'lunghezza': 'media',
            'parole_chiave': '',
        })
    assert response.status_code == 500
    assert b'API key mancante' in response.data


def test_post_genera_errore_generico_mostra_messaggio(client):
    c, _ = client
    with patch('app.generate_story', side_effect=Exception('timeout')):
        response = c.post('/genera', data={
            'tema': 'fantasy',
            'lunghezza': 'corta',
            'parole_chiave': '',
        })
    assert response.status_code == 500
    assert b'timeout' in response.data
```

- [ ] **Step 3: Eseguire i test — devono fallire**

Run: `pytest tests/test_app.py -k "genera" -v`
Expected: FAIL — `404 NOT FOUND` (la route non esiste)

- [ ] **Step 4: Implementare POST /genera in app.py**

Aggiungere dopo la route `index()`:

```python
@app.route('/genera', methods=['POST'])
def genera():
    tema = request.form.get('tema', 'random')
    lunghezza = request.form.get('lunghezza', 'media')
    parole_chiave = request.form.get('parole_chiave', '')
    keywords = [k.strip() for k in parole_chiave.split(',') if k.strip()]

    if tema == 'random':
        tema = random.choice(list(THEMES.keys()))

    try:
        title, body = generate_story(tema, keywords, lunghezza)
        filepath = save_story(title, body, tema)
        filename = os.path.basename(filepath)
        return redirect(url_for('index', nuova=filename))
    except EnvironmentError as e:
        error_msg = str(e)
    except Exception as e:
        error_msg = f"Errore durante la generazione: {e}"

    return render_template('index.html',
                           themes=THEMES,
                           lengths=list(LENGTHS.keys()),
                           history=get_history(),
                           story=None,
                           error=error_msg,
                           form={
                               'tema': request.form.get('tema'),
                               'lunghezza': lunghezza,
                               'parole_chiave': parole_chiave,
                           }), 500
```

- [ ] **Step 5: Eseguire tutti i test**

Run: `pytest tests/test_app.py -v`
Expected: tutti PASS

- [ ] **Step 6: Commit**

```bash
git add app.py tests/test_app.py
git commit -m "feat: implement POST /genera with error handling"
```

---

### Task 5: GET /storia/<filename>

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app.py`

- [ ] **Step 1: Aggiungere test per GET /storia/<filename>**

Aggiungere a `tests/test_app.py`:

```python
def test_get_storia_ritorna_contenuto(client):
    c, tmp_path = client
    f = tmp_path / "fiaba_prova.txt"
    f.write_text(
        "La lepre e la tartaruga\n========================\n\nC'era una volta...",
        encoding='utf-8'
    )
    response = c.get('/storia/fiaba_prova.txt')
    assert response.status_code == 200
    assert b'La lepre e la tartaruga' in response.data


def test_get_storia_inesistente_ritorna_404(client):
    c, _ = client
    assert c.get('/storia/inesistente.txt').status_code == 404


def test_get_storia_non_txt_ritorna_404(client):
    c, _ = client
    assert c.get('/storia/script.py').status_code == 404
```

- [ ] **Step 2: Eseguire i test — devono fallire**

Run: `pytest tests/test_app.py -k "storia" -v`
Expected: FAIL — `404 NOT FOUND`

- [ ] **Step 3: Implementare GET /storia/<filename> in app.py**

Aggiungere dopo la route `genera()`:

```python
@app.route('/storia/<filename>')
def storia(filename):
    if not filename.endswith('.txt'):
        abort(404)
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        abort(404)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
```

- [ ] **Step 4: Eseguire tutti i test**

Run: `pytest tests/test_app.py -v`
Expected: tutti PASS

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_app.py
git commit -m "feat: add GET /storia/<filename> route"
```

---

### Task 6: CSS e verifica manuale

**Files:**
- Create: `static/style.css`

- [ ] **Step 1: Creare la cartella static/ e il file static/style.css**

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: Georgia, 'Times New Roman', serif;
  background: #fdf8f0;
  color: #2c2c2c;
  line-height: 1.7;
}

.container {
  max-width: 720px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}

header {
  margin-bottom: 2rem;
  border-bottom: 2px solid #c8a96e;
  padding-bottom: 1rem;
}
header h1 { font-size: 2rem; color: #5c3d1e; }
header .subtitle { color: #888; font-style: italic; }

.error {
  background: #fdecea;
  border-left: 4px solid #c0392b;
  padding: .75rem 1rem;
  margin-bottom: 1.5rem;
  border-radius: 3px;
  color: #c0392b;
}

.form-section { margin-bottom: 2.5rem; }

fieldset {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
}
legend { font-weight: bold; padding: 0 .5rem; color: #5c3d1e; }
fieldset label { display: block; margin: .4rem 0; cursor: pointer; }
fieldset label input { margin-right: .5rem; }

.field { margin-bottom: 1rem; }
.field label { display: block; font-weight: bold; margin-bottom: .3rem; color: #5c3d1e; }
.field select,
.field input[type="text"] {
  width: 100%;
  padding: .5rem .75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
  background: #fff;
}

button[type="submit"] {
  background: #5c3d1e;
  color: #fff;
  border: none;
  padding: .75rem 2rem;
  font-size: 1rem;
  font-family: inherit;
  border-radius: 4px;
  cursor: pointer;
}
button[type="submit"]:hover { background: #7a5230; }

.story-section {
  background: #fff;
  border: 1px solid #e0cfa8;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
}
.story-section h2 { color: #5c3d1e; margin-bottom: 1rem; font-size: 1.5rem; }
.story-body { white-space: pre-wrap; }
.saved-note { margin-top: 1rem; font-size: .85rem; color: #888; }

.history-section { margin-top: 2rem; }
.history-section h3 { color: #5c3d1e; margin-bottom: .75rem; }
.history-section ul { list-style: none; }
.history-section li { padding: .3rem 0; border-bottom: 1px solid #eee; }
.history-section a { color: #5c3d1e; text-decoration: none; }
.history-section a:hover { text-decoration: underline; }

.empty { color: #aaa; font-style: italic; }
```

- [ ] **Step 2: Eseguire tutti i test per verificare nessuna regressione**

Run: `pytest tests/test_app.py -v`
Expected: tutti PASS

- [ ] **Step 3: Avviare il server e verificare manualmente**

Run: `python app.py`

Aprire `http://localhost:5000` nel browser e verificare:
- Header "AI-Sopos" e sottotitolo "Generatore di Fiabe" visibili
- Form con radio button temi (Animali, Fantasy, Avventura, Casuale — default Casuale), select lunghezza (default media), campo parole chiave, pulsante Genera
- Generare una fiaba (richiede `OPENAI_API_KEY` nel `.env`): la pagina deve ricaricarsi mostrando la fiaba
- La fiaba appare con titolo, corpo e nota "Salvata in output/..."
- Lo storico mostra le fiabe generate con link cliccabili
- Click su una voce dello storico apre il testo grezzo nel browser

- [ ] **Step 4: Commit finale**

```bash
git add static/style.css
git commit -m "feat: add CSS styling and complete web interface"
```
