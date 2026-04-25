import os
import random
from flask import Flask, render_template, request, redirect, url_for, abort

from config import THEMES, LENGTHS
from generator import generate_story
from output import save_story, OUTPUT_DIR

app = Flask(__name__)


if __name__ == '__main__':
    app.run(debug=True)
