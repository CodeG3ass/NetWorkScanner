import unittest
from unittest.mock import patch
import sys
import os
from typing import Set, Tuple

# Добавил путь к src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.ip_extractor import IPExtractor

class TestIPExtractor(unittest.TestCase):
    def test_process_single_ip(self):
        ip_addresses = set()
        IPExtractor.process_single_ip("192.168.0.0/30", ip_addresses)
        expected_ips = {"192.168.0.1", "192.168.0.2"}  # Хосты в сети 192.168.0.0/30
        self.assertEqual(ip_addresses, expected_ips)

    def test_process_ip_range(self):
        ip_addresses = set()
        IPExtractor.process_ip_range("192.168.0.1-192.168.0.3", ip_addresses)
        expected_ips = {"192.168.0.1", "192.168.0.2", "192.168.0.3"}
        self.assertEqual(ip_addresses, expected_ips)

    def test_process_line_with_ip(self):
        ip_addresses = set()
        IPExtractor.process_line("192.168.0.1", ip_addresses)
        self.assertIn("192.168.0.1", ip_addresses)

    def test_process_line_with_ip_range(self):
        ip_addresses = set()
        IPExtractor.process_line("192.168.0.1-192.168.0.3", ip_addresses)
        expected_ips = {"192.168.0.1", "192.168.0.2", "192.168.0.3"}
        self.assertEqual(ip_addresses, expected_ips)

    def test_process_file(self):
        test_file_content = """192.168.0.1
192.168.0.2-192.168.0.3"""
        test_file_path = "test_ips.txt"

        with open(test_file_path, "w") as f:
            f.write(test_file_content)

        ip_addresses = set()
        IPExtractor.process_file(test_file_path, ip_addresses)

        expected_ips = {"192.168.0.1", "192.168.0.2", "192.168.0.3"}
        self.assertEqual(ip_addresses, expected_ips)

        os.remove(test_file_path)

    def test_categorize_ip(self):
        ip_addresses = {"192.168.0.1", "8.8.8.8"}
        global_ips, local_ips = IPExtractor.categorize_ip(ip_addresses)
        self.assertEqual(global_ips, {"8.8.8.8"})
        self.assertEqual(local_ips, {"192.168.0.1"})

    @patch("core.ip_extractor.IPExtractor.process_file_in_thread")
    def test_extract_ips(self, mock_process_file_in_thread):
        mock_process_file_in_thread.side_effect = lambda file_path, ip_addresses: ip_addresses.update({"192.168.0.1", "8.8.8.8"})

        global_ips, local_ips = IPExtractor.extract_ips("dummy_path")

        self.assertEqual(global_ips, {"8.8.8.8"})
        self.assertEqual(local_ips, {"192.168.0.1"})
        mock_process_file_in_thread.assert_called_once()

if __name__ == "__main__":
    unittest.main()