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
