import json
import os
import re
import random
from flask import Flask, render_template, request, redirect, url_for, abort, session

import settings
from config import LENGTHS
from generator import generate_story
from output import save_story, OUTPUT_DIR


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


def _make_slug(label: str) -> str:
    slug = label.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '_', slug)
    slug = slug.strip('_')[:32]
    return slug or 'tema'


def _unique_slug(slug: str, existing: set) -> str:
    if slug not in existing:
        return slug
    i = 2
    while f"{slug}_{i}" in existing:
        i += 1
    return f"{slug}_{i}"


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")


@app.route('/')
def index():
    return render_template('index.html',
                           themes=settings.SETTINGS["themes"],
                           lengths=list(LENGTHS.keys()),
                           default_length=settings.SETTINGS["default_length"],
                           error=None,
                           form={})


@app.route('/genera', methods=['POST'])
def genera():
    tema = request.form.get('tema', 'random')
    lunghezza = request.form.get('lunghezza', settings.SETTINGS["default_length"])
    parole_raw = request.form.get('parole_chiave_json', '[]')
    try:
        keywords = json.loads(parole_raw)
        if not isinstance(keywords, list):
            keywords = []
    except (json.JSONDecodeError, ValueError):
        keywords = []
    keywords = [str(k).strip() for k in keywords if str(k).strip()]

    if tema == 'random':
        tema = random.choice(list(settings.SETTINGS["themes"].keys()))

    try:
        title, body = generate_story(tema, keywords, lunghezza)
        filepath = save_story(title, body, tema)
        filename = os.path.basename(filepath)
        return redirect(url_for('storia', filename=filename))
    except EnvironmentError as e:
        error_msg = str(e)
    except Exception as e:
        error_msg = f"Errore durante la generazione: {e}"

    return render_template('index.html',
                           themes=settings.SETTINGS["themes"],
                           lengths=list(LENGTHS.keys()),
                           default_length=settings.SETTINGS["default_length"],
                           error=error_msg,
                           form={
                               'tema': request.form.get('tema'),
                               'lunghezza': lunghezza,
                               'parole_chiave_json': parole_raw,
                           }), 500


@app.route('/storia/<filename>')
def storia(filename):
    if not filename.endswith('.txt'):
        abort(404)
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        abort(404)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    parts = content.split('\n', 2)
    title = parts[0].strip()
    body = parts[2].strip() if len(parts) > 2 else ''
    reader = session.get('reader', settings.SETTINGS['reader'])
    return render_template('storia.html', title=title, body=body, filename=filename, reader=reader)


@app.route('/cronologia')
def cronologia():
    return render_template('cronologia.html', history=get_history())


@app.route('/impostazioni', methods=['GET'])
def impostazioni():
    return render_template('impostazioni.html', s=settings.SETTINGS)


@app.route('/impostazioni', methods=['POST'])
def salva_impostazioni():
    system_prompt = request.form.get('system_prompt', '').strip()[:1000]

    themes = {}
    existing_slugs: set = set()
    i = 0
    while f'theme_{i}_label' in request.form:
        label = request.form.get(f'theme_{i}_label', '').strip()
        prompt = request.form.get(f'theme_{i}_prompt', '').strip()
        if label and prompt:
            slug = _make_slug(label)
            slug = _unique_slug(slug, existing_slugs)
            existing_slugs.add(slug)
            themes[slug] = {'label': label, 'prompt': prompt}
        i += 1

    if not themes:
        themes = settings.SETTINGS['themes']

    font_size_index = int(request.form.get('font_size_index', 2))
    font_size_index = max(0, min(6, font_size_index))
    dark_mode = 'dark_mode' in request.form
    scroll_speed = int(request.form.get('scroll_speed', 3))
    scroll_speed = max(1, min(10, scroll_speed))

    settings.SETTINGS['system_prompt'] = system_prompt
    settings.SETTINGS['themes'] = themes
    settings.SETTINGS['reader'] = {
        'font_size_index': font_size_index,
        'dark_mode': dark_mode,
        'scroll_speed': scroll_speed,
    }
    session['reader'] = settings.SETTINGS['reader']

    return redirect(url_for('impostazioni', saved=1))


if __name__ == '__main__':
    app.run(debug=True)
