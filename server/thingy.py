#!/usr/bin/env python

import signal
import os
import asyncio
import json
import time
import websocket
import websockets
import sfx
import gmqtt as mqtt
from dotenv import load_dotenv

# Load the .env into the environement
load_dotenv()

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = os.getenv("SERVER_PORT")
SERVER_ADRESS = f"{SERVER_HOST}:{SERVER_PORT}"


class ThingyLowLevel:
    # MQTT Config from the environement variable
    MQTT_HOST = os.getenv("MQTT_HOST")
    MQTT_PORT = int(os.getenv("MQTT_PORT"))
    MQTT_USER = os.getenv("MQTT_USER")
    MQTT_PWD = os.getenv("MQTT_PWD")

    STOP = asyncio.Event()

    # Broker endpoints
    SUB_TOPIC = "things/{}/shadow/update"
    PUB_TOPIC = "things/{}/shadow/update/accepted"

    # FLIP Enumeration
    FLIP_NORMAL, FLIP_SIDE, FLIP_UPSIDE_DOWN = 0, 1, 2
    # Lookup table : Broker flip message to enum
    _FLIP_DICT = {
        "NORMAL": FLIP_NORMAL,
        "ON_SIDE": FLIP_SIDE,
        "UPSIDE_DOWN": FLIP_UPSIDE_DOWN
    }

    def __init__(self, device, debug=False):
        self.device = device
        self.debug = debug

    async def create_connection(self):
        self.client = mqtt.Client("")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

        self.client.set_auth_credentials(self.MQTT_USER, self.MQTT_PWD)

        await self.client.connect(self.MQTT_HOST, self.MQTT_PORT)

        await self.STOP.wait()
        self.on_close()
        await self.client.disconnect()

    def on_connect(self, client, flags, rc, properties):
        self.print(f"{self.device} Connected!")
        topic = self.SUB_TOPIC.format(self.device)
        self.client.subscribe(topic, qos=0)

    def on_message(self, client, topic, payload, qos, properties):
        # self.print(f"RECV MSG: {payload}")
        data = json.loads(payload)
        if data["appId"] == "BUTTON":
            if data["data"] == "1":
                self.on_press()
            if data["data"] == "0":
                self.on_release()
        elif data["appId"] == "FLIP":
            if data["data"] in self._FLIP_DICT:
                self.on_flip(self._FLIP_DICT[data["data"]])

    def set_color(self, color):
        msg = '{"appId":"LED","data":{"color":"' + \
            color + '"},"messageType":"CFG_SET"}'
        topic = self.PUB_TOPIC.format(self.device)
        self.client.publish(topic, msg, qos=1)

    def _play(self, frequency):
        msg = '{"appId":"BUZZER","data":{"frequency":' + \
            str(frequency) + '},"messageType":"CFG_SET"}'
        topic = self.PUB_TOPIC.format(self.device)
        self.client.publish(topic, msg, qos=1)

    def play(self, frequency, t):
        self._play(frequency)
        time.sleep(t)
        self._play(0)

    def play_set(self, frequency):
        self._play(frequency)

    def on_disconnect(self, client, packet, exc=None):
        self.print(f"{self.device} Disconnected!")

    def on_subscribe(self, client, mid, qos, properties):
        self.print(f"{self.device} Subscribed!")

    def print(self, *a, **b):
        if self.debug:
            print(*a, **b)

    def ask_exit(*args):
        ThingyLowLevel.STOP.set()



class Thingy(ThingyLowLevel):

    async def ws_message(self):
        try:
            async with websockets.connect(self.uri) as ws:
                await ws.send(f"THINGY_CONNECT." + self.device)
                async for message in ws:
                    if message == "CORRECT":
                        self.set_color("00ff00")
                        sfx.songs[message](self.play)
                    if message == "INCORRECT":
                        self.set_color("ff0000")
                        sfx.songs[message](self.play)
                    if message == "VICTORY":
                        self.set_color("00ff00")
                        sfx.songs[message](self.play)
                    if message == "DEFEAT":
                        self.set_color("ff0000")
                        sfx.songs[message](self.play)
                    self.set_color("000000")


        except websockets.ConnectionClosedError:
            pass


    def __init__(self, device, loop, debug=False):
        super().__init__(device, debug)
        self.uri = f"ws://{SERVER_ADRESS}/ws"
        self.ws = websocket.create_connection(self.uri)
        task = loop.create_task(self.ws_message())

    def on_press(self):
        print(f"{self.device} Pressed!")
        self.ws.send(f"TO_CLIENT.BUTTON.{self.device}")

    def on_release(self):
        print(f"{self.device} Release!")

    def on_flip(self, orientation):
        if orientation == self.FLIP_NORMAL:
            print(f"{self.device} I'm normal")
            self.ws.send(f"TO_CLIENT.FLIP_A.{self.device}")
        elif orientation == self.FLIP_SIDE:
            print(f"{self.device} I'm on the side")
            self.ws.send(f"TO_CLIENT.FLIP_B.{self.device}")
        elif orientation == self.FLIP_UPSIDE_DOWN:
            print(f"{self.device} I'm upside down")
            self.ws.send(f"TO_CLIENT.FLIP_C.{self.device}")

    def on_close(self):
        print(f"{self.device} close !")
        self.ws.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # Set the signal to release the connection when closing the program
    loop.add_signal_handler(signal.SIGINT, Thingy.ask_exit)
    loop.add_signal_handler(signal.SIGTERM, Thingy.ask_exit)

    for i in range(1, 4)[::-1]:
        # Get configured thingy
        thingy = Thingy(f"orange-{i}", loop, debug=True)
        # Create the connection coroutine
        connection = thingy.create_connection()
        task = loop.create_task(connection)
        # break

    loop.run_until_complete(task)
