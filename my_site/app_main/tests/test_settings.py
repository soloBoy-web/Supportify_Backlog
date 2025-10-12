from unittest.mock import patch

from app_main.views import settings

from app_main.tests.tools import mock_request


class TestSettingsView:
    
    def test_returns_correct_http_response(self, mock_request):
        """Проверка что возвращается правильный HttpResponse"""
        with patch('app_main.views.HttpResponse') as mock_http_response:
            settings(mock_request)
            
            mock_http_response.assert_called_once_with("<p> Третий запрос </p>")
