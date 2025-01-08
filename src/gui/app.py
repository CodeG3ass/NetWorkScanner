import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from core.nmap_runner import NmapRunner
from core.ip_extractor import IPExtractor
from core.file_dialog import FileDialogHelper
from ipaddress import ip_address, AddressValueError
from openpyxl import Workbook
from threading import Thread
import os
import csv
from typing import List, Set


class GUIApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.input_folder = "input"  # Путь к папке с входными файлами
        self.create_buttons()
        self.create_text_fields()

    def create_buttons(self):
        tk.Button(self.root, text="Load IPs", command=self.load_ips, bg="lightblue", fg="black", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(self.root, text="Save global", command=lambda: self.save_result(self.text_field, "global"), bg="lightblue", fg="black", font=("Helvetica", 12)).pack(side=tk.TOP, padx=10, pady=10)
        tk.Button(self.root, text="Save local", command=lambda: self.save_result(self.text_field2, "local"), bg="lightblue", fg="black", font=("Helvetica", 12)).pack(side=tk.BOTTOM, padx=10, pady=10)
        tk.Button(self.root, text="Run Nmap", command=self.run_nmap_from_input, bg="lightgreen", fg="black", font=("Helvetica", 12)).pack(side=tk.RIGHT, padx=10, pady=10)

    def create_text_fields(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.text_field = tk.Text(frame, height=10, width=50, bg="lightgray", fg="black", font=("Helvetica", 12), wrap=tk.WORD, bd=2, relief="solid")
        self.text_field.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.text_field2 = tk.Text(frame, height=10, width=50, bg="lightblue", fg="black", font=("Helvetica", 12), wrap=tk.WORD, bd=2, relief="solid")
        self.text_field2.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.text_field3 = tk.Text(frame, height=10, width=50, bg="lightgreen", fg="black", font=("Helvetica", 12), wrap=tk.WORD, bd=2, relief="solid")
        self.text_field3.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.text_field_scrollbar = tk.Scrollbar(self.text_field)
        self.text_field_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_field.config(yscrollcommand=self.text_field_scrollbar.set)
        self.text_field_scrollbar.config(command=self.text_field.yview)

        self.text_field2_scrollbar = tk.Scrollbar(self.text_field2)
        self.text_field2_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_field2.config(yscrollcommand=self.text_field2_scrollbar.set)
        self.text_field2_scrollbar.config(command=self.text_field2.yview)

        self.text_field3_scrollbar = tk.Scrollbar(self.text_field3)
        self.text_field3_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_field3.config(yscrollcommand=self.text_field3_scrollbar.set)
        self.text_field3_scrollbar.config(command=self.text_field3.yview)

    def save_result(self, text_field: tk.Text, filename: str):
        output_path = FileDialogHelper.open_folder()
        if not output_path:
            return
        
        self.save_text(text_field, os.path.join(output_path, f"{filename}.txt"))
        self.save_to_excel(text_field, os.path.join(output_path, f"{filename}.xlsx"))
        self.save_to_csv(text_field, os.path.join(output_path, f"{filename}.csv"))

    def save_text(self, text_field: tk.Text, global_file_path: str):
        try:
            with open(global_file_path, 'w') as file:
                file.write(text_field.get("1.0", tk.END))
            print(f"Файл сохранён по пути: {global_file_path}")
        except Exception as e:
            print("Ошибка при сохранении файла:", e)

    def save_to_csv(self, text_field: tk.Text, global_file_path: str):
        try:
            with open(global_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                text = text_field.get("1.0", "end-1c")
                result_lines = text.splitlines()
                for result in result_lines:
                    writer.writerow([result])

            print(f"Файл сохранён по пути: {global_file_path}")
        except Exception as e:
            print("Ошибка при сохранении файла:", e)

    def save_to_excel(self, text_field: tk.Text, global_file_path: str):
        try:
            wb = Workbook()
            sheet = wb.active
            sheet.title = "IPs"
            text = text_field.get("1.0", "end-1c")
            ip_addresses = text.splitlines()

            for row, ip in enumerate(ip_addresses, start=1):
                sheet.cell(row=row, column=1, value=ip)

            wb.save(global_file_path)
            print(f"Файл сохранён по пути: {global_file_path}")
        except Exception as e:
            print("Ошибка при сохранении файла:", e)

    def run_nmap_from_input(self):
        ip_file = filedialog.askopenfilename(title="Select IP File", filetypes=[("Text Files", "*.txt")])
        if not ip_file:
            return

        runner = NmapRunner()
        if runner.check_nmap_installed():
            result_message = runner.run_nmap(
                ip_file, 
                "nmap_scan_results", 
                progress_callback=self.update_progress,
                max_threads=10
            )
            print(result_message)
        else:
            print("Nmap не установлен или недоступен в PATH.")

    def update_progress(self, message: str):
        self.text_field3.insert(tk.END, message + "\n")
        self.text_field3.yview(tk.END)
        self.root.update_idletasks()

    def load_ips(self):
        file_paths = FileDialogHelper.open_files()
        
        gb_ips: List[str] = []
        loc_ips: List[str] = []
        
        for file_path in file_paths:
            print(file_path)
            global_ips, local_ips = IPExtractor.extract_ips(file_path)

            global_ips = [ip for ip in global_ips if self.is_valid_ip(ip)]
            local_ips = [ip for ip in local_ips if self.is_valid_ip(ip)]

            gb_ips.extend(global_ips)
            loc_ips.extend(local_ips)
                
        gb_ips = sorted(gb_ips, key=lambda ip: int(ip_address(ip)))
        loc_ips = sorted(loc_ips, key=lambda ip: int(ip_address(ip)))

        for ip in gb_ips:
            self.text_field.insert(tk.END, ip + '\n')

        for ip in loc_ips:
            self.text_field2.insert(tk.END, ip + '\n')

    def is_valid_ip(self, ip: str) -> bool:
        try:
            ip_address(ip)
            return True
        except AddressValueError:
            return False
