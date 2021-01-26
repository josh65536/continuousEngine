import pygame, asyncio, multiprocessing, threading, time
from continuousEngine import *
from continuousEngine.network.client import *
from continuousEngine.network.server import NetworkGameServer

# this "bot" is controlled manually by a human
# it's intended to make it easier to test and debug another bot, by running it against this one

class Player:
    def __init__(self, game, game_name, team, *args):
        self.team = team
        threading.Thread(target=lambda:asyncio.run(NetworkGameServer(unsafe=True, clean=True).serve()), daemon=True).start()

        time.sleep(0.1)

        self.loop = asyncio.new_event_loop()
        self.server = self.loop.run_until_complete(asyncio.open_connection(host="localhost", port=port, limit=2**20))
        id = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))

        send(self.server, {"action":"create", "name":game_name, "id":id, "args":args})

        d = {
            "action":"join",
            "user":"everyone-else",
            "id":id,
            "team":"spectator"
            }
        send(self.server,d)

        async def run_human():
            pygame.init()
            await (NetworkGame(await asyncio.get_running_loop().run_in_executor(None, game, *args)).join(await (asyncio.open_connection(host="localhost", port=port, limit=2**20)), id, self.team, "human"))

        multiprocessing.Process(target=lambda:asyncio.run(run_human())).start()
        # multiprocessing.Process(target=lambda:(pygame.init(), game(*args).run())).start()

        print('yay')
    def _receive_state(self, state):
        send(self.server, {"action":"override_state", "state":state})
    def _receive_move(self, move, state):
        if move["player"]!=self.team:
            send(self.server, {"action":"move", "move":move})
    def make_move(self):
        while 1:
            msg = self.loop.run_until_complete(receive(self.server))
            if msg["action"]!="move" or msg["move"]==None or msg["move"]["player"]!=self.team:
                continue
            return msg["move"]