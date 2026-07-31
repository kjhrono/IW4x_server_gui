#!/usr/bin/env python3
import json
import os
import re
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class IW4xServerManager:

    def __init__(self, root):
        self.root = root

        # Ensure working directory matches script location when double-clicked in File Explorer
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        self.root.title("IW4x Linux/Windows Server Configurator")
        self.root.geometry("640x480")
        self.root.minsize(820, 780)

        # Main Layout: Top Notebook for settings, Bottom Frame for persistent controls
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=(10, 5))

        # Initialize Tabs
        self.tab_general = ttk.Frame(self.notebook)
        self.tab_gameplay = ttk.Frame(self.notebook)
        self.tab_gametypes = ttk.Frame(self.notebook)
        self.tab_maps = ttk.Frame(self.notebook)
        self.tab_bots = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_general, text="General & Admin")
        self.notebook.add(self.tab_gameplay, text="Gameplay & XP Rules")
        self.notebook.add(self.tab_gametypes, text="Gametypes Settings")
        self.notebook.add(self.tab_maps, text="Map Rotation (DLCs)")
        self.notebook.add(self.tab_bots, text="BotWarfare Config")

        # Setup Tabs
        self.setup_general_tab()
        self.setup_gameplay_tab()
        self.setup_gametypes_tab()
        self.setup_maps_tab()
        self.setup_bots_tab()

        # Always-Visible Bottom Action Frame
        self.setup_bottom_panel()

        # Load manager_settings.json if present; otherwise, check the directory for server.cfg
        if os.path.exists("manager_settings.json"):
            self.load_app_state()
        else:
            self.check_and_load_existing_cfg()

    # --- TAB 1: GENERAL & ADMIN ---
    def setup_general_tab(self):
        f = self.tab_general

        ttk.Label(f, text="IW4x Server Directory:").grid(
            row=0, column=0, sticky="w", padx=10, pady=6
        )
        # Default to the directory where this script resides
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.path_var = tk.StringVar(value=script_dir)

        ttk.Entry(f, textvariable=self.path_var, width=42).grid(
            row=0, column=1, padx=5, pady=6
        )
        ttk.Button(f, text="Browse", command=self.browse_path).grid(
            row=0, column=2, padx=5, pady=6
        )

        ttk.Label(f, text="Server Name (sv_hostname):").grid(
            row=1, column=0, sticky="w", padx=10, pady=6
        )
        self.hostname_var = tk.StringVar(value="^2IW4x^7 Linux Server")
        ttk.Entry(f, textvariable=self.hostname_var, width=42).grid(
            row=1, column=1, columnspan=2, sticky="w", padx=5, pady=6
        )

        ttk.Label(f, text="Message of the Day (sv_motd):").grid(
            row=2, column=0, sticky="w", padx=10, pady=6
        )
        self.motd_var = tk.StringVar(value="Welcome to our IW4x Server!")
        ttk.Entry(f, textvariable=self.motd_var, width=42).grid(
            row=2, column=1, columnspan=2, sticky="w", padx=5, pady=6
        )

        ttk.Label(f, text="Network Mode:").grid(
            row=3, column=0, sticky="w", padx=10, pady=6
        )
        self.network_var = tk.StringVar(value="Internet (Dedicated 2)")
        net_combo = ttk.Combobox(
            f,
            textvariable=self.network_var,
            values=["Internet (Dedicated 2)", "LAN Only (Dedicated 1)"],
            state="readonly",
            width=30,
        )
        net_combo.grid(row=3, column=1, sticky="w", padx=5, pady=6)

        ttk.Label(f, text="Port (net_port):").grid(
            row=4, column=0, sticky="w", padx=10, pady=6
        )
        self.port_var = tk.StringVar(value="28960")
        ttk.Entry(f, textvariable=self.port_var, width=15).grid(
            row=4, column=1, sticky="w", padx=5, pady=6
        )

        ttk.Label(f, text="Max Players:").grid(
            row=5, column=0, sticky="w", padx=10, pady=6
        )
        self.maxplayers_var = tk.StringVar(value="18")
        ttk.Entry(f, textvariable=self.maxplayers_var, width=15).grid(
            row=5, column=1, sticky="w", padx=5, pady=6
        )

        ttk.Label(f, text="RCON Password:").grid(
            row=6, column=0, sticky="w", padx=10, pady=6
        )
        self.rcon_var = tk.StringVar(value="admin123")
        ttk.Entry(f, textvariable=self.rcon_var, show="*", width=25).grid(
            row=6, column=1, sticky="w", padx=5, pady=6
        )

        ttk.Label(f, text="AFK Idle Kick Timeout (s):").grid(
            row=7, column=0, sticky="w", padx=10, pady=6
        )
        self.inactivity_var = tk.StringVar(value="300")
        ttk.Entry(f, textvariable=self.inactivity_var, width=15).grid(
            row=7, column=1, sticky="w", padx=5, pady=6
        )

        ttk.Label(f, text="AFK Spectator Kick (s):").grid(
            row=8, column=0, sticky="w", padx=10, pady=6
        )
        self.spec_inactivity_var = tk.StringVar(value="500")
        ttk.Entry(f, textvariable=self.spec_inactivity_var, width=15).grid(
            row=8, column=1, sticky="w", padx=5, pady=6
        )

    def browse_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
            self.check_and_load_existing_cfg()
    
    def check_and_load_existing_cfg(self):
        game_dir = self.path_var.get()
        if not os.path.exists(game_dir):
            return

        # Check standard userraw directory first, fallback to root folder
        cfg_path = os.path.join(game_dir, "userraw", "server.cfg")
        if not os.path.exists(cfg_path):
            cfg_path = os.path.join(game_dir, "server.cfg")

        if os.path.exists(cfg_path):
            answer = messagebox.askyesno(
                "Existing Config Found",
                f"An existing 'server.cfg' was found at:\n{cfg_path}\n\nWould you like to load its settings into the editor?",
            )
            if answer:
                self.parse_server_cfg(cfg_path)

    def parse_server_cfg(self, cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            dvars = {}
            for line in lines:
                line = line.strip()
                if line.startswith("//") or not line:
                    continue
                if "//" in line:
                    line = line.split("//")[0].strip()

                # Parse: set <dvar_name> "<value>" or set <dvar_name> <value>
                match = re.match(
                    r"^set\s+([a-zA-Z0-9_]+)\s+[\"\']?(.*?)[\"\']?$", line
                )
                if match:
                    dvar = match.group(1).lower()
                    val = match.group(2).strip('"\'')
                    dvars[dvar] = val

            # Map basic dvars
            if "sv_hostname" in dvars:
                self.hostname_var.set(dvars["sv_hostname"])
            if "sv_motd" in dvars:
                self.motd_var.set(dvars["sv_motd"])
            if "rcon_password" in dvars:
                self.rcon_var.set(dvars["rcon_password"])
            if "sv_maxclients" in dvars:
                self.maxplayers_var.set(dvars["sv_maxclients"])
            if "g_inactivity" in dvars:
                self.inactivity_var.set(dvars["g_inactivity"])
            if "g_inactivityspectator" in dvars:
                self.spec_inactivity_var.set(dvars["g_inactivityspectator"])

            # Gameplay & XP dvars
            if "g_hardcore" in dvars:
                self.hc_var.set(dvars["g_hardcore"] == "1")
            if "scr_team_fftype" in dvars:
                val = dvars["scr_team_fftype"]
                for c in [
                    "0 - Disabled",
                    "1 - Enabled (On)",
                    "2 - Reflect Damage",
                    "3 - Shared Damage",
                ]:
                    if c.startswith(val):
                        self.ff_var.set(c)
            if "scr_game_spectatetype" in dvars:
                val = dvars["scr_game_spectatetype"]
                for c in [
                    "0 - Disabled",
                    "1 - Team/Player Only",
                    "2 - Free Camera",
                ]:
                    if c.startswith(val):
                        self.spectate_var.set(c)
            if "sv_allowaimassist" in dvars:
                self.aim_assist_var.set(dvars["sv_allowaimassist"] == "1")

            if "scr_xpscale" in dvars:
                self.xpscale_var.set(dvars["scr_xpscale"])
            if "scr_war_score_kill" in dvars:
                self.xp_kill_var.set(dvars["scr_war_score_kill"])
            if "scr_war_score_headshot" in dvars:
                self.xp_headshot_var.set(dvars["scr_war_score_headshot"])
            if "scr_war_score_assist" in dvars:
                self.xp_assist_var.set(dvars["scr_war_score_assist"])
            if "scr_war_score_death" in dvars:
                self.xp_death_var.set(dvars["scr_war_score_death"])
            if "scr_war_score_suicide" in dvars:
                self.xp_suicide_var.set(dvars["scr_war_score_suicide"])
            if "scr_game_allowkillcam" in dvars:
                self.killcam_var.set(dvars["scr_game_allowkillcam"] == "1")
            if "scr_teambalance" in dvars:
                self.teambalance_var.set(dvars["scr_teambalance"] == "1")

            # Gametype rules
            for gt, _ in self.all_gametypes:
                for rule_key, dvar_name in [
                    ("scorelimit", f"scr_{gt}_scorelimit"),
                    ("timelimit", f"scr_{gt}_timelimit"),
                    ("respawn", f"scr_{gt}_playerrespawndelay"),
                    ("lives", f"scr_{gt}_numlives"),
                    ("roundlimit", f"scr_{gt}_roundlimit"),
                    ("winlimit", f"scr_{gt}_winlimit"),
                ]:
                    if dvar_name in dvars:
                        self.gt_rules_data[gt][rule_key] = dvars[dvar_name]
            self.load_gt_rules()

            # BotWarfare dvars
            if "bots_main" in dvars:
                self.bot_enable_var.set(dvars["bots_main"] == "1")
            if "bots_main_waitforhosttime" in dvars:
                self.bot_wait_var.set(dvars["bots_main_waitforhosttime"])
            if "bots_main_menu" in dvars:
                self.bot_menu_var.set(dvars["bots_main_menu"] == "1")
            if "bots_main_kickbotsatend" in dvars:
                self.bot_kick_end_var.set(dvars["bots_main_kickbotsatend"] == "1")
            if "bots_main_chat" in dvars:
                self.bot_chat_var.set(dvars["bots_main_chat"])
            if "bots_manage_fill" in dvars:
                self.bot_fill_var.set(dvars["bots_manage_fill"])
            if "bots_manage_fill_watchplayers" in dvars:
                self.bot_watch_var.set(dvars["bots_manage_fill_watchplayers"] == "1")
            if "bots_manage_fill_kick" in dvars:
                self.bot_fill_kick_var.set(dvars["bots_manage_fill_kick"] == "1")
            if "bots_skill_min" in dvars:
                self.bot_skill_min_var.set(dvars["bots_skill_min"])
            if "bots_skill_max" in dvars:
                self.bot_skill_max_var.set(dvars["bots_skill_max"])
            if "bots_loadout_allow_op" in dvars:
                self.bot_allow_op_var.set(dvars["bots_loadout_allow_op"] == "1")
            if "bots_loadout_rank" in dvars:
                self.bot_rank_var.set(dvars["bots_loadout_rank"])
            if "bots_loadout_prestige" in dvars:
                self.bot_prestige_var.set(dvars["bots_loadout_prestige"])

            # Parse sv_mapRotation tokens to restore selected maps and active gametypes
            if "sv_maprotation" in dvars:
                tokens = dvars["sv_maprotation"].split()
                parsed_maps = set()
                parsed_gts = set()
                for i in range(len(tokens) - 1):
                    if tokens[i].lower() == "map":
                        parsed_maps.add(tokens[i + 1].lower())
                    elif tokens[i].lower() == "gametype":
                        parsed_gts.add(tokens[i + 1].lower())

                if parsed_gts:
                    for code, var in self.gt_vars.items():
                        var.set(code.lower() in parsed_gts)

                if parsed_maps:
                    for category, (lb, maps) in self.map_listboxes.items():
                        lb.selection_clear(0, tk.END)
                        for idx, (code, name) in enumerate(maps):
                            if code.lower() in parsed_maps:
                                lb.select_set(idx)

            self.log(f"[LOAD] Imported existing config settings from: {cfg_path}")
            messagebox.showinfo("Success", f"Loaded settings from:\n{cfg_path}")
        except Exception as e:
            self.log(f"[ERROR] Failed parsing cfg: {e}")
            messagebox.showerror("Error", f"Could not parse file:\n{e}")

    # --- TAB 2: GAMEPLAY & XP RULES ---
    def setup_gameplay_tab(self):
        f = self.tab_gameplay

        rules_frame = ttk.LabelFrame(f, text="General Gameplay Rules")
        rules_frame.pack(fill="x", padx=10, pady=5)

        self.hc_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            rules_frame,
            text="Enable Hardcore Mode (g_hardcore)",
            variable=self.hc_var,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=4)

        ttk.Label(rules_frame, text="Friendly Fire (scr_team_fftype):").grid(
            row=1, column=0, sticky="w", padx=10, pady=4
        )
        self.ff_var = tk.StringVar(value="0 - Disabled")
        ff_combo = ttk.Combobox(
            rules_frame,
            textvariable=self.ff_var,
            values=[
                "0 - Disabled",
                "1 - Enabled (On)",
                "2 - Reflect Damage",
                "3 - Shared Damage",
            ],
            state="readonly",
            width=22,
        )
        ff_combo.grid(row=1, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(rules_frame, text="Spectator Mode:").grid(
            row=2, column=0, sticky="w", padx=10, pady=4
        )
        self.spectate_var = tk.StringVar(value="2 - Free Camera")
        spec_combo = ttk.Combobox(
            rules_frame,
            textvariable=self.spectate_var,
            values=[
                "0 - Disabled",
                "1 - Team/Player Only",
                "2 - Free Camera",
            ],
            state="readonly",
            width=22,
        )
        spec_combo.grid(row=2, column=1, sticky="w", padx=5, pady=4)

        self.killcam_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            rules_frame, text="Allow Killcam", variable=self.killcam_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=4)

        self.teambalance_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            rules_frame,
            text="Auto Team Balance (scr_teambalance)",
            variable=self.teambalance_var,
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=4)

        self.aim_assist_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            rules_frame,
            text="Enable Controller Aim-Assist (sv_allowAimAssist)",
            variable=self.aim_assist_var,
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=4)

        # XP & Score Multipliers Section
        xp_frame = ttk.LabelFrame(f, text="XP Scale & Category Multipliers")
        xp_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(xp_frame, text="Global XP Scale (scr_xpscale):").grid(
            row=0, column=0, sticky="w", padx=10, pady=4
        )
        self.xpscale_var = tk.StringVar(value="1")
        ttk.Entry(xp_frame, textvariable=self.xpscale_var, width=10).grid(
            row=0, column=1, sticky="w", padx=5, pady=4
        )

        ttk.Label(xp_frame, text="XP per Kill (scr_war_score_kill):").grid(
            row=1, column=0, sticky="w", padx=10, pady=4
        )
        self.xp_kill_var = tk.StringVar(value="0")
        ttk.Entry(xp_frame, textvariable=self.xp_kill_var, width=10).grid(
            row=1, column=1, sticky="w", padx=5, pady=4
        )

        ttk.Label(
            xp_frame, text="XP per Headshot (scr_war_score_headshot):"
        ).grid(row=2, column=0, sticky="w", padx=10, pady=4)
        self.xp_headshot_var = tk.StringVar(value="0")
        ttk.Entry(xp_frame, textvariable=self.xp_headshot_var, width=10).grid(
            row=2, column=1, sticky="w", padx=5, pady=4
        )

        ttk.Label(
            xp_frame, text="XP per Assist (scr_war_score_assist):"
        ).grid(row=3, column=0, sticky="w", padx=10, pady=4)
        self.xp_assist_var = tk.StringVar(value="0")
        ttk.Entry(xp_frame, textvariable=self.xp_assist_var, width=10).grid(
            row=3, column=1, sticky="w", padx=5, pady=4
        )

        ttk.Label(xp_frame, text="XP per Death (scr_war_score_death):").grid(
            row=4, column=0, sticky="w", padx=10, pady=4
        )
        self.xp_death_var = tk.StringVar(value="0")
        ttk.Entry(xp_frame, textvariable=self.xp_death_var, width=10).grid(
            row=4, column=1, sticky="w", padx=5, pady=4
        )

        ttk.Label(
            xp_frame, text="XP per Suicide (scr_war_score_suicide):"
        ).grid(row=5, column=0, sticky="w", padx=10, pady=4)
        self.xp_suicide_var = tk.StringVar(value="0")
        ttk.Entry(xp_frame, textvariable=self.xp_suicide_var, width=10).grid(
            row=5, column=1, sticky="w", padx=5, pady=4
        )

    # --- TAB 3: GAMETYPES SETTINGS ---
    def setup_gametypes_tab(self):
        f = self.tab_gametypes

        # Grouping Definition
        self.respawn_modes = [
            ("war", "Team Deathmatch"),
            ("dm", "Free For All"),
            ("dom", "Domination"),
            ("koth", "Headquarters"),
            ("ctf", "Capture The Flag"),
            ("gun", "Gun Game"),
            ("gtnw", "Global Thermo-Nuclear War"),
        ]

        self.round_modes = [
            ("sd", "Search & Destroy"),
            ("dd", "Demolition"),
            ("sab", "Sabotage"),
            ("arena", "Arena"),
            ("oneflag", "One-Flag CTF"),
        ]

        self.all_gametypes = self.respawn_modes + self.round_modes

        info_frame = ttk.LabelFrame(
            f, text="Gametype Selection & Group Categorization"
        )
        info_frame.pack(fill="x", padx=10, pady=5)

        note_msg = (
            "Gametypes are visually separated by mode behavior. "
            "When mixing round-based and continuous modes in map rotation, ensure "
            "round limits and win limits are properly defined to prevent premature match endings."
        )
        ttk.Label(
            info_frame, text=note_msg, wraplength=720, justify="left"
        ).pack(padx=8, pady=4)

        # Container for checkboxes
        gt_container = ttk.Frame(info_frame)
        gt_container.pack(fill="x", padx=5, pady=5)

        self.gt_vars = {}

        # Respawn Modes Frame (Blue accent label)
        f_respawn = tk.LabelFrame(
            gt_container,
            text=" Continuous / Respawn Modes ",
            fg="#1f6aa5",
            font=("Helvetica", 9, "bold"),
        )
        f_respawn.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        for code, name in self.respawn_modes:
            var = tk.BooleanVar(value=(code == "war"))
            cb = ttk.Checkbutton(
                f_respawn, text=f"{name} ({code})", variable=var
            )
            cb.pack(anchor="w", padx=10, pady=2)
            self.gt_vars[code] = var

        # Round-Based Modes Frame (Red/Orange accent label)
        f_round = tk.LabelFrame(
            gt_container,
            text=" Round-Based / Objective Modes ",
            fg="#c0392b",
            font=("Helvetica", 9, "bold"),
        )
        f_round.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        for code, name in self.round_modes:
            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(f_round, text=f"{name} ({code})", variable=var)
            cb.pack(anchor="w", padx=10, pady=2)
            self.gt_vars[code] = var

        # Rule editing frame
        rules_frame = ttk.LabelFrame(f, text="Configure Gametype Specific Rules")
        rules_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Label(rules_frame, text="Select Mode to Edit:").grid(
            row=0, column=0, sticky="w", padx=8, pady=5
        )
        self.active_gt_edit = tk.StringVar(value="war")
        gt_picker = ttk.Combobox(
            rules_frame,
            textvariable=self.active_gt_edit,
            values=[c for c, n in self.all_gametypes],
            state="readonly",
            width=12,
        )
        gt_picker.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        gt_picker.bind("<<ComboboxSelected>>", self.load_gt_rules)

        self.gt_rules_data = {
            gt: {
                "scorelimit": "7500" if gt == "war" else "1500",
                "timelimit": "10",
                "respawn": "-1" if gt in ["war", "dm"] else "0",
                "lives": "0",
                "roundlimit": "1",
                "winlimit": "1",
            }
            for gt, n in self.all_gametypes
        }

        ttk.Label(rules_frame, text="Score Limit:").grid(
            row=1, column=0, sticky="w", padx=8, pady=3
        )
        self.rule_score = ttk.Entry(rules_frame, width=12)
        self.rule_score.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(rules_frame, text="Time Limit (mins):").grid(
            row=2, column=0, sticky="w", padx=8, pady=3
        )
        self.rule_time = ttk.Entry(rules_frame, width=12)
        self.rule_time.grid(row=2, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(rules_frame, text="Player Respawn Delay (s):").grid(
            row=3, column=0, sticky="w", padx=8, pady=3
        )
        self.rule_respawn = ttk.Entry(rules_frame, width=12)
        self.rule_respawn.grid(row=3, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(rules_frame, text="Number of Lives (0=unlimited):").grid(
            row=4, column=0, sticky="w", padx=8, pady=3
        )
        self.rule_lives = ttk.Entry(rules_frame, width=12)
        self.rule_lives.grid(row=4, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(rules_frame, text="Round Limit:").grid(
            row=5, column=0, sticky="w", padx=8, pady=3
        )
        self.rule_roundlimit = ttk.Entry(rules_frame, width=12)
        self.rule_roundlimit.grid(row=5, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(rules_frame, text="Win Limit:").grid(
            row=6, column=0, sticky="w", padx=8, pady=3
        )
        self.rule_winlimit = ttk.Entry(rules_frame, width=12)
        self.rule_winlimit.grid(row=6, column=1, sticky="w", padx=5, pady=3)

        ttk.Button(
            rules_frame, text="Apply Rule Changes", command=self.save_gt_rules
        ).grid(row=7, column=0, columnspan=2, pady=6)

        self.load_gt_rules()

    def load_gt_rules(self, event=None):
        gt = self.active_gt_edit.get()
        data = self.gt_rules_data[gt]
        self.rule_score.delete(0, tk.END)
        self.rule_score.insert(0, data["scorelimit"])
        self.rule_time.delete(0, tk.END)
        self.rule_time.insert(0, data["timelimit"])
        self.rule_respawn.delete(0, tk.END)
        self.rule_respawn.insert(0, data["respawn"])
        self.rule_lives.delete(0, tk.END)
        self.rule_lives.insert(0, data["lives"])
        self.rule_roundlimit.delete(0, tk.END)
        self.rule_roundlimit.insert(0, data["roundlimit"])
        self.rule_winlimit.delete(0, tk.END)
        self.rule_winlimit.insert(0, data["winlimit"])

    def save_gt_rules(self):
        gt = self.active_gt_edit.get()
        self.gt_rules_data[gt] = {
            "scorelimit": self.rule_score.get(),
            "timelimit": self.rule_time.get(),
            "respawn": self.rule_respawn.get(),
            "lives": self.rule_lives.get(),
            "roundlimit": self.rule_roundlimit.get(),
            "winlimit": self.rule_winlimit.get(),
        }
        self.log(f"[CONFIG] Applied rules for gametype '{gt}'")

    # --- TAB 4: MAP ROTATION (DLC CATEGORIZED & PERSISTENT) ---
    def setup_maps_tab(self):
        f = self.tab_maps

        self.map_notebook = ttk.Notebook(f)
        self.map_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        self.dlc_maps = {
            "Base MW2": [
                ("mp_afghan", "Afghan"),
                ("mp_derail", "Derail"),
                ("mp_estate", "Estate"),
                ("mp_favela", "Favela"),
                ("mp_highrise", "Highrise"),
                ("mp_invasion", "Invasion"),
                ("mp_checkpoint", "Karachi"),
                ("mp_quarry", "Quarry"),
                ("mp_rundown", "Rundown"),
                ("mp_rust", "Rust"),
                ("mp_boneyard", "Scrapyard"),
                ("mp_nightshift", "Skidrow"),
                ("mp_subbase", "Sub Base"),
                ("mp_terminal", "Terminal"),
                ("mp_underpass", "Underpass"),
                ("mp_brecourt", "Wasteland"),
            ],
            "DLC 1-3": [
                ("mp_complex", "Bailout"),
                ("mp_crash", "Crash"),
                ("mp_overgrown", "Overgrown"),
                ("mp_compact", "Salvage"),
                ("mp_storm", "Storm"),
                ("mp_abandon", "Carnival"),
                ("mp_fuel2", "Fuel"),
                ("mp_strike", "Strike"),
                ("mp_trailerpark", "Trailer Park"),
                ("mp_vacant", "Vacant"),
                ("mp_nuked", "Nuketown"),
            ],
            "DLC 4-9 (Classics)": [
                ("mp_cross_fire", "Crossfire"),
                ("mp_bloc", "Bloc"),
                ("mp_cargoship", "Cargoship"),
                ("mp_killhouse", "Killhouse"),
                ("mp_bog_sh", "Bog"),
                ("mp_cargoship_sh", "Freighter"),
                ("mp_shipment", "Shipment"),
                ("mp_shipment_long", "Long: Shipment"),
                ("mp_rust_long", "Long: Rust"),
                ("mp_firingrange", "Firing Range"),
                ("mp_storm_spring", "Chemical Plant"),
                ("mp_fav_tropical", "Tropical Favela"),
                ("mp_estate_tropical", "Tropical Estate"),
                ("mp_crash_tropical", "Tropical Crash"),
                ("mp_bloc_sh", "Forgotten City"),
                ("mp_backlot", "Backlot"),
                ("mp_broadcast", "Broadcast"),
                ("mp_carentan", "Chinatown"),
                ("mp_citystreets", "District"),
                ("mp_convoy", "Ambush"),
                ("mp_countdown", "Countdown"),
                ("mp_crash_snow", "Winter Crash"),
                ("mp_farm", "Downpour"),
                ("mp_pipeline", "Pipeline"),
                ("mp_showdown", "Showdown"),
            ],
            "DLC 10 (MW3) & SP": [
                ("mp_dome", "Dome"),
                ("mp_hardhat", "Hardhat"),
                ("mp_paris", "Resistance"),
                ("mp_seatown", "Seatown"),
                ("mp_bravo", "Mission"),
                ("mp_underground", "Underground"),
                ("mp_plaza2", "Arkaden"),
                ("mp_village", "Village"),
                ("mp_alpha", "Lockdown"),
                ("oilrig", "Oilrig"),
                ("co_hunted", "Village (Co-op)"),
            ],
        }

        self.map_listboxes = {}

        for category_name, maps in self.dlc_maps.items():
            sub_frame = ttk.Frame(self.map_notebook)
            self.map_notebook.add(sub_frame, text=category_name)

            # CRITICAL FIX: exportselection=False prevents selection clearing when switching tabs
            lb = tk.Listbox(
                sub_frame,
                selectmode=tk.MULTIPLE,
                height=12,
                exportselection=False,
            )
            lb.pack(fill="both", expand=True, padx=5, pady=5)

            for code, name in maps:
                lb.insert(tk.END, f"{name} ({code})")

            # Default select base maps
            if category_name == "Base MW2":
                for idx in range(len(maps)):
                    lb.select_set(idx)

            self.map_listboxes[category_name] = (lb, maps)

    def get_selected_maps(self):
        selected = []
        for category, (lb, maps) in self.map_listboxes.items():
            indices = lb.curselection()
            for idx in indices:
                selected.append(maps[idx][0])
        return selected

    # --- TAB 5: BOTWARFARE CONFIG (EXTENDED) ---
    def setup_bots_tab(self):
        f = self.tab_bots

        # Core Settings Frame
        f_main = ttk.LabelFrame(f, text="General Bot Settings")
        f_main.pack(fill="x", padx=10, pady=4)

        self.bot_enable_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            f_main,
            text="Enable BotWarfare Mod (bots_main)",
            variable=self.bot_enable_var,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=3)

        self.bot_menu_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            f_main,
            text="Enable In-Game Host Menu (bots_main_menu)",
            variable=self.bot_menu_var,
        ).grid(row=0, column=2, columnspan=2, sticky="w", padx=8, pady=3)

        self.bot_kick_end_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            f_main,
            text="Kick Bots at Game End (bots_main_kickBotsAtEnd)",
            variable=self.bot_kick_end_var,
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=8, pady=3)

        ttk.Label(f_main, text="Wait for Host Delay (s):").grid(
            row=1, column=2, sticky="w", padx=8, pady=3
        )
        self.bot_wait_var = tk.StringVar(value="10")
        ttk.Entry(f_main, textvariable=self.bot_wait_var, width=8).grid(
            row=1, column=3, sticky="w", padx=5, pady=3
        )

        ttk.Label(f_main, text="Bot Chat Rate (0 to disable):").grid(
            row=2, column=0, sticky="w", padx=8, pady=3
        )
        self.bot_chat_var = tk.StringVar(value="1.0")
        ttk.Entry(f_main, textvariable=self.bot_chat_var, width=8).grid(
            row=2, column=1, sticky="w", padx=5, pady=3
        )

        # Management & Population Frame
        f_manage = ttk.LabelFrame(f, text="Bot Population Management")
        f_manage.pack(fill="x", padx=10, pady=4)

        ttk.Label(f_manage, text="Bot Count / Target (bots_manage_fill):").grid(
            row=0, column=0, sticky="w", padx=8, pady=3
        )
        self.bot_fill_var = tk.StringVar(value="4")
        ttk.Entry(f_manage, textvariable=self.bot_fill_var, width=8).grid(
            row=0, column=1, sticky="w", padx=5, pady=3
        )

        ttk.Label(f_manage, text="Fill Mode (bots_manage_fill_mode):").grid(
            row=1, column=0, sticky="w", padx=8, pady=3
        )
        self.bot_fill_mode_var = tk.StringVar(
            value="1 - Only counts bots (maintain bot count)"
        )
        fill_mode_combo = ttk.Combobox(
            f_manage,
            textvariable=self.bot_fill_mode_var,
            values=[
                "0 - Counts both players and bots",
                "1 - Only counts bots (maintain bot count)",
                "2 - Exactly 0 but auto adjusts to map",
                "3 - Exactly 1 but auto adjusts to map",
                "4 - Use bots to balance teams",
                "5 - Auto balance teams adjusted to map",
            ],
            state="readonly",
            width=38,
        )
        fill_mode_combo.grid(
            row=1, column=1, columnspan=2, sticky="w", padx=5, pady=3
        )

        self.bot_watch_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            f_manage,
            text="Wait for 1st player before adding (bots_manage_fill_watchplayers)",
            variable=self.bot_watch_var,
        ).grid(row=2, column=0, columnspan=3, sticky="w", padx=8, pady=3)

        self.bot_fill_kick_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            f_manage,
            text="Kick bots when players join over fill limit (bots_manage_fill_kick)",
            variable=self.bot_fill_kick_var,
        ).grid(row=3, column=0, columnspan=3, sticky="w", padx=8, pady=3)

        # Skill & Loadouts Frame
        f_skill = ttk.LabelFrame(f, text="Skill Level & Class Loadouts")
        f_skill.pack(fill="x", padx=10, pady=4)

        ttk.Label(f_skill, text="Overall Skill Mode (bots_skill):").grid(
            row=0, column=0, sticky="w", padx=8, pady=3
        )
        self.bot_skill_var = tk.StringVar(value="0 - Random per Bot")
        skill_combo = ttk.Combobox(
            f_skill,
            textvariable=self.bot_skill_var,
            values=[
                "0 - Random per Bot",
                "1 - Easiest for all",
                "2 - Easy-Medium",
                "3 - Medium",
                "4 - Medium-Hard",
                "5 - Hard",
                "6 - Very Hard",
                "7 - Hardest for all",
                "8 - Custom per Team",
                "9 - Every parameter randomized",
            ],
            state="readonly",
            width=28,
        )
        skill_combo.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(f_skill, text="Min Skill (bots_skill_min):").grid(
            row=1, column=0, sticky="w", padx=8, pady=3
        )
        self.bot_skill_min_var = tk.StringVar(value="1")
        ttk.Entry(f_skill, textvariable=self.bot_skill_min_var, width=8).grid(
            row=1, column=1, sticky="w", padx=5, pady=3
        )

        ttk.Label(f_skill, text="Max Skill (bots_skill_max):").grid(
            row=2, column=0, sticky="w", padx=8, pady=3
        )
        self.bot_skill_max_var = tk.StringVar(value="7")
        ttk.Entry(f_skill, textvariable=self.bot_skill_max_var, width=8).grid(
            row=2, column=1, sticky="w", padx=5, pady=3
        )

        self.bot_allow_op_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            f_skill,
            text="Allow Overpowered Loadouts (bots_loadout_allow_op)",
            variable=self.bot_allow_op_var,
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=8, pady=3)

        ttk.Label(
            f_skill, text="Bot Rank (-1=Average, 0=Random, 1+=Exact):"
        ).grid(row=4, column=0, sticky="w", padx=8, pady=3)
        self.bot_rank_var = tk.StringVar(value="-1")
        ttk.Entry(f_skill, textvariable=self.bot_rank_var, width=8).grid(
            row=4, column=1, sticky="w", padx=5, pady=3
        )

        ttk.Label(
            f_skill, text="Bot Prestige (-1=Host, -2=Random, 0+=Exact):"
        ).grid(row=5, column=0, sticky="w", padx=8, pady=3)
        self.bot_prestige_var = tk.StringVar(value="-1")
        ttk.Entry(f_skill, textvariable=self.bot_prestige_var, width=8).grid(
            row=5, column=1, sticky="w", padx=5, pady=3
        )

    # --- BOTTOM PERSISTENT PANEL ---
    def setup_bottom_panel(self):
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="x", side="bottom", padx=10, pady=5)

        self.log_text = tk.Text(bottom_frame, height=4, width=80)
        self.log_text.pack(fill="x", padx=5, pady=2)

        btn_container = ttk.Frame(bottom_frame)
        btn_container.pack(fill="x", pady=4)

        ttk.Button(
            btn_container,
            text="Save server.cfg",
            command=self.save_config,
            width=18,
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_container,
            text="Run (Linux)",
            command=self.launch_server_linux,
            width=18,
        ).pack(side="right", padx=5)

        ttk.Button(
            btn_container,
            text="Run (Windows)",
            command=self.launch_server_windows,
            width=18,
        ).pack(side="right", padx=5)

        self.log(
            "Ready. Select 'Run (Linux)' or 'Run (Windows)' depending on your OS."
        )

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    # --- CONFIG GENERATION LOGIC ---
    def generate_cfg(self):
        cfg = f"""// IW4x Configuration File
        // Generated by IW4x Linux Server Configurator
        
        set sv_hostname "{self.hostname_var.get()}"
        set sv_motd "{self.motd_var.get()}"
        set rcon_password "{self.rcon_var.get()}"
        set g_password ""
        set sv_maxclients "{self.maxplayers_var.get()}"
        set party_maxplayers "{self.maxplayers_var.get()}"
        
        set g_inactivity "{self.inactivity_var.get()}"
        set g_inactivitySpectator "{self.spec_inactivity_var.get()}"
        
        set g_hardcore "{"1" if self.hc_var.get() else "0"}"
        set scr_hardcore "{"1" if self.hc_var.get() else "0"}"
        set scr_team_fftype "{self.ff_var.get().split(" ")[0]}"
        set scr_game_spectatetype "{self.spectate_var.get().split(" ")[0]}"
        set sv_allowAimAssist "{"1" if self.aim_assist_var.get() else "0"}"
        
        // XP & SCORE CONFIGURATION
        set scr_xpscale "{self.xpscale_var.get()}"
        set scr_war_score_kill "{self.xp_kill_var.get()}"
        set scr_war_score_headshot "{self.xp_headshot_var.get()}"
        set scr_war_score_assist "{self.xp_assist_var.get()}"
        set scr_war_score_death "{self.xp_death_var.get()}"
        set scr_war_score_suicide "{self.xp_suicide_var.get()}"
        
        set scr_game_allowkillcam "{"1" if self.killcam_var.get() else "0"}"
        set scr_teambalance "{"1" if self.teambalance_var.get() else "0"}"
        
        // GAMETYPE SETTINGS
        """
        # Gametype rule outputs
        for gt_code, _ in self.all_gametypes:
            rules = self.gt_rules_data[gt_code]
            cfg += f"set scr_{gt_code}_scorelimit \"{rules['scorelimit']}\"\n"
            cfg += f"set scr_{gt_code}_timelimit \"{rules['timelimit']}\"\n"
            cfg += f"set scr_{gt_code}_playerrespawndelay \"{rules['respawn']}\"\n"
            cfg += f"set scr_{gt_code}_numlives \"{rules['lives']}\"\n"
            cfg += f"set scr_{gt_code}_roundlimit \"{rules['roundlimit']}\"\n"
            cfg += f"set scr_{gt_code}_winlimit \"{rules['winlimit']}\"\n\n"

        # Extended BotWarfare configuration
        cfg += "// BOTWARFARE CONFIGURATION\n"
        cfg += f"set bots_main \"{"1" if self.bot_enable_var.get() else "0"}\"\n"
        cfg += f"set bots_main_waitForHostTime \"{self.bot_wait_var.get()}\"\n"
        cfg += f"set bots_main_menu \"{"1" if self.bot_menu_var.get() else "0"}\"\n"
        cfg += f"set bots_main_kickBotsAtEnd \"{"1" if self.bot_kick_end_var.get() else "0"}\"\n"
        cfg += f"set bots_main_chat \"{self.bot_chat_var.get()}\"\n"

        cfg += f"set bots_manage_fill \"{self.bot_fill_var.get()}\"\n"
        cfg += f"set bots_manage_fill_mode \"{self.bot_fill_mode_var.get().split(" ")[0]}\"\n"
        cfg += f"set bots_manage_fill_watchplayers \"{"1" if self.bot_watch_var.get() else "0"}\"\n"
        cfg += f"set bots_manage_fill_kick \"{"1" if self.bot_fill_kick_var.get() else "0"}\"\n"

        cfg += f"set bots_skill \"{self.bot_skill_var.get().split(" ")[0]}\"\n"
        cfg += f"set bots_skill_min \"{self.bot_skill_min_var.get()}\"\n"
        cfg += f"set bots_skill_max \"{self.bot_skill_max_var.get()}\"\n"

        cfg += f"set bots_loadout_allow_op \"{"1" if self.bot_allow_op_var.get() else "0"}\"\n"
        cfg += f"set bots_loadout_rank \"{self.bot_rank_var.get()}\"\n"
        cfg += f"set bots_loadout_prestige \"{self.bot_prestige_var.get()}\"\n\n"

        # Gametype and map rotation assembly
        active_gts = [
            code for code, var in self.gt_vars.items() if var.get()
        ]
        if not active_gts:
            active_gts = ["war"]

        selected_maps = self.get_selected_maps()
        if not selected_maps:
            selected_maps = ["mp_afghan"]

        cfg += f'set g_gametype "{active_gts[0]}"\n'

        rotation_elements = []
        for gt in active_gts:
            rotation_elements.append(f"gametype {gt}")
            for m in selected_maps:
                rotation_elements.append(f"map {m}")

        rotation_str = " ".join(rotation_elements)
        cfg += f'set sv_mapRotation "{rotation_str}"\n'

        return cfg

    def save_config(self, show_popup=True):
        game_dir = self.path_var.get()
        if not os.path.exists(game_dir):
            messagebox.showerror("Error", "Invalid IW4x server directory path!")
            return False

        userraw_dir = os.path.join(game_dir, "userraw")
        os.makedirs(userraw_dir, exist_ok=True)
        cfg_path = os.path.join(userraw_dir, "server.cfg")

        try:
            with open(cfg_path, "w") as f:
                f.write(self.generate_cfg())

            # Save state to JSON for auto-loading
            self.save_app_state()

            self.log(f"[OK] Configuration written to: {cfg_path}")
            if show_popup:
                messagebox.showinfo("Saved", f"server.cfg generated:\n{cfg_path}")
            return True
        except Exception as e:
            self.log(f"[ERROR] Save failed: {e}")
            messagebox.showerror("Error", f"Failed writing file:\n{e}")
            return False

    def launch_server_linux(self):
        game_dir = self.path_var.get()
        exe_path = os.path.join(game_dir, "iw4x.exe")

        if not os.path.isfile(exe_path):
            messagebox.showwarning(
                "Warning",
                f"iw4x.exe was not found in:\n{game_dir}\nAttempting launch anyway...",
            )

        if not self.save_config(show_popup=False):
            return

        lan_flag = "1" if "LAN" in self.network_var.get() else "0"
        ded_flag = "1" if "LAN" in self.network_var.get() else "2"
        port = self.port_var.get()

        wine_cmd = (
            f"wine iw4x.exe -dedicated -g_log games_mp.log "
            f"+set dedicated {ded_flag} +set net_port {port} +set sv_lanOnly {lan_flag} "
            f"+exec server.cfg +map_rotate"
        )

        terminals = [
            ["x-terminal-emulator", "-e", wine_cmd],
            [
                "gnome-terminal",
                "--",
                "bash",
                "-c",
                f"{wine_cmd}; read -p 'Server stopped. Press Enter to close...'",
            ],
            ["xterm", "-e", wine_cmd],
        ]

        launched = False
        for term_cmd in terminals:
            try:
                subprocess.Popen(term_cmd, cwd=game_dir)
                self.log(
                    f"[LAUNCH-LINUX] Server opened in terminal using '{term_cmd[0]}'."
                )
                launched = True
                break
            except FileNotFoundError:
                continue

        if not launched:
            cmd = [
                "wine",
                "iw4x.exe",
                "-dedicated",
                "-g_log",
                "games_mp.log",
                "+set",
                "dedicated",
                ded_flag,
                "+set",
                "net_port",
                port,
                "+set",
                "sv_lanOnly",
                lan_flag,
                "+exec",
                "server.cfg",
                "+map_rotate",
            ]
            try:
                subprocess.Popen(cmd, cwd=game_dir)
                self.log(
                    "[LAUNCH-LINUX] Server launched as background Wine process."
                )
            except Exception as e:
                self.log(f"[ERROR] Failed to start process: {e}")
                messagebox.showerror("Error", f"Could not launch process:\n{e}")

    def launch_server_windows(self):
        # Resolve absolute path to ensure Explorer launcher finds it
        game_dir = os.path.abspath(self.path_var.get())
        exe_path = os.path.join(game_dir, "iw4x.exe")

        if not os.path.isfile(exe_path):
            messagebox.showwarning(
                "Warning",
                f"iw4x.exe was not found in:\n{game_dir}\nAttempting launch anyway...",
            )

        if not self.save_config(show_popup=False):
            return

        lan_flag = "1" if "LAN" in self.network_var.get() else "0"
        ded_flag = "1" if "LAN" in self.network_var.get() else "2"
        port = self.port_var.get()

        cmd = [
            exe_path,  # Use full absolute path to exe
            "-dedicated",
            "-g_log",
            "games_mp.log",
            "+set",
            "dedicated",
            ded_flag,
            "+set",
            "net_port",
            port,
            "+set",
            "sv_lanOnly",
            lan_flag,
            "+exec",
            "server.cfg",
            "+map_rotate",
        ]

        self.log(f"[LAUNCH-WINDOWS] Executing in {game_dir}:")
        self.log(" ".join(cmd))

        try:
            creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
            subprocess.Popen(cmd, cwd=game_dir, creationflags=creationflags)
            self.log(
                "[OK] Windows server started successfully in a new console window."
            )
        except Exception as e:
            self.log(f"[ERROR] Windows launch failed: {e}")
            messagebox.showerror(
                "Error", f"Could not launch Windows process:\n{e}"
            )

    def save_app_state(self):
        state = {
            "path": self.path_var.get(),
            "hostname": self.hostname_var.get(),
            "motd": self.motd_var.get(),
            "network": self.network_var.get(),
            "port": self.port_var.get(),
            "maxplayers": self.maxplayers_var.get(),
            "rcon": self.rcon_var.get(),
            "inactivity": self.inactivity_var.get(),
            "spec_inactivity": self.spec_inactivity_var.get(),
            "hardcore": self.hc_var.get(),
            "friendly_fire": self.ff_var.get(),
            "spectate": self.spectate_var.get(),
            "aim_assist": self.aim_assist_var.get(),
            "xpscale": self.xpscale_var.get(),
            "xp_kill": self.xp_kill_var.get(),
            "xp_headshot": self.xp_headshot_var.get(),
            "xp_assist": self.xp_assist_var.get(),
            "xp_death": self.xp_death_var.get(),
            "xp_suicide": self.xp_suicide_var.get(),
            "killcam": self.killcam_var.get(),
            "teambalance": self.teambalance_var.get(),
            "gametypes": {code: var.get() for code, var in self.gt_vars.items()},
            "gt_rules": self.gt_rules_data,
            "selected_maps": self.get_selected_maps(),
            "bot_enable": self.bot_enable_var.get(),
            "bot_wait": self.bot_wait_var.get(),
            "bot_menu": self.bot_menu_var.get(),
            "bot_kick_end": self.bot_kick_end_var.get(),
            "bot_chat": self.bot_chat_var.get(),
            "bot_fill": self.bot_fill_var.get(),
            "bot_fill_mode": self.bot_fill_mode_var.get(),
            "bot_watch": self.bot_watch_var.get(),
            "bot_fill_kick": self.bot_fill_kick_var.get(),
            "bot_skill": self.bot_skill_var.get(),
            "bot_skill_min": self.bot_skill_min_var.get(),
            "bot_skill_max": self.bot_skill_max_var.get(),
            "bot_allow_op": self.bot_allow_op_var.get(),
            "bot_rank": self.bot_rank_var.get(),
            "bot_prestige": self.bot_prestige_var.get(),
        }
        try:
            with open("manager_settings.json", "w") as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            self.log(f"[WARN] Failed to save manager settings: {e}")

    def load_app_state(self):
        if not os.path.exists("manager_settings.json"):
            return

        try:
            with open("manager_settings.json", "r") as f:
                state = json.load(f)

            self.path_var.set(state.get("path", self.path_var.get()))
            self.hostname_var.set(state.get("hostname", self.hostname_var.get()))
            self.motd_var.set(state.get("motd", self.motd_var.get()))
            self.network_var.set(state.get("network", self.network_var.get()))
            self.port_var.set(state.get("port", self.port_var.get()))
            self.maxplayers_var.set(state.get("maxplayers", self.maxplayers_var.get()))
            self.rcon_var.set(state.get("rcon", self.rcon_var.get()))
            self.inactivity_var.set(state.get("inactivity", self.inactivity_var.get()))
            self.spec_inactivity_var.set(state.get("spec_inactivity", self.spec_inactivity_var.get()))
            self.hc_var.set(state.get("hardcore", self.hc_var.get()))
            self.ff_var.set(state.get("friendly_fire", self.ff_var.get()))
            self.spectate_var.set(state.get("spectate", self.spectate_var.get()))
            self.aim_assist_var.set(state.get("aim_assist", self.aim_assist_var.get()))
            self.xpscale_var.set(state.get("xpscale", self.xpscale_var.get()))
            self.xp_kill_var.set(state.get("xp_kill", self.xp_kill_var.get()))
            self.xp_headshot_var.set(state.get("xp_headshot", self.xp_headshot_var.get()))
            self.xp_assist_var.set(state.get("xp_assist", self.xp_assist_var.get()))
            self.xp_death_var.set(state.get("xp_death", self.xp_death_var.get()))
            self.xp_suicide_var.set(state.get("xp_suicide", self.xp_suicide_var.get()))
            self.killcam_var.set(state.get("killcam", self.killcam_var.get()))
            self.teambalance_var.set(state.get("teambalance", self.teambalance_var.get()))

            # Restore Gametypes
            gt_saved = state.get("gametypes", {})
            for code, var in self.gt_vars.items():
                if code in gt_saved:
                    var.set(gt_saved[code])

            if "gt_rules" in state:
                self.gt_rules_data.update(state["gt_rules"])
                self.load_gt_rules()

            # Restore Map Selections
            saved_maps = set(state.get("selected_maps", []))
            if saved_maps:
                for category, (lb, maps) in self.map_listboxes.items():
                    lb.selection_clear(0, tk.END)
                    for idx, (code, name) in enumerate(maps):
                        if code in saved_maps:
                            lb.select_set(idx)

            # Restore Bots
            self.bot_enable_var.set(state.get("bot_enable", self.bot_enable_var.get()))
            self.bot_wait_var.set(state.get("bot_wait", self.bot_wait_var.get()))
            self.bot_menu_var.set(state.get("bot_menu", self.bot_menu_var.get()))
            self.bot_kick_end_var.set(state.get("bot_kick_end", self.bot_kick_end_var.get()))
            self.bot_chat_var.set(state.get("bot_chat", self.bot_chat_var.get()))
            self.bot_fill_var.set(state.get("bot_fill", self.bot_fill_var.get()))
            self.bot_fill_mode_var.set(state.get("bot_fill_mode", self.bot_fill_mode_var.get()))
            self.bot_watch_var.set(state.get("bot_watch", self.bot_watch_var.get()))
            self.bot_fill_kick_var.set(state.get("bot_fill_kick", self.bot_fill_kick_var.get()))
            self.bot_skill_var.set(state.get("bot_skill", self.bot_skill_var.get()))
            self.bot_skill_min_var.set(state.get("bot_skill_min", self.bot_skill_min_var.get()))
            self.bot_skill_max_var.set(state.get("bot_skill_max", self.bot_skill_max_var.get()))
            self.bot_allow_op_var.set(state.get("bot_allow_op", self.bot_allow_op_var.get()))
            self.bot_rank_var.set(state.get("bot_rank", self.bot_rank_var.get()))
            self.bot_prestige_var.set(state.get("bot_prestige", self.bot_prestige_var.get()))

            self.log("[CONFIG] Auto-loaded saved configuration.")
        except Exception as e:
            self.log(f"[WARN] Failed to load saved state: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = IW4xServerManager(root)
    root.mainloop()
