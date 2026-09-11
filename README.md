# Desktop Manager

A tiny Windows desktop utility with two tools: swap your wallpaper in one click, and auto-organize the files cluttering your Desktop into folders by keyword.

No installer needed beyond Python — everything it uses ships with Python on Windows. Built with Tkinter.

## Features

- **Wallpaper Loadout** — save a few wallpapers with names, then double-click one to instantly set it as your Windows desktop background.
- **Desktop Organizer** — create categories (Games, Documents, etc.), give each one a list of keywords, then hit "Organize Desktop Now" to sort matching files on your Desktop into folders named after those categories.
  - Keywords match anywhere in a filename, case-insensitive — e.g. the keyword `psd` matches both `banner.psd` and `Old_PSD_backup.zip`.
  - Only scans loose files sitting directly on your Desktop — it never touches folders that are already there, including category folders it made itself.
  - Safe to run repeatedly: once a file's sorted, it's no longer on the Desktop, so there's nothing left to re-match.
  - Files that don't match any category are left alone, unless you enable the optional "Other" catch-all folder.

Some starter categories (Games, Editing, Documents) come pre-filled with example keywords — edit them or add your own.

## How to run

1. If you don't have Python yet, install it from [python.org](https://www.python.org/downloads/). During install, tick **"Add Python to PATH"**.
2. Double-click `DesktopManager.pyw`. It opens with no console window.
   (If double-clicking does nothing, right-click it → **Open with** → Python.)
3. Set up your wallpapers and/or categories, then use either tab as needed.

## Requirements

- Windows
- Python (no extra libraries required — everything used ships with Python by default)

## Your settings

Saved wallpapers and categories/keywords are stored in:
```
%APPDATA%\DesktopManager\config.json
```
Feel free to open, back up, or delete this file — deleting it resets everything to defaults.

## Customizing further

- **Keyboard shortcut:** right-click `DesktopManager.pyw` → Send to → Desktop (create shortcut), then right-click the new shortcut → Properties → Shortcut key.
- **Run at login:** drop a shortcut to it in:
  ```
  %AppData%\Microsoft\Windows\Start Menu\Programs\Startup
  ```

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
