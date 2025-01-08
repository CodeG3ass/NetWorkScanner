import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import tempfile
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import nmap

from core.nmap_runner import NmapRunner  # Предположим, что ваш класс находится в файле nmap_runner.py

class TestNmapRunner(unittest.TestCase):

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('os.path.exists', return_value=True)
    @patch('nmap.PortScanner')
    def test_run_nmap_success(self, MockPortScanner, mock_exists, mock_open):
        # Создание временного файла с IP-адресами
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b'192.168.1.1\n192.168.1.2\n')
            temp_file_path = temp_file.name

        # Мокаем создание экземпляра PortScanner
        mock_scanner = MagicMock()
        MockPortScanner.return_value = mock_scanner

        # Мокаем сохранение результатов
        mock_save = MagicMock()
        nmap_runner = NmapRunner()
        nmap_runner.save_results = mock_save

        # Запуск метода
        result = nmap_runner.run_nmap(temp_file_path, 'output_prefix', None)

        # Проверка, что файл был открыт для чтения
        mock_open.assert_any_call(temp_file_path, 'r')
        # Проверка, что результаты были сохранены
        mock_save.assert_called_once()

        # Проверка, что возвращено ожидаемое сообщение
        self.assertIn('Сканирование завершено. Результаты сохранены.', result)

        # Удаляем временный файл
        os.remove(temp_file_path)

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('os.path.exists', return_value=True)
    @patch('nmap.PortScanner')
    def test_run_nmap_empty_ip_file(self, MockPortScanner, mock_exists, mock_open):
        # Создание временного пустого файла для IP-адресов
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        # Мокаем создание экземпляра PortScanner
        mock_scanner = MagicMock()
        MockPortScanner.return_value = mock_scanner

        # Мокаем сохранение результатов
        mock_save = MagicMock()
        nmap_runner = NmapRunner()
        nmap_runner.save_results = mock_save

        # Запуск метода с пустым файлом
        result = nmap_runner.run_nmap(temp_file_path, 'output_prefix', None)

        # Проверка, что возвращено ожидаемое сообщение
        self.assertIn('Сканирование завершено. Результаты сохранены.', result)

        # Удаляем временный файл
        os.remove(temp_file_path)

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('os.path.exists', return_value=True)
    @patch('nmap.PortScanner')
    def test_run_nmap_error_in_scan(self, MockPortScanner, mock_exists, mock_open):
        # Создание временного файла с IP-адресами
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b'192.168.1.1\n')
            temp_file_path = temp_file.name

        # Мокаем создание экземпляра PortScanner
        mock_scanner = MagicMock()
        MockPortScanner.return_value = mock_scanner
        mock_scanner.scan.side_effect = Exception("Ошибка при сканировании")

        # Мокаем сохранение результатов
        mock_save = MagicMock()
        nmap_runner = NmapRunner()
        nmap_runner.save_results = mock_save

        # Запуск метода
        result = nmap_runner.run_nmap(temp_file_path, 'output_prefix', None)

        # Проверка, что вернулось сообщение об ошибке
        self.assertIn('Ошибка при выполнении сканирования', result)

        # Удаляем временный файл
        os.remove(temp_file_path)

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('os.path.exists', return_value=False)
    @patch('nmap.PortScanner')
    def test_run_nmap_file_not_found(self, MockPortScanner, mock_exists, mock_open):
        # Мокаем создание экземпляра PortScanner
        mock_scanner = MagicMock()
        MockPortScanner.return_value = mock_scanner

        # Запуск метода с несуществующим файлом
        result = NmapRunner().run_nmap('non_existent_file.txt', 'output_prefix', None)

        # Проверка, что возвращено сообщение о том, что файл не найден
        self.assertIn('не найден. Проверьте путь и повторите попытку.', result)


if __name__ == '__main__':
    unittest.main()