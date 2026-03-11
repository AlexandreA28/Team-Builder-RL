import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.font import Font
import json
import os
import sys
import random
import copy

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

try:
    from PIL import Image, ImageTk
except ImportError:
    messagebox.showerror("Erreur", "La bibliothèque Pillow n'est pas installée. Tapez 'pip install Pillow' dans le terminal.")

class TournamentManager:
    def __init__(self):
        self.players = []
        self.save_file = "joueurs.json"
        self.load_players()

    def get_rank_info(self, mmr):
        ranks = [
            (1860, 8, "SSL"), (1715, 7, "GC3"), (1575, 7, "GC2"), (1435, 7, "GC1"),
            (1315, 6, "C3"),  (1195, 6, "C2"),  (1075, 6, "C1"),
            (995,  5, "D3"),  (915,  5, "D2"),  (835,  5, "D1"),
            (775,  4, "P3"),  (715,  4, "P2"),  (655,  4, "P1"),
            (595,  3, "G3"),  (535,  3, "G2"),  (475,  3, "G1"),
            (415,  2, "S3"),  (355,  2, "S2"),  (295,  2, "S1"),
            (235,  1, "B3"),  (175,  1, "B2"),  (0,    1, "B1")
        ]
        
        for threshold, cat, rank_name in ranks:
            if mmr >= threshold:
                return f"Cat. {cat} : {rank_name}", rank_name
        return "Cat. 1 : B1", "B1"

    def load_players(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r", encoding="utf-8") as f:
                self.players = json.load(f)

    def save_players(self):
        with open(self.save_file, "w", encoding="utf-8") as f:
            json.dump(self.players, f, indent=4)

    def add_player(self, name, mmr):
        self.players.append({"name": name, "mmr": mmr})
        self.save_players()

    def remove_player(self, index):
        if 0 <= index < len(self.players):
            del self.players[index]
            self.save_players()

    def generate_teams(self, team_size, max_mmr_gap=250, iterations=1000):
        total_players = len(self.players)
        if total_players == 0:
            return "❌ Erreur : Aucun joueur enregistré."
        if total_players % team_size != 0:
            return f"❌ Erreur : Impossible de faire des équipes complètes de {team_size} joueurs."

        num_teams = total_players // team_size
        players_copy = copy.deepcopy(self.players)
        unique_draws = {}

        for _ in range(iterations):
            random.shuffle(players_copy)
            teams = [{"id": i+1, "players": [], "total_mmr": 0} for i in range(num_teams)]
            
            for i, player in enumerate(players_copy):
                team_index = i % num_teams
                teams[team_index]["players"].append(player)
                teams[team_index]["total_mmr"] += player["mmr"]
            
            mmrs = [t["total_mmr"] for t in teams]
            mmr_diff = max(mmrs) - min(mmrs)
            
            team_signatures = []
            for t in teams:
                names = tuple(sorted([p["name"] for p in t["players"]]))
                team_signatures.append(names)
            
            match_signature = tuple(sorted(team_signatures))
            if match_signature not in unique_draws:
                unique_draws[match_signature] = {
                    "diff": mmr_diff,
                    "teams": copy.deepcopy(teams)
                }

        all_draws = list(unique_draws.values())
        all_draws.sort(key=lambda x: x["diff"])

        acceptable_draws = [draw for draw in all_draws if draw["diff"] <= max_mmr_gap]
        final_draw = random.choice(acceptable_draws) if acceptable_draws else all_draws[0]

        return final_draw["teams"]

class TournamentApp:
    def __init__(self, root):
        self.manager = TournamentManager()
        self.root = root
        self.root.title("ROCKET LEAGUE – TEAM BUILDER")
        self.root.state('zoomed')
        
        self.bg_color = "#1A1F2C"
        self.panel_color = "#2E364F"
        self.text_color = "#E0E4EB"
        self.highlight_color = "#4996F3" 
        self.button_gradient = ["#4996F3", "#B162F0"]
        
        self.root.configure(bg=self.bg_color)

        self.title_font = Font(family="Segoe UI Semibold", size=18)
        self.bold_font = Font(family="Arial", size=12)
        self.normal_font = Font(family="Arial", size=12)
        self.result_font = Font(family="Consolas", size=11)
        self.list_font = Font(family="Arial", size=12)
        self.header_font = Font(family="Arial", size=11)

        icon_path = resource_path("icone_team_builder.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Treeview", background=self.panel_color, foreground=self.text_color, 
                        rowheight=45, fieldbackground=self.panel_color, font=self.list_font)
        style.map('Treeview', background=[('selected', self.highlight_color)])
        style.configure("Treeview.Heading", font=self.header_font, foreground=self.text_color, 
                        background="#1A1F2C", padding=(0, 10))

        self.rank_images = {}
        self.load_rank_images()

        header_frame = tk.Frame(root, bg=self.bg_color, pady=10)
        header_frame.pack(fill=tk.X, padx=20)

        tk.Label(header_frame, text="⚙️", font=("Arial", 30), bg=self.bg_color, fg=self.highlight_color).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(header_frame, text="ROCKET LEAGUE – TEAM BUILDER", font=self.title_font, bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)

        left_frame = tk.Frame(root, bg=self.bg_color, padx=30, pady=20, width=450)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)

        tk.Label(left_frame, text="JOUEURS", font=self.bold_font, bg=self.bg_color, fg=self.text_color).pack(anchor="w")
        self.players_count_label = tk.Label(left_frame, text="0 joueur(s)", font=self.normal_font, bg=self.bg_color, fg="#888888")
        self.players_count_label.pack(anchor="w", pady=(0, 20))

        tk.Label(left_frame, text="PSEUDO :", font=self.bold_font, bg=self.bg_color, fg=self.text_color).pack(anchor="w")
        self.name_entry = tk.Entry(left_frame, width=30, bg="#2A2F3D", fg="white", font=self.normal_font, insertbackground="white")
        self.name_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(left_frame, text="MMR :", font=self.bold_font, bg=self.bg_color, fg=self.text_color).pack(anchor="w")
        mmr_frame = tk.Frame(left_frame, bg=self.bg_color)
        mmr_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.mmr_entry = tk.Entry(mmr_frame, width=15, bg="#2A2F3D", fg="white", font=self.normal_font, insertbackground="white")
        self.mmr_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.add_btn = tk.Button(mmr_frame, text="AJOUTER", command=self.add_player, bg=self.button_gradient[0], fg="white", font=self.bold_font, bd=0, padx=15, pady=5)
        self.add_btn.pack(side=tk.RIGHT)

        tk.Label(left_frame, text="Liste des joueurs inscrits :", font=self.bold_font, bg=self.bg_color, fg=self.text_color).pack(anchor="w", pady=(10, 10))
        
        self.players_tree = ttk.Treeview(left_frame, columns=("JOUEUR", "MMR"), show="tree headings", height=12)
        self.players_tree.column("#0", width=80, anchor=tk.CENTER, stretch=tk.NO)
        self.players_tree.heading("#0", text="RANG", anchor=tk.CENTER)

        self.players_tree.column("JOUEUR", width=150, anchor=tk.CENTER)
        self.players_tree.heading("JOUEUR", text="JOUEUR", anchor=tk.CENTER)

        self.players_tree.column("MMR", width=80, anchor=tk.CENTER)
        self.players_tree.heading("MMR", text="MMR", anchor=tk.CENTER)
        self.players_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.players_tree.bind("<Double-1>", self.on_double_click)
        self.players_tree.bind("<Return>", self.on_enter_pressed)
        self.players_tree.bind("<Delete>", lambda e: self.remove_player())
        
        self.refresh_listbox()
        
        tk.Button(left_frame, text="🗑️Supprimer sélection", command=self.remove_player, bg="#f44336", fg="white", font=self.normal_font, bd=0, pady=5).pack(fill=tk.X)

        right_frame = tk.Frame(root, bg=self.bg_color, padx=30, pady=20)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(right_frame, bg=self.bg_color)
        control_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(control_frame, text="RÉGLAGES :", font=self.bold_font, bg=self.bg_color, fg=self.text_color).pack(anchor="w")
        
        settings_frame = tk.Frame(control_frame, bg=self.bg_color)
        settings_frame.pack(fill=tk.X, pady=(15, 10))

        tk.Label(settings_frame, text="Format d'équipe :", font=self.bold_font, bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=(0, 10))
        self.team_size_var = tk.IntVar(value=2)
        tk.Radiobutton(settings_frame, text="2 VS 2", variable=self.team_size_var, value=2, indicatoron=0, bg=self.panel_color, fg=self.text_color, selectcolor=self.highlight_color, font=self.normal_font, padx=10).pack(side=tk.LEFT)
        tk.Radiobutton(settings_frame, text="3 VS 3", variable=self.team_size_var, value=3, indicatoron=0, bg=self.panel_color, fg=self.text_color, selectcolor=self.highlight_color, font=self.normal_font, padx=10).pack(side=tk.LEFT, padx=5)

        tk.Label(settings_frame, text="Écart MMR Max :", font=self.bold_font, bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=(30, 10))
        self.max_gap_entry = tk.Entry(settings_frame, width=5, bg="#2A2F3D", fg="white", font=self.normal_font, insertbackground="white")
        self.max_gap_entry.insert(0, "200")
        self.max_gap_entry.pack(side=tk.LEFT)

        buttons_frame = tk.Frame(control_frame, bg=self.bg_color)
        buttons_frame.pack(pady=(15, 0))

        self.generate_btn = tk.Button(buttons_frame, text="GÉNÉRER LES ÉQUIPES", command=self.generate, bg=self.button_gradient[1], fg="white", font=self.bold_font, bd=0, padx=20, pady=10)
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        self.copy_discord_btn = tk.Button(buttons_frame, text="COPIE DISCORD", command=self.copy_to_discord, bg="#5865F2", fg="white", font=self.bold_font, bd=0, padx=20, pady=10)
        self.copy_discord_btn.pack(side=tk.LEFT, padx=5)

        self.result_text = tk.Text(right_frame, state=tk.DISABLED, font=self.result_font, bg=self.panel_color, fg=self.text_color, bd=0, padx=15, pady=15)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def copy_to_discord(self):
        content = self.result_text.get("1.0", tk.END).strip()
        
        if not content or "🏆" not in content:
            messagebox.showwarning("Info", "Il n'y a rien à copier !\nGénère d'abord des équipes.")
            return
            
        discord_format = f"```\n{content}\n```"
        
        self.root.clipboard_clear()
        self.root.clipboard_append(discord_format)

    def load_rank_images(self):
        ranks_list = ["B1", "B2", "B3", "S1", "S2", "S3", "G1", "G2", "G3", 
                      "P1", "P2", "P3", "D1", "D2", "D3", "C1", "C2", "C3", 
                      "GC1", "GC2", "GC3", "SSL"]
        
        folder_path = resource_path("ranks")
        if not os.path.exists(folder_path):
            return
            
        for rank in ranks_list:
            path_png = os.path.join(folder_path, f"{rank}.png")
            path_jpg = os.path.join(folder_path, f"{rank}.jpg")
            target_path = path_png if os.path.exists(path_png) else (path_jpg if os.path.exists(path_jpg) else None)
            
            if target_path:
                try:
                    img = Image.open(target_path)
                    img = img.resize((40, 40), Image.Resampling.LANCZOS)
                    self.rank_images[rank] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Erreur au chargement de {target_path} : {e}")

    def refresh_listbox(self):
        self.players_tree.delete(*self.players_tree.get_children())
        
        for i, p in enumerate(self.manager.players):
            _, short_rank = self.manager.get_rank_info(p['mmr'])
            img = self.rank_images.get(short_rank)
            
            self.players_tree.insert("", tk.END, image=img, text="", values=(p['name'], p['mmr']))
            
        self.players_count_label.config(text=f"{len(self.manager.players)} joueur(s)")

    def add_player(self):
        name = self.name_entry.get().strip()
        mmr_str = self.mmr_entry.get().strip()

        if not name or not mmr_str:
            messagebox.showwarning("Attention", "Veuillez remplir le Pseudo et le MMR.")
            return

        try:
            mmr = int(mmr_str)
        except ValueError:
            messagebox.showerror("Erreur", "Le MMR doit être un nombre.")
            return

        self.manager.add_player(name, mmr)
        self.refresh_listbox()
        self.name_entry.delete(0, tk.END)
        self.mmr_entry.delete(0, tk.END)
        self.name_entry.focus()

    def remove_player(self):
        selected_item = self.players_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Veuillez sélectionner un joueur à supprimer.")
            return
        
        index = self.players_tree.index(selected_item[0])
        self.manager.remove_player(index)
        self.refresh_listbox()

    def on_enter_pressed(self, event):
        selected = self.players_tree.selection()
        if selected:
            item_id = selected[0]
            index = self.players_tree.index(item_id)
            player_data = self.manager.players[index]
            self.open_edit_window(index, player_data)

    def on_double_click(self, event):
        item_id = self.players_tree.identify_row(event.y)
        if item_id:
            index = self.players_tree.index(item_id)
            self.open_edit_window(index, self.manager.players[index])

    def open_edit_window(self, index, data):
        edit_win = tk.Toplevel(self.root)
        edit_win.title("MODIFIER JOUEUR")

        x = self.root.winfo_pointerx() - 150
        y = self.root.winfo_pointery() - 125

        edit_win.geometry(f"300x250+{x}+{y}")
        edit_win.configure(bg=self.bg_color)
        edit_win.grab_set()

        tk.Label(edit_win, text=f"Modifier {data['name']}", font=self.bold_font, bg=self.bg_color, fg=self.highlight_color).pack(pady=10)

        tk.Label(edit_win, text="Pseudo :", bg=self.bg_color, fg=self.text_color).pack()
        name_entry = tk.Entry(edit_win)
        name_entry.insert(0, data['name'])
        name_entry.pack(pady=5)
        name_entry.focus()

        tk.Label(edit_win, text="MMR :", bg=self.bg_color, fg=self.text_color).pack()
        mmr_entry = tk.Entry(edit_win)
        mmr_entry.insert(0, str(data['mmr']))
        mmr_entry.pack(pady=5)

        def save():
            new_name = name_entry.get().strip()
    
            if len(new_name) < 1:
                messagebox.showwarning("Erreur", "Le pseudo ne peut pas être vide !")
                return
            try:
                new_mmr = int(mmr_entry.get().strip())
                self.manager.players[index] = {"name": new_name, "mmr": new_mmr}
                self.manager.save_players()
                self.refresh_listbox()
                edit_win.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Le MMR doit être un nombre.")

        tk.Button(edit_win, text="ENREGISTRER", command=save, bg=self.highlight_color, fg="white").pack(pady=20)
        edit_win.bind('<Return>', lambda e: save())

    def generate(self):
        try:
            team_size = self.team_size_var.get()
            max_gap = int(self.max_gap_entry.get())
        except ValueError:
            messagebox.showerror("Erreur", "L'Écart MMR Max doit être un nombre.")
            return
        
        teams = self.manager.generate_teams(team_size=team_size, max_mmr_gap=max_gap)

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        if isinstance(teams, str):
            self.result_text.insert(tk.END, teams)
        else:
            mmrs = [t["total_mmr"] for t in teams]
            ecart = max(mmrs) - min(mmrs)

            all_names = [p['name'] for p in self.manager.players]
            max_name_len = max(len(name) for name in all_names) if all_names else 15
            sep_len = max_name_len + 34
            
            self.result_text.insert(tk.END, f"🏆 RÉSULTAT DU TIRAGE DES ÉQUIPES 🏆\n\n\n")
            self.result_text.insert(tk.END, f"Écart maximum de MMR : {ecart} (Limite: {max_gap})\n")
            self.result_text.insert(tk.END, "=" * sep_len + "\n")

            for team in teams:
                self.result_text.insert(tk.END, f"\n\n◈ ÉQUIPE {team['id']} | MMR TOTAL : {team['total_mmr']} ◈\n")
                self.result_text.insert(tk.END, "-" * sep_len + "\n")
                
                for p in team['players']:
                    _, short_rank = self.manager.get_rank_info(p['mmr'])
                    
                    self.result_text.insert(tk.END, f" •  {p['name'].ljust(max_name_len)}  |  MMR : {str(p['mmr']).ljust(4)}  |  ")
                    
                    if short_rank in self.rank_images:
                        self.result_text.image_create(tk.END, image=self.rank_images[short_rank])
                        self.result_text.insert(tk.END, f" {short_rank}\n")
                    else:
                        self.result_text.insert(tk.END, f"{short_rank}\n")
            
        self.result_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = TournamentApp(root)
    root.mainloop()