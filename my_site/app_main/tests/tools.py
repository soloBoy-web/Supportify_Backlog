from unittest.mock import Mock

import pytest
from django.http import HttpRequest


@pytest.fixture
def mock_request():
    """Фикстура для создания мока запроса"""
    return Mock(spec=HttpRequest)
