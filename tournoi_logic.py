import random
import copy
import json
import os

class TournamentManager:
    def __init__(self):
        self.players = []
        self.save_file = "joueurs.json"
        self.load_players()

    def load_players(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r", encoding="utf-8") as f:
                self.players = json.load(f)
                print(f"{len(self.players)} joueurs chargés.")

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

    def generate_teams(self, team_size, rand_mmr_diff=40, max_mmr_gap=150, iterations=1000):
        total_players = len(self.players)
        
        if total_players == 0:
            return "❌ Erreur : Aucun joueur enregistré."
            
        if total_players % team_size != 0:
            return "❌ Erreur : Impossible de faire des équipes complètes."

        num_teams = total_players // team_size
        adjusted_players = []
        
        for p in self.players:
            variance = random.randint(-rand_mmr_diff, rand_mmr_diff)
            adjusted_players.append({
                "name": p["name"],
                "base_mmr": p["mmr"],
                "effective_mmr": p["mmr"] + variance,
                "variance": variance
            })

        unique_draws = {}

        for _ in range(iterations):
            random.shuffle(adjusted_players)
            teams = [{"id": i+1, "players": [], "total_mmr": 0, "base_total_mmr": 0} for i in range(num_teams)]
            
            for i, player in enumerate(adjusted_players):
                team_index = i % num_teams
                teams[team_index]["players"].append(player)
                teams[team_index]["total_mmr"] += player["effective_mmr"]
                teams[team_index]["base_total_mmr"] += player["base_mmr"]
            
            base_mmrs = [t["base_total_mmr"] for t in teams]
            base_diff = max(base_mmrs) - min(base_mmrs)
            
            team_signatures = []
            for t in teams:
                names = tuple(sorted([p["name"] for p in t["players"]]))
                team_signatures.append(names)
            
            match_signature = tuple(sorted(team_signatures))
            
            if match_signature not in unique_draws:
                unique_draws[match_signature] = {
                    "diff": base_diff,
                    "teams": copy.deepcopy(teams)
                }

        all_draws = list(unique_draws.values())
        all_draws.sort(key=lambda x: x["diff"])

        acceptable_draws = [draw for draw in all_draws if draw["diff"] <= max_mmr_gap]
        final_draw = random.choice(acceptable_draws) if acceptable_draws else all_draws[0]

        return final_draw["teams"]