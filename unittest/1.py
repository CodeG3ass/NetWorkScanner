import unittest
from unittest.mock import patch, MagicMock
import unittest
from test import *

class TestMyFunction(unittest.TestCase):

    @patch('my_module.filedialog.askopenfilenames')
    @patch('my_module.open')
    @patch('my_module.ipaddress.ip_network')
    @patch('my_module.ipaddress.ip_address')
    def test_my_function(self, mock_ip_address, mock_ip_network, mock_open, mock_askopenfilenames):
        # Установка возвращаемые значения для mock-объектов
        mock_askopenfilenames.return_value = ['file1.txt', 'file2.txt']
        mock_open.return_value = MagicMock()
        mock_open.return_value.__enter__.return_value.readlines.return_value = ['192.168.1.1\n', '192.168.1.2\n']
        mock_ip_network.return_value.hosts.return_value = ['192.168.1.1', '192.168.1.2']
        mock_ip_address.return_value.is_private = True

        # Вызов функцию my_function
        my_module.my_function()

        # Проверка, что функция my_function вызвала ожидаемые методы
        mock_askopenfilenames.assert_called_once()
        mock_open.assert_called_with('file1.txt', 'r')
        mock_ip_network.assert_called_with('192.168.1.1', strict=False)
        mock_ip_address.assert_called_with('192.168.1.1')

        # Проверка, что функция my_function добавила ожидаемые IP-адреса в текстовые поля
        self.assertEqual(text_field2.get('1.0', tk.END), '192.168.1.1\n192.168.1.2\n')
        self.assertEqual(text_field.get('1.0', tk.END), '')

if __name__ == '__main__':
    unittest.main()
