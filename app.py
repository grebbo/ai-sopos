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
    return render_template('index.html',
                           themes=THEMES,
                           lengths=list(LENGTHS.keys()),
                           history=get_history(),
                           story=None,
                           error=None,
                           form={})


if __name__ == '__main__':
    app.run(debug=True)
