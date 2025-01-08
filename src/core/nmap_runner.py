import nmap
import os
import threading
import queue
import csv
from openpyxl import Workbook
import tkinter as tk
from tkinter import filedialog

class NmapRunner:

    def __init__(self):
        self.nmap_path = [r"C:\Program Files (x86)\Nmap\nmap.exe",]

    def check_nmap_installed(self):
        try:
            nm = nmap.PortScanner(nmap_search_path=self.nmap_path)
            nm.nmap_version()
            return True
        except nmap.PortScannerError:
            return False
        except Exception as e:
            print(f"Ошибка при проверке Nmap: {e}")
            return False

    def run_nmap(self, ip_file, output_prefix, progress_callback=None, max_threads=10):
        """
        Выполняет сканирование с помощью Nmap через python-nmap с параллельными потоками и обратным вызовом для прогресса.
        """
        if not os.path.exists(ip_file):
            return f"Файл {ip_file} не найден. Проверьте путь и повторите попытку."

        try:
            nm = nmap.PortScanner(nmap_search_path=self.nmap_path)

            # Чтение IP-адресов из файла
            with open(ip_file, 'r') as file:
                ip_list = file.read().splitlines()

            results = []
            total_ips = len(ip_list)
            q = queue.Queue()  # Очередь для обмена данными между потоками

            def scan_ip(ip, index):
                """Функция для сканирования одного IP в потоке"""
                try:
                    scan_result = nm.scan(hosts=ip, arguments="-O -sS --top-ports 1000 -T2 -Pn")
                    results.append(scan_result)
                    q.put(f"Сканирование {index + 1}/{total_ips}: {ip} завершено.")
                except Exception as e:
                    q.put(f"Ошибка при сканировании {ip}: {e}")

            # Запуск потоков
            threads = []
            for index, ip in enumerate(ip_list):
                thread = threading.Thread(target=scan_ip, args=(ip, index))
                thread.start()
                threads.append(thread)

                # Если количество потоков достигло max_threads, ждем завершения
                if len(threads) >= max_threads:
                    for t in threads:
                        t.join()
                    threads = []  # Сбрасываем список потоков

            # Ждем завершения всех оставшихся потоков
            for t in threads:
                t.join()

            # Получаем результаты из очереди
            while not q.empty():
                message = q.get()
                if progress_callback:
                    progress_callback(message)

            # Спрашиваем у пользователя, куда сохранить результаты
            save_directory = self.ask_save_directory()

            if save_directory:
                # Сохраняем результаты в несколько форматов в выбранной папке
                self.save_results(results, save_directory, output_prefix)

            return f"Сканирование завершено. Результаты сохранены."

        except Exception as e:
            return f"Ошибка при выполнении сканирования: {e}"

    def ask_save_directory(self):
        """Запрашивает у пользователя директорию для сохранения файлов"""
        root = tk.Tk()
        root.withdraw()  # Скрыть основное окно
        save_directory = filedialog.askdirectory(title="Выберите папку для сохранения результатов")
        return save_directory

    def save_results(self, results, save_directory, output_prefix):
        """Сохраняет результаты в три формата: TXT, CSV и Excel в указанной папке."""

        # Сохранение в текстовый файл
        output_txt = os.path.join(save_directory, f"{output_prefix}.txt")
        with open(output_txt, 'w') as file:
            file.write(str(results))
        print(f"Результаты сохранены в {output_txt}")

        # Сохранение в CSV файл
        output_csv = os.path.join(save_directory, f"{output_prefix}.csv")
        with open(output_csv, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['IP', 'Status', 'Details'])  # Заголовки
            for result in results:
                for ip, data in result['scan'].items():
                    status = data.get('status', {}).get('state', 'Unknown')
                    details = str(data)  # Можно отформатировать, если нужно
                    writer.writerow([ip, status, details])
        print(f"Результаты сохранены в {output_csv}")

        # Сохранение в Excel файл
        output_xlsx = os.path.join(save_directory, f"{output_prefix}.xlsx")
        wb = Workbook()
        ws = wb.active
        ws.title = "Scan Results"
        ws.append(['IP', 'Status', 'Details'])  # Заголовки
        for result in results:
            for ip, data in result['scan'].items():
                status = data.get('status', {}).get('state', 'Unknown')
                details = str(data)  # Можно отформатировать, если нужно
                ws.append([ip, status, details])
        wb.save(output_xlsx)
        print(f"Результаты сохранены в {output_xlsx}")
