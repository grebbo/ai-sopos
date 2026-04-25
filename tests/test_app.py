import os
import pytest
from unittest.mock import patch


def test_app_importabile():
    import app
    assert app.app is not None
