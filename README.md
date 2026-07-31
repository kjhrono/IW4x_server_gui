# 🎮 IW4x Server Configurator & Launcher

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/)
[![Game](https://img.shields.io/badge/Game-IW4x%20MW2-FF4500?style=for-the-badge)](https://alterware.dev/)
[![AI Collaborator](https://img.shields.io/badge/Co--Developed%20With-Gemini-8E44AD?style=for-the-badge&logo=google&logoColor=white)](https://gemini.google.com/)

A lightweight, cross-platform graphical configuration manager and server launcher for hosting **IW4x (Call of Duty: Modern Warfare 2)** dedicated servers on **Windows** and **Linux (Ubuntu / Mint Cinnamon)**.

Built with Python and Tkinter, this tool eliminates manual `server.cfg` editing by providing a multi-tabbed interface to manage settings, map rotations, gametypes, XP scaling, and BotWarfare.

## ✨ Features

### ⚙️ General & Network Configuration
* **Smart Directory Auto-Scan**: Detects your IW4x installation folder and automatically imports existing `server.cfg` files on startup.
* **Server Properties**: Manage hostname (with full Call of Duty color code support), MOTD, network mode (`Dedicated 1` LAN vs `Dedicated 2` Public Internet), net port, max players, RCON password, and AFK spectator/inactivity timers.
* **Gameplay Toggles**: Quick controls for controller aim-assist (`sv_allowAimAssist`), auto team balancing, and killcams.

### 🎯 Gameplay Rules & XP Modifiers
* **Rules & Physics**: Support for Hardcore modes, spectator camera restrictions, and Friendly Fire policies (*Disabled, Enabled, Reflect, Shared*).
* **XP Scaling**: Adjust global XP multipliers (`scr_xpscale`) alongside individual points rewarded for kills, headshots, assists, deaths, and suicides.

### 🏆 Organized Gametype Management
* **Categorized Modes**: Gametypes split into **Continuous / Respawn Modes** (TDM, FFA, Domination, HQ, CTF, Gun Game, GTNW) and **Round-Based Objective Modes** (S&D, Demolition, Sabotage, Arena, One-Flag CTF).
* **Per-Gametype Overrides**: Fine-tune score limits, time limits, player respawn delays, lives, round limits, and win limits for every mode.

### 🗺️ Map Rotation & Visual Details Panel
* **DLC Categorization**: Comprehensive map selection tabs covering Base MW2, DLC 1–3 (Stimulus/Resurgence), DLC 4–9 (Classics & Recycled maps), and DLC 10 (MW3) + SP maps.
* **Color-Coded Asset Scanning**:
  * 🟢 **Green**: Installed map assets found in your local game files.
  * 🔴 **Red**: Missing / uninstalled maps (automatically disabled from selection).
* **Map Details Panel**:
  * Real-time map preview renderer supporting `.webp`, `.png`, `.jpg`, and `.jpeg` images.
  * Detailed tactical overviews and map descriptions.
  * Interactive gametype recommendation checkboxes that dynamically update map tags.
* **Presets & Tags**: Save and load custom map rotation presets (`.json`) and store custom tags in `map_tags.json`.
* **Visual Legend**: Quick-reference guide for gametype acronyms and status indicators.

### 🤖 BotWarfare Integration
* **Full DVAR Coverage**: Native support for INeedBots' IW4 BotWarfare mod.
* **Bot Controls**: Configure bot population count, fill modes, min/max skill levels, host menu access, OP weapon filters, rank, and prestige progression.

### 🚀 Cross-Platform Launcher
* **Windows Execution**: Resolves absolute working paths and executes `iw4x.exe` directly in a new Command Prompt console window.
* **Linux Execution**: Automatically hooks into `wine iw4x.exe` using system terminal wrappers (`x-terminal-emulator`, `gnome-terminal`, or `xterm`).

## 📁 Directory Structure

```text
IW4x-Server-Manager/
├── iw4x_manager.py          # Main Python GUI application
├── manager_settings.json    # Application state (auto-generated)
├── map_tags.json            # Custom map tags database (auto-generated)
├── map_previews/            # Map preview image folder
│   ├── preview_mp_afghan.png
│   ├── mp_rust.webp
│   └── ...
└── <game_directory>/
    └── userraw/
        └── server.cfg       # Executable configuration file
```

## 📦 Prerequisites

### 🐧 Linux (Ubuntu / Linux Mint)
Ensure Python 3, Tkinter, Pillow (for image processing), and Wine are installed.

### 🪟 Windows
Download and install Python 3.x from python.org.  
During installation, make sure to check "Add python.exe to PATH".  
Install the Pillow package via Command Prompt: pip install Pillow   

## 🚀 How to Run

### 🐧 Linux (Ubuntu / Linux Mint)
Open your terminal in the script directory and run: python3 iw4x_manager.py

### 🪟 Windows
Using Command Prompt: py iw4x_manager.py  
Direct Double-Click: Rename iw4x_manager.py to iw4x_manager.pyw. Double-clicking a .pyw file in Windows Explorer launches the GUI directly without keeping a background black command window open.

### 🖼️ Adding Map Preview Images
Place your loading screen images inside the ./map_previews/ folder relative to the script.  
  
Supported Formats: .webp, .png, .jpg, .jpeg  
Supported Naming Formats: preview_mp_mapname.png (e.g., preview_mp_afghan.png), mp_mapname.webp (e.g., mp_rust.webp)  

## 🤝 Credits & Acknowledgments
IW4x Team / AlterWare: For developing and maintaining the IW4x client platform.  
INeedBots: For the IW4 BotWarfare mod implementation.  
Gemini (Google AI): Designed, architecture-planned, and co-developed in technical collaboration with Gemini.  
