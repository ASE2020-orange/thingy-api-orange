#!/usr/bin/env python

import signal
import os
import asyncio
import json
import time

import gmqtt as mqtt
from dotenv import load_dotenv

# Load the .env into the environement
load_dotenv()

DEBUG = True


def debug(*a, **b):
    if DEBUG:
        print(*a, **b)


class Thingy:
    # MQTT Config from the environement variable
    MQTT_HOST = os.getenv("MQTT_HOST")
    MQTT_PORT = int(os.getenv("MQTT_PORT"))
    MQTT_USER = os.getenv("MQTT_USER")
    MQTT_PWD = os.getenv("MQTT_PWD")

    # Broker endpoints
    SUB_TOPIC = "things/{}/shadow/update"
    PUB_TOPIC = "things/{}/shadow/update/accepted"

    STOP = asyncio.Event()

    client = None

    # FLIP Enumeration
    FLIP_NORMAL, FLIP_SIDE, FLIP_UPSIDE_DOWN = 0, 1, 2
    # Lookup table : Broker flip message to enum
    _FLIP_DICT = {
        "NORMAL": FLIP_NORMAL,
        "ON_SIDE": FLIP_SIDE,
        "UPSIDE_DOWN": FLIP_UPSIDE_DOWN
    }

    def __init__(self, device):
        self.device = device
        # Callbacks
        self.on_press = lambda *args: None
        self.on_release = lambda *args: None
        self.on_flip = lambda *args: None

    async def create_connection(self):
        self.client = mqtt.Client("")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

        self.client.set_auth_credentials(Thingy.MQTT_USER, Thingy.MQTT_PWD)

        await self.client.connect(Thingy.MQTT_HOST, Thingy.MQTT_PORT)

        await Thingy.STOP.wait()
        await self.client.disconnect()

    def on_connect(self, client, flags, rc, properties):
        debug(f"{self.device} Connected!")
        topic = Thingy.SUB_TOPIC.format(self.device)
        client.subscribe(topic, qos=0)

    def on_message(self, client, topic, payload, qos, properties):
        # debug('RECV MSG:', payload)
        data = json.loads(payload)
        if data["appId"] == "BUTTON":
            if data["data"] == "1":
                self.on_press()
            if data["data"] == "0":
                self.on_release()
        elif data["appId"] == "FLIP":
            if data["data"] in Thingy._FLIP_DICT:
                self.on_flip(Thingy._FLIP_DICT[data["data"]])

    def set_color(self, color):
        msg = '{"appId":"LED","data":{"color":"' + \
            color + '"},"messageType":"CFG_SET"}'
        topic = Thingy.PUB_TOPIC.format(self.device)
        self.client.publish(topic, msg, qos=1)

    def _play(self, frequency):
        msg = '{"appId":"BUZZER","data":{"frequency":' + \
            str(frequency) + '},"messageType":"CFG_SET"}'
        topic = Thingy.PUB_TOPIC.format(self.device)
        self.client.publish(topic, msg, qos=1)

    def play(self, frequency, t):
        self._play(frequency)
        time.sleep(t)
        self._play(0)

    def play_set(self, frequency):
        self._play(frequency)

    def on_disconnect(self, client, packet, exc=None):
        debug(f"{self.device} Disconnected!")

    def on_subscribe(self, client, mid, qos, properties):
        debug(f"{self.device} Subscribed!")

    def ask_exit(*args):
        Thingy.STOP.set()


def example1():
    thingy = Thingy("orange-3")

    def on_press():
        print("Pressed!")
        thingy.set_color("ffffff")
        thingy.play(440, 1)

    def on_release():
        print("Release!")
        thingy.set_color("000000")

    def on_flip(orientation):
        if orientation == Thingy.FLIP_NORMAL:
            print("I'm normal")
        elif orientation == Thingy.FLIP_SIDE:
            print("I'm on the side")
        elif orientation == Thingy.FLIP_UPSIDE_DOWN:
            print("I'm upside down")

    thingy.on_press = on_press
    thingy.on_release = on_release
    thingy.on_flip = on_flip
    return thingy


def example2():
    """
    Play music with 3 notes:
    Each oriantation is a note :
        - normal : c
        - side : d
        - upside down : e
    """
    # using a array to have a mutable variable int for the frequency
    freq = [261]
    is_pressed = [False]

    thingy = Thingy("orange-3")

    def on_press():
        print("Pressed!")
        thingy.set_color("ffffff")
        thingy.play_set(freq[0])
        is_pressed[0] = True

    def on_release():
        print("Release!")
        thingy.set_color("000000")
        thingy.play_set(0)
        is_pressed[0] = False

    def on_flip(orientation):
        if orientation == Thingy.FLIP_NORMAL:
            print("I'm normal")
            freq[0] = 261  # c4
        elif orientation == Thingy.FLIP_SIDE:
            print("I'm on the side")
            freq[0] = 293  # d4
        elif orientation == Thingy.FLIP_UPSIDE_DOWN:
            print("I'm upside down")
            freq[0] = 329  # e4

        if is_pressed[0] is True:
            thingy.play_set(freq[0])

    thingy.on_press = on_press
    thingy.on_release = on_release
    thingy.on_flip = on_flip
    return thingy


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # Set the signal to release the connection when closing the program
    loop.add_signal_handler(signal.SIGINT, Thingy.ask_exit)
    loop.add_signal_handler(signal.SIGTERM, Thingy.ask_exit)

    # Get configured thingy example
    # thingy = example1()
    thingy = example2()

    # Create the connection coroutine
    connection = thingy.create_connection()

    loop.run_until_complete(connection)
