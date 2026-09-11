"""
Desktop Manager
---------------
A tiny Windows utility with two tools:

1. Wallpaper Loadout  - save a few wallpapers with names, click one to
   instantly "equip" it as your desktop background.
2. Desktop Organizer  - define categories (Games, Editing, Documents...)
   with keyword lists. Running it scans your Desktop and moves matching
   files into subfolders named after the category.

Run it by double-clicking DesktopManager.pyw (needs Python installed,
get it from python.org if you don't have it - check "Add to PATH"
during install). No extra libraries needed, everything used here ships
with Python on Windows.

Your settings (saved wallpapers + categories/keywords) are stored in:
  %APPDATA%\\DesktopManager\\config.json
so they persist between runs.
"""

import os
import sys
import json
import shutil
import ctypes
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

# ---------------------------------------------------------------------------
# Paths / config
# ---------------------------------------------------------------------------

APPDATA = os.environ.get("APPDATA", os.path.expanduser("~"))
CONFIG_DIR = os.path.join(APPDATA, "DesktopManager")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

DEFAULT_CONFIG = {
    "wallpapers": {},  # name -> absolute file path
    "categories": {    # category name -> list of lowercase keywords
        "Games": ["game", "steam", "launcher", "epic", "riot", "valorant", "league"],
        "Editing": ["edit", "premiere", "photoshop", "psd", "resolve", "capcut", "clip"],
        "Documents": ["doc", "report", "resume", "invoice", "notes", "pdf"],
    },
    # files whose name matches nothing above stay where they are unless this is on
    "catch_all_enabled": False,
    "catch_all_name": "Other",
}

# Files we never touch when organizing
SKIP_NAMES = {"desktop.ini", "DesktopManager.pyw", "DesktopManager.py", "config.json"}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # backfill any missing keys (in case config is from an older version)
        for k, v in DEFAULT_CONFIG.items():
            data.setdefault(k, v)
        return data
    except (json.JSONDecodeError, OSError):
        return json.loads(json.dumps(DEFAULT_CONFIG))


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


# ---------------------------------------------------------------------------
# Wallpaper
# ---------------------------------------------------------------------------

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02


def set_wallpaper(path):
    """Sets the Windows desktop wallpaper to the given image path."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    # SystemParametersInfoW needs an absolute path
    abs_path = os.path.abspath(path)
    ok = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, abs_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    if not ok:
        raise OSError("Windows refused to set the wallpaper.")


# ---------------------------------------------------------------------------
# Organizer
# ---------------------------------------------------------------------------

def organize_desktop(cfg, desktop_path=DESKTOP_PATH):
    """
    Scans desktop_path, moves each file into a subfolder matching the
    first category whose keyword appears in the filename (case-insensitive).
    Folders already on the desktop are left alone (so it won't try to
    re-organize the category folders it already made, or your other folders).
    Returns a dict: category -> list of moved filenames, plus "skipped".
    """
    categories = cfg["categories"]
    results = {name: [] for name in categories}
    results["skipped"] = []

    if not os.path.isdir(desktop_path):
        raise FileNotFoundError(f"Desktop folder not found: {desktop_path}")

    entries = os.listdir(desktop_path)

    for name in entries:
        full_path = os.path.join(desktop_path, name)

        if name in SKIP_NAMES:
            continue
        if os.path.isdir(full_path):
            # don't move folders (avoids moving the category folders themselves,
            # or any other folder structure you've already got going)
            continue

        lower_name = name.lower()
        matched_category = None
        for cat_name, keywords in categories.items():
            for kw in keywords:
                if kw.lower() in lower_name:
                    matched_category = cat_name
                    break
            if matched_category:
                break

        if matched_category is None:
            if cfg.get("catch_all_enabled"):
                matched_category = cfg.get("catch_all_name", "Other")
            else:
                results["skipped"].append(name)
                continue

        dest_folder = os.path.join(desktop_path, matched_category)
        os.makedirs(dest_folder, exist_ok=True)
        dest_path = os.path.join(dest_folder, name)

        # avoid clobbering an existing file with the same name
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(name)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(dest_folder, f"{base} ({counter}){ext}")
                counter += 1

        shutil.move(full_path, dest_path)
        results.setdefault(matched_category, []).append(name)

    return results


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class DesktopManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Desktop Manager")
        self.geometry("560x520")
        self.minsize(480, 420)

        self.cfg = load_config()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.wallpaper_tab = ttk.Frame(notebook)
        self.organize_tab = ttk.Frame(notebook)
        notebook.add(self.wallpaper_tab, text="Wallpapers")
        notebook.add(self.organize_tab, text="Organize Desktop")

        self._build_wallpaper_tab()
        self._build_organize_tab()

    # -- Wallpaper tab ----------------------------------------------------

    def _build_wallpaper_tab(self):
        frame = self.wallpaper_tab

        ttk.Label(frame, text="Saved wallpapers - double-click to equip:",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 4))

        self.wallpaper_listbox = tk.Listbox(frame, height=12)
        self.wallpaper_listbox.pack(fill="both", expand=True, padx=10, pady=4)
        self.wallpaper_listbox.bind("<Double-Button-1>", lambda e: self.equip_selected_wallpaper())
        self._refresh_wallpaper_list()

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill="x", padx=10, pady=8)

        ttk.Button(btn_row, text="Add wallpaper...", command=self.add_wallpaper).pack(side="left")
        ttk.Button(btn_row, text="Equip selected", command=self.equip_selected_wallpaper).pack(side="left", padx=6)
        ttk.Button(btn_row, text="Remove selected", command=self.remove_wallpaper).pack(side="left")

        ttk.Separator(frame).pack(fill="x", padx=10, pady=8)
        ttk.Button(frame, text="Set a one-off wallpaper (not saved)...",
                   command=self.set_custom_wallpaper).pack(anchor="w", padx=10, pady=(0, 10))

    def _refresh_wallpaper_list(self):
        self.wallpaper_listbox.delete(0, "end")
        for name in self.cfg["wallpapers"]:
            self.wallpaper_listbox.insert("end", name)

    def add_wallpaper(self):
        path = filedialog.askopenfilename(
            title="Choose a wallpaper image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")],
        )
        if not path:
            return
        default_name = os.path.splitext(os.path.basename(path))[0]
        name = simpledialog.askstring("Name this wallpaper", "Give it a short name:",
                                       initialvalue=default_name)
        if not name:
            return
        self.cfg["wallpapers"][name] = path
        save_config(self.cfg)
        self._refresh_wallpaper_list()

    def equip_selected_wallpaper(self):
        sel = self.wallpaper_listbox.curselection()
        if not sel:
            messagebox.showinfo("Pick one", "Select a wallpaper from the list first.")
            return
        name = self.wallpaper_listbox.get(sel[0])
        path = self.cfg["wallpapers"].get(name)
        try:
            set_wallpaper(path)
            messagebox.showinfo("Done", f'"{name}" is now your wallpaper.')
        except Exception as e:
            messagebox.showerror("Couldn't set wallpaper", str(e))

    def remove_wallpaper(self):
        sel = self.wallpaper_listbox.curselection()
        if not sel:
            return
        name = self.wallpaper_listbox.get(sel[0])
        if messagebox.askyesno("Remove", f'Remove "{name}" from the saved list?'):
            self.cfg["wallpapers"].pop(name, None)
            save_config(self.cfg)
            self._refresh_wallpaper_list()

    def set_custom_wallpaper(self):
        path = filedialog.askopenfilename(
            title="Choose an image to use right now",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            set_wallpaper(path)
            messagebox.showinfo("Done", "Wallpaper updated.")
        except Exception as e:
            messagebox.showerror("Couldn't set wallpaper", str(e))

    # -- Organize tab -------------------------------------------------------

    def _build_organize_tab(self):
        frame = self.organize_tab

        top = ttk.Frame(frame)
        top.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: category list
        left = ttk.Frame(top)
        left.pack(side="left", fill="y")

        ttk.Label(left, text="Categories", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.category_listbox = tk.Listbox(left, height=14, width=20, exportselection=False)
        self.category_listbox.pack(fill="y", pady=4)
        self.category_listbox.bind("<<ListboxSelect>>", lambda e: self._refresh_keyword_list())

        cat_btn_row = ttk.Frame(left)
        cat_btn_row.pack(fill="x")
        ttk.Button(cat_btn_row, text="+ Category", command=self.add_category).pack(side="left")
        ttk.Button(cat_btn_row, text="- Remove", command=self.remove_category).pack(side="left", padx=4)

        # Right: keyword list for selected category
        right = ttk.Frame(top)
        right.pack(side="left", fill="both", expand=True, padx=(16, 0))

        ttk.Label(right, text="Keywords for selected category",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(right, text="(matched anywhere in the filename, case-insensitive)",
                  foreground="#666").pack(anchor="w", pady=(0, 4))

        self.keyword_listbox = tk.Listbox(right, height=12)
        self.keyword_listbox.pack(fill="both", expand=True)

        kw_row = ttk.Frame(right)
        kw_row.pack(fill="x", pady=6)
        self.keyword_entry = ttk.Entry(kw_row)
        self.keyword_entry.pack(side="left", fill="x", expand=True)
        self.keyword_entry.bind("<Return>", lambda e: self.add_keyword())
        ttk.Button(kw_row, text="Add", command=self.add_keyword).pack(side="left", padx=4)
        ttk.Button(kw_row, text="Remove selected", command=self.remove_keyword).pack(side="left")

        self._refresh_category_list()

        # Bottom: run + options
        bottom = ttk.Frame(frame)
        bottom.pack(fill="x", padx=10, pady=(0, 10))

        self.catch_all_var = tk.BooleanVar(value=self.cfg.get("catch_all_enabled", False))
        ttk.Checkbutton(
            bottom, text='Also sort leftover files into an "Other" folder',
            variable=self.catch_all_var, command=self._save_catch_all
        ).pack(anchor="w")

        ttk.Button(bottom, text="Organize Desktop Now", command=self.run_organize).pack(anchor="w", pady=(8, 0))

    def _save_catch_all(self):
        self.cfg["catch_all_enabled"] = self.catch_all_var.get()
        save_config(self.cfg)

    def _refresh_category_list(self):
        self.category_listbox.delete(0, "end")
        for name in self.cfg["categories"]:
            self.category_listbox.insert("end", name)
        self._refresh_keyword_list()

    def _selected_category(self):
        sel = self.category_listbox.curselection()
        if not sel:
            return None
        return self.category_listbox.get(sel[0])

    def _refresh_keyword_list(self):
        self.keyword_listbox.delete(0, "end")
        cat = self._selected_category()
        if not cat:
            return
        for kw in self.cfg["categories"].get(cat, []):
            self.keyword_listbox.insert("end", kw)

    def add_category(self):
        name = simpledialog.askstring("New category", "Category name (this becomes a folder name):")
        if not name:
            return
        if name in self.cfg["categories"]:
            messagebox.showinfo("Already exists", f'"{name}" already exists.')
            return
        self.cfg["categories"][name] = []
        save_config(self.cfg)
        self._refresh_category_list()

    def remove_category(self):
        cat = self._selected_category()
        if not cat:
            return
        if messagebox.askyesno("Remove category", f'Remove category "{cat}" and its keywords?\n'
                                                    f"(This won't touch files already moved into that folder.)"):
            self.cfg["categories"].pop(cat, None)
            save_config(self.cfg)
            self._refresh_category_list()

    def add_keyword(self):
        cat = self._selected_category()
        if not cat:
            messagebox.showinfo("Pick a category", "Select a category on the left first.")
            return
        kw = self.keyword_entry.get().strip()
        if not kw:
            return
        self.cfg["categories"][cat].append(kw)
        save_config(self.cfg)
        self.keyword_entry.delete(0, "end")
        self._refresh_keyword_list()

    def remove_keyword(self):
        cat = self._selected_category()
        if not cat:
            return
        sel = self.keyword_listbox.curselection()
        if not sel:
            return
        kw = self.keyword_listbox.get(sel[0])
        self.cfg["categories"][cat].remove(kw)
        save_config(self.cfg)
        self._refresh_keyword_list()

    def run_organize(self):
        if not messagebox.askyesno(
            "Organize Desktop",
            "This will move matching files on your Desktop into category folders.\n\n"
            "Folders already on your Desktop are left untouched.\nContinue?"
        ):
            return
        try:
            results = organize_desktop(self.cfg)
        except Exception as e:
            messagebox.showerror("Something went wrong", str(e))
            return

        lines = []
        for cat, files in results.items():
            if cat == "skipped":
                continue
            if files:
                lines.append(f"{cat}: {len(files)} file(s)")
        skipped = len(results.get("skipped", []))
        if skipped:
            lines.append(f"Left alone (no match): {skipped} file(s)")
        if not lines:
            lines.append("Nothing to move.")

        messagebox.showinfo("Organize complete", "\n".join(lines))


if __name__ == "__main__":
    if sys.platform != "win32":
        print("This tool uses Windows-only APIs for setting the wallpaper.")
    app = DesktopManagerApp()
    app.mainloop()
