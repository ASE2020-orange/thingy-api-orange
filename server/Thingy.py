#!/usr/bin/env python

import signal
import os
import asyncio
import json

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

    def __init__(self, device):
        self.device = device
        # Callbacks
        self.on_press = lambda *args: None
        self.on_release = lambda *args: None

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

    def set_color(self, color):
        msg = '{"appId":"LED","data":{"color":"' + \
            color + '"},"messageType":"CFG_SET"}'
        topic = Thingy.PUB_TOPIC.format(self.device)
        self.client.publish(topic, msg)

    def on_disconnect(self, client, packet, exc=None):
        debug(f"{self.device} Disconnected!")

    def on_subscribe(self, client, mid, qos, properties):
        debug(f"{self.device} Subscribed!")

    def ask_exit(*args):
        Thingy.STOP.set()


def example():
    thingy = Thingy("orange-3")

    def on_press():
        print("Pressed!")
        thingy.set_color("ff0000")

    def on_release():
        print("Release!")
        thingy.set_color("00ff00")

    thingy.on_press = on_press
    thingy.on_release = on_release
    return thingy


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # Set the signal to release the connection when closing the program
    loop.add_signal_handler(signal.SIGINT, Thingy.ask_exit)
    loop.add_signal_handler(signal.SIGTERM, Thingy.ask_exit)

    # Get configured thingy example
    thingy = example()
    # Create the connection cooroutine
    connection = thingy.create_connection()

    loop.run_until_complete(connection)
