# PC Health Check Toolkit

A simple Windows desktop tool with a GUI for checking on your PC's health —
clean up junk, tidy up startup programs, spot anything suspicious, and (if
you're on a hard drive) give your system a speed boost.

No installer, no dependencies — just two files. Everything is built from
PowerShell and Windows Forms.

## Features

- **Run Diagnostics** — a read-only snapshot of disk space, memory usage,
  top processes by memory, and recent system errors. Nothing is changed.
- **Scan Junk Files** — checks common clutter spots (temp folders, browser
  caches, Windows Update cache, Recycle Bin) and shows the size of each.
  You tick what you want gone; nothing is deleted until you confirm.
- **Optimize Startup** — lists your startup programs and lets you disable
  ones you don't need. This only stops auto-launch on next login — nothing
  is uninstalled, and every change can be undone.
- **Suspicious Report** — flags things worth a closer look: unsigned
  executables currently running, non-Microsoft scheduled tasks, unexpected
  hosts file entries, and installed Chrome extensions. This flags
  anomalies for your own review — it isn't a malware scan or a verdict.
- **Speed Boost (HDD)** — tweaks aimed at traditional hard drives: analyze/
  defragment the C: drive, check SysMain, Fast Startup, and visual effects
  settings. Every change asks for confirmation first, and the tool notes
  when a drive is an SSD (where defrag isn't needed).

Every action shows you what it found before doing anything. Cleanup and
disable steps only run on items you've explicitly checked and confirmed.

## Getting started

1. Download or clone this repo, keeping `PC-HealthCheck-GUI.ps1` and
   `Launch_PC_Health_Check.bat` in the same folder — the launcher needs the
   script alongside it.
2. Double-click `Launch_PC_Health_Check.bat`.
3. Approve the User Account Control (UAC) prompt when it appears — the tool
   needs administrator rights for startup items and drive optimization.
4. Pick an option from the GUI and follow the on-screen prompts.

## Requirements

- Windows 10 or 11
- PowerShell (included with Windows by default)
- Administrator rights for full functionality (some diagnostics still run
  without it, with reduced detail)

## Notes

- This is an **unsigned PowerShell script**. It's open source — every line
  is visible in `PC-HealthCheck-GUI.ps1` — so if you have any doubt about
  what it does, read the source before running it rather than taking my
  word for it.
- Windows SmartScreen or your antivirus may flag it simply for being
  unsigned and requesting elevation. That's a generic "unknown publisher"
  notice, not a virus detection.
- The `.bat` launcher uses `-ExecutionPolicy Bypass` for its own process
  only — it doesn't change your system's execution policy permanently or
  touch your antivirus settings.
- Back up anything important before using **Speed Boost** or **Optimize
  Startup** — they make real changes to your system, even though each one
  asks for confirmation first.
- This project was built through an AI-assisted coding conversation. I run
  and check it before it's posted here, but as with any tool that touches
  startup items, files, or drive settings, review it and use it at your
  own discretion.

Found a bug, or genuinely suspicious behavior? Open an issue with specifics
(line numbers help) — I'll take a look.

## License

MIT — see [LICENSE](LICENSE) for details.
