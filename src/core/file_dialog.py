from tkinter import filedialog


class FileDialogHelper:
    @staticmethod
    def open_files():
        return filedialog.askopenfilenames(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    
    @staticmethod
    def open_folder() -> str:
        """
        Открывает диалоговое окно для выбора папки и возвращает путь к выбранной папке.
        """
        folder_path = filedialog.askdirectory(title="Select Folder")
        return folder_path
    
    @staticmethod
    def open_file(dir):
        return filedialog.askopenfilenames(initialdir = dir, title="Select IP file")
