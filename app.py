import os
import random
from flask import Flask, render_template, request, redirect, url_for, abort

from config import THEMES, LENGTHS
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


app = Flask(__name__)


@app.route('/')
def index():
    history = get_history()
    nuova = request.args.get('nuova')
    if nuova:
        nuova = os.path.basename(nuova)
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


if __name__ == '__main__':
    app.run(debug=True)
