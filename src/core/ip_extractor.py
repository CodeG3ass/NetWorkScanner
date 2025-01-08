import re
import ipaddress
import threading
from typing import Set, Tuple

class IPExtractor:
    @staticmethod
    def extract_ips(file_path: str) -> Tuple[Set[str], Set[str]]:
        """
        Извлекает IP-адреса и диапазоны IP из указанного файла.
        """
        ip_addresses: Set[str] = set()

        # Создаем поток для обработки файла
        IPExtractor.process_file_in_thread(file_path, ip_addresses)

        # Ожидаем завершения обработки
        return IPExtractor.categorize_ip(ip_addresses)

    @staticmethod
    def process_file_in_thread(file_path: str, ip_addresses: Set[str]) -> None:
        """
        Обрабатывает файл в отдельном потоке.
        """
        thread = threading.Thread(target=IPExtractor.process_file, args=(file_path, ip_addresses))
        thread.start()
        thread.join()  # Ожидаем завершения потока

    @staticmethod
    def process_file(file_path: str, ip_addresses: Set[str]) -> None:
        """
        Обрабатывает файл, извлекая IP-адреса или диапазоны IP.
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    IPExtractor.process_line(line, ip_addresses)
        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")

    @staticmethod
    def process_line(line: str, ip_addresses: Set[str]) -> None:
        """
        Обрабатывает строку из файла и извлекает IP-адреса или диапазоны IP.
        """
        ip_range = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}-\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', line)
        if ip_range:
            # Если диапазон IP-адресов найден, обрабатываем его
            IPExtractor.process_ip_range(ip_range.group(), ip_addresses)
        else:
            ip_address = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:\/[0-9]{1,2})?\b', line)
            if ip_address:
                # Если IP-адрес найден, обрабатываем его
                IPExtractor.process_single_ip(ip_address.group(), ip_addresses)

    @staticmethod
    def process_ip_range(ip_range: str, ip_addresses: Set[str]) -> None:
        """
        Обрабатывает диапазон IP-адресов и добавляет все IP из диапазона в множество.
        """
        start_ip, end_ip = ip_range.split('-')
        start_ip = ipaddress.ip_address(start_ip)
        end_ip = ipaddress.ip_address(end_ip)
        for ip in range(int(start_ip), int(end_ip) + 1):
            # Добавляем каждый IP-адрес в множество
            ip_addresses.add(str(ipaddress.ip_address(ip)))

    @staticmethod
    def process_single_ip(ip_str: str, ip_addresses: Set[str]) -> None:
        """
        Обрабатывает одиночный IP-адрес или сеть и добавляет все хосты в множество.
        """
        ip_network = ipaddress.ip_network(ip_str, strict=False)
        for ip in ip_network.hosts():
            # Добавляем каждый IP-адрес в множество
            ip_addresses.add(str(ip))

    @staticmethod
    def categorize_ip(ip_addresses: Set[str]) -> Tuple[Set[str], Set[str]]:
        """
        Распределяет IP-адресы по категориям: локальные и глобальные.
        """
        global_ips: Set[str] = set()
        local_ips: Set[str] = set()

        ip_addresses = sorted(ip_addresses, key=lambda ip: ipaddress.ip_address(ip))

        for ip in sorted(ip_addresses):
            if ipaddress.ip_address(ip).is_private:
                local_ips.add(str(ip))
            else:
                global_ips.add(str(ip))

        return global_ips, local_ips
