#!/usr/bin/env python3
import json
import os
import re
import subprocess
import random
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

# Relative directory paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PREVIEWS_DIR = os.path.join(APP_DIR, "map_previews")
os.makedirs(PREVIEWS_DIR, exist_ok=True)

class IW4xServerManager:

    def __init__(self, root):
        self.root = root

        # Force working directory to script location
        os.chdir(APP_DIR)

        # Window config
        self.root.title("IW4x Linux/Windows Server Configurator")
        self.root.geometry("640x480")
        self.root.minsize(820, 780)

        # Initialize State Containers
        self.found_maps = set()
        self.current_selected_map = ("mp_afghan", "Afghan")
        self.current_img = None  # Holds active image reference

        # Default Community Map Tags
        self.default_tags = {
            "mp_afghan": "TDM, DOM, SD, CTF, SAB",
            "mp_derail": "TDM, DOM, SD",
            "mp_estate": "TDM, DOM, CTF, SAB",
            "mp_favela": "TDM, DM, DOM, SD, HQ",
            "mp_highrise": "TDM, DM, DOM, SD, CTF, SAB",
            "mp_invasion": "TDM, DOM, SD",
            "mp_checkpoint": "TDM, DM, DOM, SD, HQ",
            "mp_quarry": "TDM, DOM, SD, HQ",
            "mp_rundown": "TDM, DOM, SD",
            "mp_rust": "DM, TDM, GUN",
            "mp_boneyard": "TDM, DM, DOM, SD, CTF",
            "mp_nightshift": "TDM, DM, DOM, SD, HQ",
            "mp_subbase": "TDM, DOM, SD, CTF",
            "mp_terminal": "TDM, DM, DOM, SD, CTF",
            "mp_underpass": "TDM, DOM, SD",
            "mp_brecourt": "TDM, DOM, SD",
            "mp_nuked": "DM, TDM, DOM, GUN",
            "mp_crash": "TDM, DM, DOM, SD, HQ",
            "mp_vacant": "TDM, DM, DOM, SD, HQ",
            "mp_strike": "TDM, DOM, SD",
            "mp_cross_fire": "TDM, DOM, SD, CTF",
            "mp_shipment": "DM, TDM, GUN",
            "mp_dome": "DM, TDM, DOM, GUN",
        }

        # Complete Map Descriptions Dictionary (Base + DLC 1-10 + SP)
        self.map_descriptions = {
            # --- Base Game Maps ---
            "mp_afghan": "Large open area centered around a crashed plane. Great for snipers and long-range combat.",
            "mp_derail": "Large snowy train depot. Favors long-range engagements and tactical movement.",
            "mp_estate": "Woodland estate with a central cabin hill. High elevation combat and tight indoor lanes.",
            "mp_favela": "Multi-level Brazilian slum. Fast-paced close-quarters combat with high verticality.",
            "mp_highrise": "Skyscraper roof under construction. Iconic sniper sightlines and fast objective play.",
            "mp_invasion": "War-torn city streets. Balanced mix of indoor corridors and outdoor street lanes.",
            "mp_checkpoint": "Karachi city streets and alleyways. Dense urban layout with multiple flank routes.",
            "mp_quarry": "Industrial stone quarry. Multi-tiered structures and open ground combat.",
            "mp_rundown": "Overgrown village separated by a river. Medium to long range engagements.",
            "mp_rust": "Small desert oil rig. Extremely fast-paced, chaotic, instant-action map.",
            "mp_boneyard": "Scrapyard filled with airplane fuselages. Excellent objective map.",
            "mp_nightshift": "Skidrow urban apartment complex. Intense close-to-medium range corridor fights.",
            "mp_subbase": "Snowy submarine base. Tight interior hallways and open central courtyard.",
            "mp_terminal": "Airport terminal and tarmac. Iconic map with long sightlines and choke points.",
            "mp_underpass": "Overcast rain-soaked highway underpass. Dark corners and dense vegetation.",
            "mp_brecourt": "Wasteland open field surrounding a central bunker. Sniper paradise.",

            # --- DLC 1 - 3 (Stimulus, Resurgence, Nuketown) ---
            "mp_complex": "Bailout - Apartment complex with multi-level indoor corridors and a central courtyard.",
            "mp_crash": "Crash - Crashed helicopter in a desert town square. Highly balanced, classic layout.",
            "mp_overgrown": "Overgrown - Rural village featuring a dried riverbed, farmhouses, and long sniper lanes.",
            "mp_compact": "Salvage - Compact snow-covered junkyard filled with crushed cars and tight choke points.",
            "mp_storm": "Storm - Industrial park under heavy rain with warehouses and elevated catwalks.",
            "mp_abandon": "Carnival - Abandoned theme park featuring bumper cars, roller coasters, and vibrant funhouses.",
            "mp_fuel2": "Fuel - Sprawling oil refinery with huge open sightlines and a large interior warehouse.",
            "mp_strike": "Strike - Large desert city market. Dynamic sightlines for all weapon classes.",
            "mp_trailerpark": "Trailer Park - Extremely tight, maze-like trailer park favoring shotguns and SMGs.",
            "mp_vacant": "Vacant - Abandoned office complex. Tight interior rooms and short sightlines.",
            "mp_nuked": "Nuketown - Classic suburban nuclear test site. Extremely fast close-quarters map.",

            # --- DLC 4 - 9 (Classics & Recycled) ---
            "mp_cross_fire": "Crossfire - Iconic war-torn street with a high-intensity central killzone.",
            "mp_bloc": "Bloc - Large Russian apartment complex surrounding a central overgrown statue courtyard.",
            "mp_cargoship": "Cargoship - Freighter map with stormy weather, containers, and multi-deck combat.",
            "mp_killhouse": "Killhouse - Tiny military shoot-house designed for frantic, ultra-fast combat.",
            "mp_bog_sh": "Bog - Open, muddy night swamp with a central bus choke point.",
            "mp_cargoship_sh": "Freighter - Nighttime cargo ship variant with tight container lanes.",
            "mp_shipment": "Shipment - Ultra-small container yard. The ultimate chaotic fast-paced map.",
            "mp_shipment_long": "Long Shipment - Expanded version of Shipment offering slightly longer sightlines.",
            "mp_rust_long": "Long Rust - Extended layout of Rust with added outer perimeter routes.",
            "mp_firingrange": "Firing Range - Military training facility with balanced lanes and wooden target structures.",
            "mp_storm_spring": "Chemical Plant - Springtime industrial variant of Storm with dense foliage.",
            "mp_fav_tropical": "Tropical Favela - Sun-drenched, overgrown jungle variant of Favela.",
            "mp_estate_tropical": "Tropical Estate - Dense jungle resort variant of Estate.",
            "mp_crash_tropical": "Tropical Crash - Overgrown tropical jungle variant of Crash.",
            "mp_bloc_sh": "Forgotten City - Overgrown daytime variant of Bloc.",
            "mp_backlot": "Backlot - Urban construction site with strong vertical power positions.",
            "mp_broadcast": "Broadcast - TV station interior with tight office corridors and a large central newsroom.",
            "mp_carentan": "Chinatown - Nighttime urban town with two-story buildings and intense street combat.",
            "mp_citystreets": "District - Middle Eastern market square with surrounding alleyways.",
            "mp_convoy": "Ambush - Desert highway with destroyed convoy vehicles and flanking alleyways.",
            "mp_countdown": "Countdown - Missile launch facility with open tarmac and blast doors.",
            "mp_crash_snow": "Winter Crash - Festive holiday snow variant of Crash with festive lights.",
            "mp_farm": "Downpour - Heavy rain farm map with siloed barns and tall grass.",
            "mp_pipeline": "Pipeline - Abandoned train depot with underground drainage tunnels.",
            "mp_showdown": "Showdown - Small courtyard fortress with upper balcony sightlines.",

            # --- DLC 10 (MW3) & SP Maps ---
            "mp_dome": "Dome - Radar facility with a fast-paced central arena.",
            "mp_hardhat": "Hardhat - Construction site featuring an infamous central pipe choke point.",
            "mp_paris": "Resistance - Urban Paris streets with courtyard combat and shop interiors.",
            "mp_seatown": "Seatown - Coastal village with narrow alleys and marketplace rooftops.",
            "mp_bravo": "Mission - African village layout split by an aggressive central ravine.",
            "mp_underground": "Underground - Subway station with underground tracks and street-level shops.",
            "mp_plaza2": "Arkaden - Shopping mall with two-story interior stores and glass walkways.",
            "mp_village": "Village - African valley village with a central riverbed and cliffside paths.",
            "mp_alpha": "Lockdown - European city center with tight streets and apartment vantage points.",
            "oilrig": "Oilrig - Single-player campaign map set on an ocean drilling platform with multi-tier walkways.",
            "co_hunted": "Village (Co-op) - Special Ops countryside farm area adapted for multiplayer combat.",
        }

        # Load map tags
        self.map_tags = self.load_map_tags()

        # Set randomizator for maps
        self.randomize_rotation_var = tk.BooleanVar(value=False)

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

        # SMART INITIALIZATION
        settings_path = os.path.join(APP_DIR, "manager_settings.json")
        if os.path.exists(settings_path):
            self.load_app_state()
        else:
            # First run: Scan directory first, then only select INSTALLED base maps
            self.scan_installed_maps(silent=True)
            self.check_and_load_existing_cfg()

            lb_base, maps_base = self.map_listboxes["Base MW2"]
            lb_base.selection_clear(0, tk.END)
            for idx, (code, name) in enumerate(maps_base):
                if code.lower() in self.found_maps:
                    lb_base.select_set(idx)

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

        self.auto_scan_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            f,
            text="Automatically scan for installed maps on folder/config load",
            variable=self.auto_scan_var,
        ).grid(row=9, column=0, columnspan=3, sticky="w", padx=10, pady=6)

    def browse_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
            self.check_and_load_existing_cfg()
            self.trigger_map_scan(reason="Folder Changed")
    
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

            # Parse map scans
            self.trigger_map_scan(reason="server.cfg Loaded")

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

    # --- TAB 4: MAP ROTATION (REDESIGNED LAYOUT) ---
    def setup_maps_tab(self):
        f = self.tab_maps

        # 1. LEGENDA (Top)
        legend_frame = tk.LabelFrame(
            f,
            text=" Map Rotation Legend ",
            font=("Helvetica", 9, "bold"),
            bd=1,
            relief="solid",
            bg="#f8f9fa",
            fg="#212529",
            padx=8,
            pady=4,
        )
        legend_frame.pack(fill="x", padx=5, pady=(5, 3))

        status_frame = tk.Frame(legend_frame, bg="#f8f9fa")
        status_frame.pack(fill="x", padx=2, pady=(0, 2))

        tk.Label(
            status_frame,
            text="Map Status:",
            font=("Helvetica", 8, "bold"),
            bg="#f8f9fa",
            fg="#212529",
        ).pack(side="left", padx=(0, 5))

        tk.Label(
            status_frame,
            text="■ Green: Installed / Found",
            fg="#2e7d32",
            bg="#f8f9fa",
            font=("Helvetica", 8, "bold"),
        ).pack(side="left", padx=8)

        tk.Label(
            status_frame,
            text="■ Red: Missing / Uninstalled",
            fg="#c62828",
            bg="#f8f9fa",
            font=("Helvetica", 8, "bold"),
        ).pack(side="left", padx=8)

        acronym_text = (
            "Gametypes: TDM (Team Deathmatch) | DM (Free For All) | DOM (Domination) | SD (Search & Destroy) | HQ (Headquarters)\n"
            "CTF (Capture The Flag) | SAB (Sabotage) | DD (Demolition) | GUN (Gun Game) | GTNW (Global Thermo-Nuclear War)"
        )
        tk.Label(
            legend_frame,
            text=acronym_text,
            font=("Helvetica", 8),
            bg="#f8f9fa",
            fg="#333333",
            justify="center",
        ).pack(fill="x", padx=2, pady=(1, 0))

        # 2. MAIN SPLIT CONTENT AREA
        main_split = ttk.Frame(f)
        main_split.pack(expand=True, fill="both", padx=5, pady=3)

        # LEFT SIDE (60%): DLC Map Notebook
        left_frame = ttk.Frame(main_split)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 3))

        self.map_notebook = ttk.Notebook(left_frame)
        self.map_notebook.pack(expand=True, fill="both")

        # RIGHT SIDE (40%): Map Details, Preview & Interactive Tags Panel
        right_frame = ttk.LabelFrame(main_split, text=" Selected Map Details ")
        right_frame.pack(
            side="right", fill="both", padx=(3, 0), ipadx=5, ipady=5
        )

        # Container frame with locked dimensions (prevents Tkinter 9-pixel collapse bug)
        preview_container = tk.Frame(
            right_frame,
            width=260,
            height=145,
            bg="#d0d0d0",
            relief="sunken",
            bd=1,
        )
        preview_container.pack_propagate(False)  # Prevents shrinking
        preview_container.pack(fill="none", padx=6, pady=(5, 2))

        # Map Preview Image Label
        self.map_img_label = tk.Label(
            preview_container,
            text="Select a map to preview",
            bg="#d0d0d0",
            fg="#444444",
        )
        self.map_img_label.pack(expand=True, fill="both")

        # Tip label explaining where to place map preview images
        tk.Label(
            right_frame,
            text="💡 Place map images in './map_previews/'\n(e.g., preview_mp_afghan.png or mp_afghan.webp)",
            font=("Helvetica", 7, "italic"),
            fg="#555555",
            justify="center",
        ).pack(fill="x", padx=6, pady=(0, 4))

        # Title & Code
        self.map_title_label = tk.Label(
            right_frame,
            text="Afghan (mp_afghan)",
            font=("Helvetica", 10, "bold"),
            anchor="w",
        )
        self.map_title_label.pack(fill="x", padx=6, pady=(4, 2))

        # Description
        self.map_desc_text = tk.Text(
            right_frame,
            height=3,
            wrap="word",
            font=("Helvetica", 8),
            bg="#f4f4f4",
            relief="solid",
            bd=1,
        )
        self.map_desc_text.pack(fill="x", padx=6, pady=2)

        # Interactive Tag Checkboxes
        tag_frame = ttk.LabelFrame(right_frame, text=" Recommended Gametypes ")
        tag_frame.pack(fill="both", expand=True, padx=6, pady=6)

        self.tag_options = ["TDM", "DM", "DOM", "SD", "HQ", "CTF", "SAB", "DD", "GUN", "GTNW"]
        self.tag_cb_vars = {}

        tag_grid = ttk.Frame(tag_frame)
        tag_grid.pack(fill="both", expand=True, padx=4, pady=4)

        col, row = 0, 0
        for tag in self.tag_options:
            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(
                tag_grid,
                text=tag,
                variable=var,
                command=self.on_tag_checkbox_toggled,
            )
            cb.grid(row=row, column=col, sticky="w", padx=6, pady=2)
            self.tag_cb_vars[tag] = var
            col += 1
            if col > 1:
                col = 0
                row += 1

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

            lb = tk.Listbox(
                sub_frame,
                selectmode=tk.MULTIPLE,
                height=12,
                exportselection=False,
            )
            lb.pack(fill="both", expand=True, padx=3, pady=3)

            # Bind mouse click release directly to calculate exact row clicked
            lb.bind("<ButtonRelease-1>", self.on_map_click)

            self.map_listboxes[category_name] = (lb, maps)

        self.refresh_map_listboxes()

        # 3. CONTROL BAR (Positioned below the map view)
        top_bar = ttk.Frame(f)
        top_bar.pack(fill="x", padx=5, pady=(2, 5))

        ttk.Button(
            top_bar,
            text="Save Preset",
            command=self.save_rotation_preset,
            width=14,
        ).pack(side="left", padx=4)

        ttk.Button(
            top_bar,
            text="Load Preset",
            command=self.load_rotation_preset,
            width=14,
        ).pack(side="left", padx=4)

        ttk.Button(
            top_bar,
            text="Scan Directory",
            command=self.scan_installed_maps,
            width=16,
        ).pack(side="left", padx=4)

        # Randomize Checkbox
        ttk.Checkbutton(
            top_bar,
            text="🎲 Shuffle / Randomize Rotation Order",
            variable=self.randomize_rotation_var,
        ).pack(side="left", padx=12)
            
    def load_map_tags(self):
        tags = dict(self.default_tags)
        tag_file = os.path.join(APP_DIR, "map_tags.json")
        if os.path.exists(tag_file):
            try:
                with open(tag_file, "r") as f:
                    user_tags = json.load(f)
                    tags.update(user_tags)
            except Exception:
                pass
        return tags

    def save_map_tags(self):
        tag_file = os.path.join(APP_DIR, "map_tags.json")
        try:
            with open(tag_file, "w") as f:
                json.dump(self.map_tags, f, indent=4)
        except Exception as e:
            self.log(f"[WARN] Failed to save custom map tags: {e}")

    def update_map_details_panel(self, code, name):
        self.current_selected_map = (code, name)
        self.map_title_label.config(text=f"{name} ({code})")

        # Description
        desc = self.map_descriptions.get(
            code,
            "Standard multiplayer map. Suitable for team objectives and classic elimination modes.",
        )
        self.map_desc_text.delete("1.0", tk.END)
        self.map_desc_text.insert(tk.END, desc)

        # Image Preview (.png, .jpg, .webp with/without preview_ prefix)
        img_found = False
        for prefix in ["preview_", ""]:
            for ext in [".png", ".jpg", ".jpeg", ".webp"]:
                filename = f"{prefix}{code}{ext}"
                img_path = os.path.join(PREVIEWS_DIR, filename)

                if os.path.exists(img_path):
                    try:
                        # PIL (Pillow) image scaling to fit 255x140
                        try:
                            from PIL import Image, ImageTk

                            pil_img = Image.open(img_path)
                            pil_img = pil_img.resize(
                                (255, 140), Image.Resampling.LANCZOS
                            )
                            self.current_img = ImageTk.PhotoImage(pil_img)
                            self.map_img_label.config(
                                image=self.current_img, text="", bg="#f8f9fa"
                            )
                            img_found = True
                            break
                        except ImportError:
                            # Standard Tkinter fallback (PNG only)
                            if ext == ".png":
                                self.current_img = tk.PhotoImage(file=img_path)
                                self.map_img_label.config(
                                    image=self.current_img, text="", bg="#f8f9fa"
                                )
                                img_found = True
                                break
                    except Exception:
                        pass
            if img_found:
                break

        if not img_found:
            self.map_img_label.config(
                image="",
                text=f"[No Preview Image]\nPlace 'preview_{code}.png' or\n'{code}.png' in './map_previews/'",
                bg="#e0e0e0",
                fg="#555555",
            )

        # Update Checkboxes based on current map tags
        active_tags = [
            t.strip() for t in self.map_tags.get(code, "").split(",") if t.strip()
        ]
        for tag, var in self.tag_cb_vars.items():
            var.set(tag in active_tags)

    def on_tag_checkbox_toggled(self):
        code, name = self.current_selected_map
        selected_tags = [
            tag for tag, var in self.tag_cb_vars.items() if var.get()
        ]
        tag_str = ", ".join(selected_tags) if selected_tags else "NONE"

        self.map_tags[code] = tag_str
        self.save_map_tags()
        self.refresh_map_listboxes()
        self.log(f"[TAGS] Updated tags for {code}: [{tag_str}]")

    def build_map_rotation_string(self):
        # Translate UI gametypes to MW2 internal engine codes
        gt_engine_map = {
            "tdm": "war",  # MW2 engine code for TDM is 'war'
            "hq": "koth",  # MW2 engine code for HQ is 'koth' (King of the Hill)
            "dm": "dm",
            "dom": "dom",
            "sd": "sd",
            "ctf": "ctf",
            "sab": "sab",
            "dd": "dd",
            "gun": "gun",
            "gtnw": "gtnw",
            "arena": "arena",
            "oneflag": "oneflag",
        }

        enabled_gt = [
            gt.lower() for gt, var in self.gt_vars.items() if var.get()
        ]
        if not enabled_gt:
            enabled_gt = ["tdm"]

        selected_maps = self.get_selected_maps()
        if not selected_maps:
            return 'set sv_mapRotation "gametype war map mp_afghan"'

        rotation_pairs = []

        # Pair each selected map with allowed enabled gametypes based on map tags
        for code in selected_maps:
            map_tag_str = self.map_tags.get(code, "").upper()
            allowed_tags = [
                t.strip() for t in map_tag_str.split(",") if t.strip()
            ]

            for gt in enabled_gt:
                engine_gt = gt_engine_map.get(gt, gt)

                # Check if gametype is allowed on this map
                if (
                    not allowed_tags
                    or "ALL" in allowed_tags
                    or gt.upper() in allowed_tags
                    or engine_gt.upper() in allowed_tags
                ):
                    rotation_pairs.append((engine_gt, code))

        # Fallback if tag filtering yielded no pairs
        if not rotation_pairs:
            for code in selected_maps:
                for gt in enabled_gt:
                    engine_gt = gt_engine_map.get(gt, gt)
                    rotation_pairs.append((engine_gt, code))

        # Shuffle rotation order if checkbox is enabled
        if self.randomize_rotation_var.get():
            random.shuffle(rotation_pairs)

        # Build execution string
        parts = []
        current_gt = None
        for engine_gt, map_code in rotation_pairs:
            if engine_gt != current_gt:
                parts.append(f"gametype {engine_gt}")
                current_gt = engine_gt
            parts.append(f"map {map_code}")

        return f'set sv_mapRotation "{" ".join(parts)}"'

    def on_map_click(self, event):
        lb = event.widget
        category_name = None
        for cat, (box, maps) in self.map_listboxes.items():
            if box == lb:
                category_name = cat
                break

        if not category_name:
            return

        maps = self.map_listboxes[category_name][1]

        # Get exact row index under mouse cursor
        idx = lb.nearest(event.y)
        bbox = lb.bbox(idx)

        # Ensure click occurred on an item row, not empty space
        if bbox and bbox[1] <= event.y <= (bbox[1] + bbox[3]):
            if 0 <= idx < len(maps):
                code, name = maps[idx]

                # Update details panel immediately for clicked map
                self.update_map_details_panel(code, name)

                # If map is uninstalled, prevent selection
                if code.lower() not in self.found_maps:
                    self.root.after(10, lambda: lb.selection_clear(idx))

    def format_map_label(self, code, name):
        tag_str = self.map_tags.get(code, "ALL")
        return f"{name} ({code})   ▸  [{tag_str}]"

    def refresh_map_listboxes(self):
        for category_name, (lb, maps) in self.map_listboxes.items():
            selected_indices = set(lb.curselection())
            lb.delete(0, tk.END)

            for idx, (code, name) in enumerate(maps):
                lb.insert(tk.END, self.format_map_label(code, name))

                # Color coding: Green for found, Red for missing
                if code.lower() in self.found_maps:
                    lb.itemconfig(idx, foreground="#2e7d32")  # Dark Green
                else:
                    lb.itemconfig(idx, foreground="#c62828")  # Dark Red

                if idx in selected_indices:
                    lb.select_set(idx)

    def edit_selected_map_tag(self):
        # Find active listbox tab
        current_tab_idx = self.map_notebook.index(self.map_notebook.select())
        category_name = list(self.dlc_maps.keys())[current_tab_idx]
        lb, maps = self.map_listboxes[category_name]

        selected = lb.curselection()
        if not selected:
            messagebox.showinfo(
                "Info", "Please select a map in the current listbox to edit its tags."
            )
            return

        idx = selected[0]
        code, name = maps[idx]
        current_tag = self.map_tags.get(code, "ALL")

        new_tag = simpledialog.askstring(
            "Edit Map Tags",
            f"Enter recommended gametype tags for map '{name}' ({code}):\n(e.g., TDM, DOM, SD, CTF)",
            initialvalue=current_tag,
        )

        if new_tag is not None:
            self.map_tags[code] = new_tag.strip().upper()
            self.save_map_tags()
            self.refresh_map_listboxes()
            self.log(f"[TAGS] Updated tags for {code}: [{self.map_tags[code]}]")

    def save_rotation_preset(self):
        filepath = filedialog.asksaveasfilename(
            initialdir=APP_DIR,
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Save Map Rotation Preset",
        )
        if not filepath:
            return

        selected_maps = self.get_selected_maps()
        data = {"selected_maps": selected_maps, "map_tags": self.map_tags}
        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo(
                "Success", f"Preset saved to:\n{os.path.basename(filepath)}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preset:\n{e}")

    def load_rotation_preset(self):
        filepath = filedialog.askopenfilename(
            initialdir=APP_DIR,
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Load Map Rotation Preset",
        )
        if not filepath:
            return

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            saved_maps = set(data.get("selected_maps", []))

            # Deselect all, then select loaded installed maps
            for category, (lb, maps) in self.map_listboxes.items():
                lb.selection_clear(0, tk.END)
                for idx, (code, name) in enumerate(maps):
                    if code in saved_maps and code.lower() in self.found_maps:
                        lb.select_set(idx)

            if "map_tags" in data:
                self.map_tags.update(data["map_tags"])
                self.save_map_tags()
                self.refresh_map_listboxes()

            messagebox.showinfo(
                "Success", f"Preset loaded from:\n{os.path.basename(filepath)}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load preset:\n{e}")

    def scan_installed_maps(self, silent=False):
        game_dir = self.path_var.get()
        if not os.path.exists(game_dir):
            if not silent:
                messagebox.showerror(
                    "Error", "Invalid IW4x server directory path!"
                )
            return

        self.found_maps.clear()
        for root, dirs, files in os.walk(game_dir):
            for f in files:
                if f.endswith(".ff"):
                    self.found_maps.add(f[:-3].lower())
            for d in dirs:
                self.found_maps.add(d.lower())

        self.refresh_map_listboxes()

        self.log(
            f"[SCAN] Discovered {len(self.found_maps)} map assets in: {game_dir}"
        )
        if not silent:
            messagebox.showinfo("Scan Complete", "Map directory scan finished!")

    def trigger_map_scan(self, reason="Folder/Config Change"):
        game_dir = self.path_var.get()
        if not os.path.exists(game_dir):
            return

        if self.auto_scan_var.get():
            self.scan_installed_maps(silent=True)
        else:
            answer = messagebox.askyesno(
                "Scan Directory for Maps?",
                f"The server directory was updated ({reason}).\n\nWould you like to scan for installed maps now?",
            )
            if answer:
                self.scan_installed_maps(silent=False)

    def get_selected_maps(self):
        selected = []
        for category, (lb, maps) in self.map_listboxes.items():
            indices = lb.curselection()
            for idx in indices:
                code = maps[idx][0]
                if code.lower() in self.found_maps:
                    selected.append(code)
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
        # Translation map for MW2 engine gametypes
        gt_engine_map = {
            "tdm": "war",
            "hq": "koth",
            "dm": "dm",
            "dom": "dom",
            "sd": "sd",
            "ctf": "ctf",
            "sab": "sab",
            "dd": "dd",
            "gun": "gun",
            "gtnw": "gtnw",
            "arena": "arena",
            "oneflag": "oneflag",
        }
        
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

        # Set default startup gametype (translated)
        active_gts = [
            gt.lower() for gt, var in self.gt_vars.items() if var.get()
        ]
        default_gt = active_gts[0] if active_gts else "tdm"
        engine_default_gt = gt_engine_map.get(default_gt, default_gt)

        # Disable party mode & set default gametype
        cfg += 'set party_enable "0"\n'
        cfg += f'set g_gametype "{engine_default_gt}"\n\n'

        # Append map rotation
        map_rotation_line = self.build_map_rotation_string()
        cfg += f"{map_rotation_line}\n"

    def save_config(self, show_popup=True):
        game_dir = self.path_var.get()
        if not os.path.exists(game_dir):
            messagebox.showerror(
                "Error", "Invalid IW4x server directory path!"
            )
            return False

        # Ensure <game_directory>/userraw/ exists
        userraw_dir = os.path.join(game_dir, "userraw")
        os.makedirs(userraw_dir, exist_ok=True)

        cfg_path = os.path.join(userraw_dir, "server.cfg")

        try:
            cfg_content = self.generate_cfg()
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write(cfg_content)

            self.save_app_state()  # Saves manager state to script's ./ folder
            self.log(f"[CONFIG] Wrote server.cfg successfully to {cfg_path}")

            if show_popup:
                messagebox.showinfo(
                    "Success", f"server.cfg saved successfully to:\n{cfg_path}"
                )
            return True
        except Exception as e:
            self.log(f"[ERROR] Failed to write server.cfg: {e}")
            messagebox.showerror("Error", f"Failed to save server.cfg:\n{e}")
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
        state_file = os.path.join(APP_DIR, "manager_settings.json")
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
            "xpscale": self.xpscale_var.get(),
            "xp_kill": self.xp_kill_var.get(),
            "xp_headshot": self.xp_headshot_var.get(),
            "xp_assist": self.xp_assist_var.get(),
            "xp_death": self.xp_death_var.get(),
            "xp_suicide": self.xp_suicide_var.get(),
            "killcam": self.killcam_var.get(),
            "teambalance": self.teambalance_var.get(),
            "aim_assist": self.aim_assist_var.get(),
            "auto_scan": self.auto_scan_var.get(),
            "gametypes": {code: var.get() for code, var in self.gt_vars.items()},
            "gt_rules": self.gt_rules_data,
            "selected_maps": self.get_selected_maps(),
            "randomize_rotation": self.randomize_rotation_var.get(),
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
            with open(state_file, "w") as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            self.log(f"[WARN] Failed to save manager settings: {e}")

    def load_app_state(self):
        state_file = os.path.join(APP_DIR, "manager_settings.json")
        if not os.path.exists(state_file):
            return

        try:
            with open(state_file, "r") as f:
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
            self.xpscale_var.set(state.get("xpscale", self.xpscale_var.get()))
            self.xp_kill_var.set(state.get("xp_kill", self.xp_kill_var.get()))
            self.xp_headshot_var.set(state.get("xp_headshot", self.xp_headshot_var.get()))
            self.xp_assist_var.set(state.get("xp_assist", self.xp_assist_var.get()))
            self.xp_death_var.set(state.get("xp_death", self.xp_death_var.get()))
            self.xp_suicide_var.set(state.get("xp_suicide", self.xp_suicide_var.get()))
            self.killcam_var.set(state.get("killcam", self.killcam_var.get()))
            self.teambalance_var.set(state.get("teambalance", self.teambalance_var.get()))
            self.aim_assist_var.set(state.get("aim_assist", self.aim_assist_var.get()))
            self.auto_scan_var.set(state.get("auto_scan", self.auto_scan_var.get()))

            # Restore Gametypes
            gt_saved = state.get("gametypes", {})
            for code, var in self.gt_vars.items():
                if code in gt_saved:
                    var.set(gt_saved[code])

            if "gt_rules" in state:
                self.gt_rules_data.update(state["gt_rules"])
                self.load_gt_rules()

            # Scan installed maps
            self.trigger_map_scan(reason="App Settings Loaded")

            # Restore Map Selections
            saved_maps = set(state.get("selected_maps", []))
            if saved_maps:
                for category, (lb, maps) in self.map_listboxes.items():
                    lb.selection_clear(0, tk.END)
                    for idx, (code, name) in enumerate(maps):
                        if code in saved_maps and code.lower() in self.found_maps:
                            lb.select_set(idx)

            # Restore Map randomization
            self.randomize_rotation_var.set(
                state.get("randomize_rotation", self.randomize_rotation_var.get())
            )

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
