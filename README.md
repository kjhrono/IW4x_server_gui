Here is a complete, well-structured README.md file tailored for your repository.

IW4x Server Configurator & Launcher
A lightweight, cross-platform graphical configuration tool and launcher for hosting IW4x (Call of Duty: Modern Warfare 2) dedicated servers on Linux (Ubuntu / Mint Cinnamon) and Windows.

Built with Python and Tkinter, this tool streamlines server.cfg generation, DLC map rotation management, XP scaling, and BotWarfare configuration into a clean tabbed GUI.

Features
🛠️ General & Admin Management
Directory Detection: Defaults to the script directory or lets you browse to your IW4x installation path.

Auto-Import: Automatically detects and offers to parse existing server.cfg files upon directory selection.

Server Settings: Configure server hostname (with color code support), MOTD, network mode (Dedicated 1 LAN vs. Dedicated 2 Public Internet), port, max players, RCON password, and AFK kick timeouts.

Aim-Assist & Balance: Toggles for controller aim-assist (sv_allowAimAssist), auto team balancing, and killcams.

🎮 Gameplay & XP Customization
Hardcore & FF Modes: Custom options for hardcore mode, spectator camera styles, and friendly fire behaviors (Disabled, On, Reflect, Shared).

XP Scaling: Easily set scr_xpscale and individual event XP values (Kills, Headshots, Assists, Deaths, Suicides).

🏆 Organized Gametype Settings
Visual Grouping: Separates continuous/respawn modes (TDM, FFA, Domination, HQ, CTF, Gun Game, GTNW) from round-based objective modes (S&D, Demolition, Sabotage, Arena, One-Flag CTF).

Per-Gametype Rules: Customize score limits, time limits, player respawn delays, lives, round limits, and win limits per mode.

🗺️ Map Rotation & Visual Details Panel
DLC Categorization: Maps grouped by Base MW2, DLCs 1–3, DLCs 4–9 (Classics & Recycled), and DLC 10 (MW3) + SP maps.

Color-Coded Scanning:

🟢 Green: Installed map assets found in game files.

🔴 Red: Missing / uninstalled maps (automatically disabled from selection).

Map Details Panel:

Displays loading screen preview images (.webp, .png, .jpg).

Shows map descriptions and tactical overviews.

Interactive gametype recommendation checkboxes that update map list tags in real-time.

Presets & Tags: Save and load custom map rotation presets (.json) and edit custom map tags (map_tags.json).

Built-in Legenda: Quick-reference guide for gametype acronyms and map status colors.

🤖 BotWarfare Integration
Full DVAR Coverage: Dedicated tab for INeedBots' BotWarfare mod.

Control Options: Bot population fill count, fill modes, skill levels (min/max), wait-for-host delays, chat frequency, in-game host menu toggles, OP loadout filters, rank, and prestige settings.

🚀 Cross-Platform Execution & Persistence
Linux Execution: Runs wine iw4x.exe inside a visible terminal emulator (x-terminal-emulator, gnome-terminal, or xterm).

Windows Execution: Runs native iw4x.exe in a standalone Command Prompt window.

Auto-State Persistence: Automatically saves and restores all GUI states to manager_settings.json upon saving.

Directory Structure
Plaintext
IW4x-Server-Manager/
├── iw4x_manager.py          # Main Python application
├── manager_settings.json    # Saved GUI state (auto-generated)
├── map_tags.json            # Custom map tags (auto-generated)
├── map_previews/            # Map preview images (preview_mp_afghan.png, mp_rust.webp, etc.)
└── userraw/
    └── server.cfg           # Generated server configuration file
Prerequisites
🐧 Linux (Ubuntu / Mint Cinnamon)
Ensure Python 3, Tkinter, Pillow (for WebP/image loading), and Wine are installed:

Bash
sudo apt update
sudo apt install python3 python3-tk python3-pil python3-pil.imagetk wine
🪟 Windows
Download and install Python 3.x from python.org.

During setup, make sure to check "Add python.exe to PATH".

Install Pillow for image support (run in Command Prompt):

DOS
pip install Pillow
How to Run
On Linux
Run the script directly from your terminal inside the IW4x directory:

Bash
python3 iw4x_manager.py
On Windows
Via Command Prompt:

DOS
py iw4x_manager.py
Via Double-Click: Rename iw4x_manager.py to iw4x_manager.pyw. Double-clicking .pyw files on Windows launches the application directly without leaving a black Command Prompt window open in the background.

Adding Map Preview Images
Place map loading screen images inside the ./map_previews/ folder relative to the script directory.

Supported formats: .webp, .png, .jpg, .jpeg

Supported naming conventions: preview_mp_mapname.png or mp_mapname.webp

Examples: preview_mp_afghan.png, mp_rust.webp, preview_mp_terminal.jpg

Credits & Acknowledgments
IW4x Team: For creating the IW4x client platform for Modern Warfare 2.

INeedBots: For the IW4 BotWarfare mod.

AI Assistance: Designed, structured, and developed in collaboration with Gemini (Google AI).
