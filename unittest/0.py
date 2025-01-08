import unittest
from unittest.mock import patch, MagicMock
from your_module import my_function

class TestMyFunction(unittest.TestCase):

    @patch('tkinter.filedialog.askopenfilenames')
    @patch('tkinter.filedialog.asksaveasfilename')
    @patch('tkinter.Text')
    @patch('tkinter.Button')
    @patch('tkinter.Tk')
    def test_my_function(self, mock_tk, mock_button, mock_text, mock_asksaveasfilename, mock_askopenfilenames):
        # Создаем мок-экземпляры для Tkinter-компонентов
        mock_tk_instance = MagicMock()
        mock_button_instance = MagicMock()
        mock_text_instance = MagicMock()

        # Устанавливаем возвращаемые значения для диалоговых окон и компонентов Tkinter
        mock_asksaveasfilename.return_value = 'test.txt'
        mock_askopenfilenames.return_value = ['test1.txt', 'test2.txt']
        mock_tk.return_value = mock_tk_instance
        mock_button.return_value = mock_button_instance
        mock_text.return_value = mock_text_instance

        # Вызов функцию, которую тестируете
        my_function()

        # Проверки, чтобы убедиться, что мок-методы были вызваны как ожидалось
        mock_askopenfilenames.assert_called_once()  # Проверяет, что диалог открытия файла был вызван
        mock_asksaveasfilename.assert_called_once()  # Проверяет, что диалог сохранения файла был вызван
        mock_tk_instance.mainloop.assert_called_once()  # Проверяет, что mainloop был вызван один раз

        # Дополнительные проверки
        mock_button_instance.configure.assert_called_once_with(bg='lightblue', fg='black', font=('Helvetica', 12))  # Проверка на конфигурацию кнопки
        mock_text_instance.insert.assert_called()  # Проверяет, что метод insert был вызван на mock_text_instance

if __name__ == '__main__':
    unittest.main()
