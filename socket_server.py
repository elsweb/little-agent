import asyncio
import json
import threading

import websockets


class RobotSocketServer:

    def __init__(
        self,
        host="127.0.0.1",
        port=8765
    ):

        self.host = host
        self.port = port

        self.clients = set()

        self.loop = None
        self.thread = None


    # ==================================================
    # CLIENTE WEBSOCKET
    # ==================================================

    async def handler(self, websocket):

        print()
        print("========================================")
        print("🟢 HTML CONECTADO AO SOCKET")
        print("========================================")
        print()

        self.clients.add(websocket)

        try:

            async for message in websocket:

                print(
                    "JAVASCRIPT -> PYTHON:",
                    message
                )

        except Exception as e:

            print(
                "ERRO SOCKET:",
                e
            )

        finally:

            self.clients.discard(websocket)

            print()
            print("========================================")
            print("⚪ HTML DESCONECTADO")
            print("========================================")
            print()


    # ==================================================
    # SERVIDOR
    # ==================================================

    async def server(self):

        async with websockets.serve(
            self.handler,
            self.host,
            self.port
        ):

            print()
            print("========================================")
            print("🤖 SOCKET SERVER INICIADO")
            print("========================================")
            print(
                f"ws://{self.host}:{self.port}"
            )
            print()

            await asyncio.Future()


    # ==================================================
    # THREAD
    # ==================================================

    def _run(self):

        self.loop = asyncio.new_event_loop()

        asyncio.set_event_loop(
            self.loop
        )

        self.loop.run_until_complete(
            self.server()
        )


    # ==================================================
    # INICIAR
    # ==================================================

    def start(self):

        if self.thread is not None:

            return

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self.thread.start()


    # ==================================================
    # ENVIO ASYNC
    # ==================================================

    async def _broadcast(
        self,
        payload
    ):

        if not self.clients:

            print(
                "⚠️ NENHUM HTML CONECTADO"
            )

            return


        message = json.dumps(
            payload,
            ensure_ascii=False
        )


        clients = list(
            self.clients
        )


        for client in clients:

            try:

                await client.send(
                    message
                )

            except Exception as e:

                print(
                    "ERRO AO ENVIAR PARA CLIENTE:",
                    e
                )

                self.clients.discard(
                    client
                )


    # ==================================================
    # PYTHON -> HTML
    # ==================================================

    def send(
        self,
        event,
        data=None
    ):

        print()
        print("########################################")
        print("# PYTHON -> SOCKET -> JAVASCRIPT")
        print("########################################")


        payload = {

            "event": event,

            "data": data

        }


        print(
            json.dumps(
                payload,
                ensure_ascii=False
            )
        )


        if self.loop is None:

            print(
                "⚠️ SOCKET AINDA NÃO ESTÁ INICIADO"
            )

            return False


        if not self.clients:

            print(
                "⚠️ NENHUM HTML CONECTADO"
            )

            return False


        asyncio.run_coroutine_threadsafe(

            self._broadcast(
                payload
            ),

            self.loop

        )


        return True