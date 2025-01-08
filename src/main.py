from gui.app import GUIApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Network Scanner")
    root.geometry("800x600")
    app = GUIApp(root)
    root.mainloop()