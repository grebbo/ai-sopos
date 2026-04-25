import os
import pytest
from unittest.mock import patch


def test_app_importabile():
    import app
    assert app.app is not None


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
