
from unittest.mock import patch

from app_main.views import index

from app_main.tests.tools import mock_request


class TestIndexView:
    
    def test_uses_correct_template(self, mock_request):
        """Использование правильного шаблона"""
        with patch('app_main.views.render') as mock_render:
            
            index(mock_request)
            
            # Проверяем что render был вызван с правильным template_name
            mock_render.assert_called_once()
            call_args = mock_render.call_args
            assert call_args[1]['template_name'] == 'app_main/index.html'
    
    def test_uses_empty_context(self, mock_request):
        """Тест проверяет что контекст пустой"""
        with patch('app_main.views.render') as mock_render:
            # Вызов view функции
            index(mock_request)
            
            # Проверяем что render был вызван с пустым контекстом
            mock_render.assert_called_once()
            call_args = mock_render.call_args
            assert call_args[1]['context'] == {}
