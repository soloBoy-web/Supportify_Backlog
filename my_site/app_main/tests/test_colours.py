from unittest.mock import patch

from app_main.views import colours

from app_main.tests.tools import mock_request


class TestColoursView:
    
    def test_uses_correct_template(self, mock_request):
        """Использование правильного шаблона"""
        with patch('app_main.views.render') as mock_render:

            colours(mock_request)
            
            mock_render.assert_called_once()
            call_args = mock_render.call_args
            assert call_args[1]['template_name'] == 'app_main/colours.html'
    
    def test_uses_empty_context(self, mock_request):
        """Проверка что контекст пустой"""
        with patch('app_main.views.render') as mock_render:
            
            colours(mock_request)
            
            mock_render.assert_called_once()
            call_args = mock_render.call_args
            assert call_args[1]['context'] == {}
