import asyncio
import json
import random
import sys
import redis.asyncio as redis

class TankBot:
    def __init__(self, team_name):
        self.team_name = team_name
        self.r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.pubsub_channel = "game:state"
        self.command_channel = "game:commands"
        self.current_state = None

    async def send_action(self, action):
        cmd = {
            "team": self.team_name,
            "action": action
        }
        await self.r.publish(self.command_channel, json.dumps(cmd))

    async def listen_game_state(self):
        pubsub = self.r.pubsub()
        await pubsub.subscribe(self.pubsub_channel)
        async for message in pubsub.listen():
            if message["type"] == "message":
                self.current_state = json.loads(message["data"])

    async def brain_loop(self):
        await asyncio.sleep(0.5)
        await self.send_action("REGISTER")
        print(f"[{self.team_name}] Registered & Waiting in Lobby...")

        while True:
            if self.current_state:
                game_status = self.current_state.get("status", "WAITING")
                players = self.current_state.get("players", {})
                my_info = players.get(self.team_name)

                if game_status == "IN_GAME" and my_info and my_info["hp"] > 0:
                    actions = ["UP", "DOWN", "LEFT", "RIGHT", "FIRE"]
                    chosen = random.choice(actions)
                    await self.send_action(chosen)
                
                elif game_status == "GAME_OVER":
                    print(f"[{self.team_name}] Game Over! Winner: {self.current_state.get('winner')}")
                    break

            await asyncio.sleep(0.1)

    async def run(self):
        await asyncio.gather(self.listen_game_state(), self.brain_loop())

if __name__ == "__main__":
    team = sys.argv[1] if len(sys.argv) > 1 else f"Team_{random.randint(10, 99)}"
    bot = TankBot(team_name=team)
    asyncio.run(bot.run())