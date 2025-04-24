import curses
import json
import sys
import time

import paho.mqtt.client as mqtt

from config import MQTT_BROKER_PORT, MQTT_BROKER_URL, MQTT_KEEP_ALIVE

MAX_MESSAGES_ON_SCREEN = 4
SENSOR_VALUE_ON = 100
SENSOR_VALUE_OFF = 1000

mac_address: str = ""  # We'll fill this with an existing MAC address to simulate a device
received_messages: list = list()  # We'll keep the top N received messages and log to screen
sent_messages: list = list()  # We'll keep the top N sent messages and log to screen
topic_subscriptions: set = set()  # We'll keep track of the topics we're subscribed to
sensor_status: bool = False  # Is the sensor on or off?
led_status: bool = False  # Is the LED on or off?
color: dict = {"red": 0, "green": 0, "blue": 0}  # The color of the LED (background of the screen)

mac_addresses = [
    "18:1F:3B:BD:9E:7C", 
    "20:88:4E:DA:D4:D4", 
    "74:C7:7A:1B:5A:E0", 
    "1C:31:7B:1B:5A:E0", 
    "4C:F1:77:1B:5A:E0"
]

def get_mac_address(index: int) -> str:
    """
    Get an existing mac address from the list, by index
    :param index: The index of the mac address to get
    :return: The mac address as a string
    """
    return mac_addresses[index]


def update_screen(stdscr) -> None:
    """
    Just for simulation purposes
    Use the terminal background color to simulate an RGB LED
    We only support these 8 colors (black if "off"):
    - 255/255/255 = white
    - 255/0/0 = red
    - 0/255/0 = green
    - 0/0/255 = blue
    - 255/255/0 = yellow
    - 255/0/255 = magenta
    - 0/255/255 = cyan
    - 0/0/0 = black

    Also write some extra info like mac address, sensor status and the last N messages
    :param stdscr: The standard screen object from curses
    """
    if led_status:
        if color.get("red", 0) and color.get("green", 0) and color.get("blue", 0):
            led_color = curses.COLOR_WHITE
        elif color.get("red", 0) and color.get("green", 0):
            led_color = curses.COLOR_YELLOW
        elif color.get("red", 0) and color.get("blue", 0):
            led_color = curses.COLOR_MAGENTA
        elif color.get("green", 0) and color.get("blue", 0):
            led_color = curses.COLOR_CYAN
        elif color.get("red", 0):
            led_color = curses.COLOR_RED
        elif color.get("green", 0):
            led_color = curses.COLOR_GREEN
        elif color.get("blue", 0):
            led_color = curses.COLOR_BLUE
        else:
            led_color = curses.COLOR_BLACK
    else:
        led_color = curses.COLOR_BLACK

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, led_color)
    stdscr.bkgd(' ', curses.color_pair(1))

    # Just for simulation purposes, 
    # write the status of the sensor to the screen
    stdscr.clear()  # clear the screen before writing new text

    left = 2


    text = "Sensor = ON" if sensor_status else "Sensor = OFF"
    stdscr.addstr(3, left, text, curses.color_pair(1))

    text = f"MAC Address: {mac_address}"
    stdscr.addstr(5, left, text, curses.color_pair(1))
    
    for i, topic in enumerate(topic_subscriptions):
        top = 6 + i
        stdscr.addstr(top, left, f"Subscribed to: {topic}", curses.color_pair(1))

    stdscr.addstr(8, left, f"Last {MAX_MESSAGES_ON_SCREEN} messages received:", curses.color_pair(1))

    for i, message in enumerate(received_messages):
        top = 9 + i
        stdscr.addstr(top, left, f"{message.topic}", curses.color_pair(1))

    stdscr.addstr(13 + MAX_MESSAGES_ON_SCREEN, left, f"Last {MAX_MESSAGES_ON_SCREEN} messages sent:", curses.color_pair(1))

    for i, topic in enumerate(sent_messages):
        top = 14 + MAX_MESSAGES_ON_SCREEN + i
        stdscr.addstr(top, left, topic, curses.color_pair(1))

    stdscr.refresh()


def publish_sensor_status(mqtt_client) -> None:
    """
    Sends its sensor status to the MQTT broker via a JSON payload
    :param mqtt_client: The MQTT client instance to use for publishing
    """
    # Instead of sending boolean true / false, 
    # we send an integer value in the topic
    sensor_int_value = SENSOR_VALUE_ON if sensor_status else SENSOR_VALUE_OFF
    topic = f"ActiveHarmony/{mac_address}/{sensor_int_value}"
    payload = {
        # We don't use a payload, since everything is in the topics
    }
    mqtt_client.publish(topic, json.dumps(payload), qos=1)

    # Write the last N sent messages on the screen
    if len(sent_messages) >= MAX_MESSAGES_ON_SCREEN:
        sent_messages.pop()
    sent_messages.insert(0, topic)

def announce_device(mqtt_client) -> None:
    """
    Sends an announcement message to the MQTT broker
    :param mqtt_client: The MQTT client instance to use for publishing
    """
    topic = f"ActiveHarmony/{mac_address}/announce"
    payload = {
        # We don't use a payload, since everything is in the topics
    }
    mqtt_client.publish(topic, json.dumps(payload), qos=1)

def on_sensor_message_received(mqtt_client, userdata, message, topic):
    """
    Every time we receive a message that controls the LED, 
    we update the color and status
    """
    global color
    global led_status
    global message_on_screen
    
    # Adapt the global color dict variable with the received color
    # The topic is in the format: ActiveHarmony/{mac_address}/{red}/{green}/{blue}
    topic_parts = topic.split("/")
    color["red"] = int(topic_parts[-3])
    color["green"] = int(topic_parts[-2])
    color["blue"] = int(topic_parts[-1])

    led_status = False if topic.endswith("/0/0/0") else True

    message_on_screen = f"on_sensor_message_received: {topic}"

    stdscr = userdata
    update_screen(stdscr)

def on_mqtt_message(mqtt_client, userdata, message):
    """
    Receives messages from the MQTT broker and prints them to the console
    """
    # While we're simulating, just show the last N messages on screen
    received_messages.insert(0, message)
    if len(received_messages) > MAX_MESSAGES_ON_SCREEN:
        received_messages.pop()
    
    on_sensor_message_received(mqtt_client, userdata, message, message.topic)


if __name__ == "__main__":
    # Read parameter from command line to know which device tp simulate
    # We can run the script with a parameter to simulate different devices
    # e.g. `python simulate_button.py 0` or `python simulate_button.py 1`
    # If no parameter is given, we use the first device
    mac_address_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    mac_address = get_mac_address(mac_address_index)

    client = mqtt.Client()
    client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT, MQTT_KEEP_ALIVE)

    # Listen to incoming messages that control the LED
    client.on_message = on_mqtt_message

    # Subscribe to the topic that controls the LED
    subscription_topic = f"ActiveHarmony/{mac_address}/+/+/+"
    client.subscribe(subscription_topic)
    topic_subscriptions.add(subscription_topic)

    # Start the loop to process received messages
    client.loop_start()

    # Announce the device to the world
    #announce_device(client)

    def main(stdscr):
        global sensor_status  # Tell Python to use the global variable instead of creating a local one 

        curses.curs_set(0)  # Hide the cursor
        stdscr.nodelay(1)  # Make getch() non-blocking
        stdscr.timeout(100)  # Refresh every 100ms

        client.user_data_set(stdscr)  # Make sure we can access the screen bg in the event handler

        update_screen(stdscr)

        while True:
            key = stdscr.getch()
            if key == 27:  # ESC key
                break
            elif key == ord(' '):  # Space bar
                sensor_status = not sensor_status

            # Publish the sensor status when it has changed
            publish_sensor_status(client)

            update_screen(stdscr)

            time.sleep(0.5)
            

    curses.wrapper(main)
