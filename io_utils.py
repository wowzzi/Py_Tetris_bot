from tkinter import filedialog
from pathlib import Path

def get_json_file():
    path = filedialog.askopenfile("r", defaultextension=".json", filetypes=[("json files", "*.json")])
    if path:
        return Path(path.name)

if __name__ == "__main__":
    print(get_json_file())