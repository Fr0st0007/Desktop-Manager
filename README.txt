Desktop Manager - quick start
==============================

WHAT IT DOES
- Wallpapers tab: save a few wallpapers with names, double-click one to
  instantly set it as your Windows desktop background.
- Organize Desktop tab: create categories (Games, Documents, etc.), give each
  one a list of keywords, then hit "Organize Desktop Now" to sort matching
  files on your Desktop into folders with those names.

HOW TO RUN IT
1. If you don't have Python yet, install it from https://www.python.org/downloads/
   During install, tick the box that says "Add Python to PATH".
2. Double-click DesktopManager.pyw. It opens with no console window.
   (If double-clicking does nothing, right-click it -> Open with -> Python.)

SETTING UP CATEGORIES
- Some starter categories (Games, Editing, Documents) are already there with
  example keywords. Edit these or add your own:
  - Click a category on the left to see/edit its keywords.
  - Type a keyword and hit Add or press Enter. Keywords match anywhere in a
    filename, case-insensitive - e.g. keyword "psd" matches "banner.psd" and
    "Old_PSD_backup.zip".
- "+ Category" makes a new category, which becomes a folder name on your
  Desktop once files are sorted into it.

RUNNING THE ORGANIZER
- Click "Organize Desktop Now". It scans files (not folders) sitting
  directly on your Desktop and moves each one into the first category
  folder whose keyword matches. Files that match nothing are left alone,
  unless you tick "Also sort leftover files into an Other folder".
- It never touches folders already on your Desktop, so it won't try to
  re-sort a category folder it already made or any of your existing folders.
- It's safe to run repeatedly - already-sorted files simply won't be on the
  Desktop anymore, so there's nothing left to re-match.

YOUR SETTINGS
Saved wallpapers and categories/keywords live in:
  %APPDATA%\DesktopManager\config.json
Feel free to open/back up this file, or delete it to reset to defaults.

CUSTOMIZING FURTHER
- Want a keyboard shortcut to launch it? Right-click DesktopManager.pyw ->
  Send to -> Desktop (create shortcut), then right-click the new shortcut ->
  Properties -> Shortcut key.
- Want it to run automatically at login? Put a shortcut to it in:
  %AppData%\Microsoft\Windows\Start Menu\Programs\Startup
