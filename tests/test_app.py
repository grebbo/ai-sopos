import os
import pytest
from unittest.mock import patch


def test_app_importabile():
    import app
    assert app.app is not None


def test_get_history_vuota(tmp_path):
    nonexistent = str(tmp_path / 'nonexistent')
    with patch('app.OUTPUT_DIR', nonexistent):
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


def test_get_route_con_nuova_mostra_storia(client):
    c, tmp_path = client
    f = tmp_path / "fiaba_test.txt"
    f.write_text(
        "Il drago biscottino\n====================\n\nC'era una volta un drago.",
        encoding='utf-8'
    )
    html = c.get('/?nuova=fiaba_test.txt').data.decode('utf-8')
    assert 'Il drago biscottino' in html
    assert "C&#39;era una volta un drago." in html


def test_get_route_con_nuova_inesistente_non_crasha(client):
    c, _ = client
    response = c.get('/?nuova=file_inesistente.txt')
    assert response.status_code == 200


def test_get_route_nuova_no_path_traversal(client):
    c, _ = client
    response = c.get('/?nuova=../app.py')
    assert response.status_code == 200
    assert b'def index' not in response.data


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
