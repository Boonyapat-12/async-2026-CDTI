import asyncio
import json
import os
import redis.asyncio as redis

class GameDashboard:
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.pubsub_channel = "game:state"

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render_board(self, state):
        grid_size = state.get("grid_size", 10)
        players = state.get("players", {})
        bullets = state.get("bullets", [])
        is_over = state.get("is_over", False)
        winner = state.get("winner", None)

        grid = [[" . " for _ in range(grid_size)] for _ in range(grid_size)]
        
        for b in bullets:
            grid[b["y"]][b["x"]] = " * "

        for team_name, info in players.items():
            if info.get("hp", 0) > 0:
                grid[info["y"]][info["x"]] = f" {team_name[0].upper()} "

        self.clear_screen()
        print("=" * 40)
        print(" 🎮 TANK BATTLE ARENA (LAST TANK STANDING) ")
        print("=" * 40)
        print("┌" + "─" * (grid_size * 3) + "┐")
        for row in grid:
            print("│" + "".join(row) + "│")
        print("└" + "─" * (grid_size * 3) + "┘")
        
        print("\n📊 TEAM STATUS & HP:")
        for team_name, info in players.items():
            hp = info["hp"]
            status = "ALIVE" if hp > 0 else "DESTROYED 💀"
            bar_count = max(0, hp // 10)
            hp_bar = "█" * bar_count + "░" * (10 - bar_count)
            print(f"   • [{team_name[0].upper()}] {team_name:10s} | HP: {hp:3d} [{hp_bar}] | Status: {status}")

        # แสดงป้ายประกาศผู้ชนะเมื่อเกมจบ
        if is_over:
            print("\n" + "=" * 40)
            print(f" 🏆 GAME OVER! WINNER: {winner} 🏆")
            print("=" * 40)

    async def run(self):
        pubsub = self.r.pubsub()
        await pubsub.subscribe(self.pubsub_channel)
        async for message in pubsub.listen():
            if message["type"] == "message":
                state = json.loads(message["data"])
                self.render_board(state)

if __name__ == "__main__":
    dashboard = GameDashboard()
    try:
        asyncio.run(dashboard.run())
    except KeyboardInterrupt:
        pass