import unittest
from unittest.mock import patch, mock_open
from io import StringIO
from ipaddress import ip_address
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from core.ip_extractor import IPExtractor

class TestIPExtractor(unittest.TestCase):
    
    @patch("builtins.open", new_callable=mock_open, read_data="192.168.0.1\n10.0.0.1-10.0.0.5\n172.16.0.0/30\n")
    def test_extract_ips(self, mock_file):
        # Arrange
        file_path = "test.txt"
        
        # Act
        global_ips, local_ips = IPExtractor.extract_ips(file_path)

        # Assert
        expected_global_ips = {"172.16.0.1", "172.16.0.2"}
        expected_local_ips = {"192.168.0.1", "10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5"}

        self.assertEqual(global_ips, expected_global_ips)
        self.assertEqual(local_ips, expected_local_ips)

    @patch("builtins.open", new_callable=mock_open, read_data="192.168.0.1\n10.0.0.1-10.0.0.5\n")
    def test_process_file_in_thread(self, mock_file):
        # Arrange
        file_path = "test.txt"
        
        # Act
        ip_addresses = set()
        IPExtractor.process_file_in_thread(file_path, ip_addresses)

        # Assert
        expected_ips = {"192.168.0.1", "10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5"}
        self.assertEqual(ip_addresses, expected_ips)

    @patch("builtins.open", new_callable=mock_open, read_data="10.0.0.1-10.0.0.2\n192.168.1.1\n")
    def test_process_ip_range(self, mock_file):
        # Arrange
        ip_addresses = set()
        ip_range = "10.0.0.1-10.0.0.2"
        
        # Act
        IPExtractor.process_ip_range(ip_range, ip_addresses)

        # Assert
        expected_ips = {"10.0.0.1", "10.0.0.2"}
        self.assertEqual(ip_addresses, expected_ips)

    def test_process_single_ip(self):
        # Arrange
        ip_addresses = set()
        ip_str = "10.0.0.0/30"
        
        # Act
        IPExtractor.process_single_ip(ip_str, ip_addresses)

        # Assert
        expected_ips = {"10.0.0.1", "10.0.0.2"}
        self.assertEqual(ip_addresses, expected_ips)

    def test_categorize_ip(self):
        # Arrange
        ip_addresses = {"192.168.0.1", "10.0.0.1", "8.8.8.8"}
        
        # Act
        global_ips, local_ips = IPExtractor.categorize_ip(ip_addresses)
        
        # Assert
        expected_global_ips = {"8.8.8.8"}
        expected_local_ips = {"192.168.0.1", "10.0.0.1"}
        
        self.assertEqual(global_ips, expected_global_ips)
        self.assertEqual(local_ips, expected_local_ips)

if __name__ == "__main__":
    unittest.main()
