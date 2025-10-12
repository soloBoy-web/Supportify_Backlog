from unittest.mock import patch

from app_main.views import welcome_page

from app_main.tests.tools import mock_request


class TestWelcomePageView:
    
    def test_uses_correct_template(self, mock_request):
        """Использование правильного шаблона"""
        with patch('app_main.views.render') as mock_render:
            welcome_page(mock_request)
            
            mock_render.assert_called_once()
            call_args = mock_render.call_args
            assert call_args[1]['template_name'] == 'app_main/welcome_page.html'
    
    def test_uses_correct_context(self, mock_request):
        """Проверка что контекст заполнен правильно"""
        with patch('app_main.views.render') as mock_render:
            welcome_page(mock_request)
            
            mock_render.assert_called_once()
            call_args = mock_render.call_args
            expected_context = {
                'title': 'Добро пожаловать!',
                'content': 'Это базовый HTML шаблон, который включает в себя все основные элементы веб-страницы.',
                'additional_content': 'Вы можете использовать его как отправную точку для создания своего сайта.'
            }
            assert call_args[1]['context'] == expected_context
