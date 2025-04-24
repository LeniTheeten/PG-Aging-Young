import random
import pygame
import time
import threading
from threading import Thread
import paho.mqtt.client as mqtt
from collections import Counter

MQTT_BROKER_URL = "mqtt.eclipseprojects.io"
MQTT_BROKER_PORT = 1883
MQTT_KEEP_ALIVE = 60

mqtt_connected = threading.Event()

sensor_max = 600

is_muziek_bezig = False

muziek_dictionary = {
    0: r"C:\Users\lenit\OneDrive - UGent\Documenten\school\2IO\semester 2\project gebruiksgericht ontwerp\code active harmony\full test\BeatIt1.mp3",
    1: r"C:\Users\lenit\OneDrive - UGent\Documenten\school\2IO\semester 2\project gebruiksgericht ontwerp\code active harmony\full test\BeatIt2.mp3",
    2: r"C:\Users\lenit\OneDrive - UGent\Documenten\school\2IO\semester 2\project gebruiksgericht ontwerp\code active harmony\full test\BeatIt3.mp3",
    3: r"C:\Users\lenit\OneDrive - UGent\Documenten\school\2IO\semester 2\project gebruiksgericht ontwerp\code active harmony\full test\BeatIt4.mp3",
    4: r"C:\Users\lenit\OneDrive - UGent\Documenten\school\2IO\semester 2\project gebruiksgericht ontwerp\code active harmony\full test\BeatIt5.mp3",
    5: r"C:\Users\lenit\OneDrive - UGent\Documenten\school\2IO\semester 2\project gebruiksgericht ontwerp\code active harmony\full test\BeatIt6.mp3"
}
#Bericht ontvangen ActiveHarmony/18:1F:3B:BD:9E:7C:/909
#Bericht ontvangen ActiveHarmony/20:88:4E:DA:D4:D4:/886
#Bericht ontvangen ActiveHarmony/74:C7:7A:1B:5A:E0:/975
#Bericht ontvangen ActiveHarmony/1C:31:7B:1B:5A:E0:/8
#Bericht ontvangen ActiveHarmony/4C:F1:77:1B:5A:E0:/946

#arduino_dict = {'18:1F:3B:BD:9E:7C': 'mac1', '20:88:4E:DA:D4:D4': 'mac2', '74:C7:7A:1B:5A:E0': 'mac3', '1C:31:7B:1B:5A:E0': 'mac4', '4C:F1:77:1B:5A:E0': 'mac5'}
arduino_dict = {'20:88:4E:DA:D4:D4': 'mac1', '74:C7:7A:1B:5A:E0': 'mac2', '4C:F1:77:1B:5A:E0': 'mac3', '1C:31:7B:1B:5A:E0': 'mac4'}
# Hou globaal de sensorwaarden bij, per Arduino
# Initialiseer ze allemaal op -1
tegel_sensor_waardes = dict()
for mac in arduino_dict.keys():
    tegel_sensor_waardes[mac] = sensor_max + 1

# Functie die de volgorde van de tegels genereert, afhankelijk van het aantal ingevoerde Arduino's
def genereer_volgorde_tegels():
    tegel_namen = list(arduino_dict.values())
    volgorde = []
    vorige = None

    while len(volgorde) < 6:
        keuze = random.choice(tegel_namen)
        if keuze != vorige:
            volgorde.append(keuze)
            vorige = keuze

    print(f"Volgorde van tegels: {volgorde}")
    return volgorde

# Functie die het spel afspeelt
def speel_muziek(muziek_index) -> None:
    global is_muziek_bezig
    is_muziek_bezig = True #blokkeer berichtverwerking
    print(f"Speel {muziek_dictionary[muziek_index]}")
    pygame.mixer.music.load(muziek_dictionary[muziek_index])
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    is_muziek_bezig = False

def connect_mqtt(client, userdata, flags, rc):
    if rc == 0:
        print("Geconnecteerd")
        mqtt_connected.set()  # verbinding is gelukt
        topic = f"ActiveHarmony/+/+"
        client.subscribe(topic)
        print(f"Geabonneerd op topic: {topic}")  # Abonneer je direct na het verbinden
    else:
        print("Verbinden mislukt")

# Callback functie voor ontvangen berichten
def on_message(client, userdata, message):
    global tegel_sensor_waardes
    if message is None:
        return
    
    #print(f"Bericht ontvangen {message.topic}")
    parts = message.topic.split("/")
    if len(parts)<3:
        print(f"Ongeldig ontvangen: {message.topic}")
        return
    mac = parts[1]
    try:
        sensor_int = int(parts[2])
        tegel_sensor_waardes[mac] = sensor_int # Opslaan in variabele
    except ValueError:
        print(f"Fout bij het omzetten van sensorwaarde naar int: {parts[2]}")
    #print(received_message)

def wacht_op_tegel_veranderd(timeout, min_veranderings_waarde) -> tuple:
    """
    Deze code wacht op tegel verandering
    """
    while any (sensor_waarde < sensor_max for sensor_waarde in tegel_sensor_waardes.values()):
        print("wacht tot alle tegels losgelaten zijn")
        time.sleep(0.1)

    vorige_toestand = dict(tegel_sensor_waardes)  # Maak een kopie van de huidige toestand

    while True:
        # Bereken van alle tegels hoe veel ze veranderd zijn
        tegels_met_hun_veranderings_waarde = dict()

        for mac, sensor_waarde in tegel_sensor_waardes.items():
            if mac in vorige_toestand and sensor_waarde != vorige_toestand[mac]:
                verschil = abs(sensor_waarde - vorige_toestand[mac])
                tegels_met_hun_veranderings_waarde[mac] = verschil

        # Vind de tegel en de grootste verandering
        if tegels_met_hun_veranderings_waarde:
            mac = max(tegels_met_hun_veranderings_waarde, key=tegels_met_hun_veranderings_waarde.get)
            waarde = tegels_met_hun_veranderings_waarde[mac]
            if waarde > min_veranderings_waarde:
                print(f"Sensor {mac} heeft een verandering van {waarde}")
                return mac, tegel_sensor_waardes[mac]
            time.sleep(timeout)


def stuur_lichtcommando(topic) -> None:
    #print(f"MQTT-bericht verzonden: {topic}")
    client.publish(topic, "1") 

def stuur_leds(rood, groen, blauw, leds: list) -> None:
    print(f"Stuur leds {leds}")
    for mac in leds:
        stuur_lichtcommando(f"ActiveHarmony/{mac}/{rood}/{groen}/{blauw}")

def stuur_tijdelijk_leds(rood, groen, blauw, leds: list, duur: int) -> None:
    stuur_leds(rood, groen, blauw, leds)
    time.sleep(duur)
    stuur_leds(0, 0, 0, leds)

def knipper_leds(rood, groen, blauw, leds: list, aantal_keer: int, duur: int) -> None:
    for i in range(aantal_keer):
        stuur_tijdelijk_leds(rood, groen, blauw, leds, duur)

def stuur_fout(leds: list):
    knipper_leds(255,0,0,leds,5,1)
    time.sleep (1)

def stuur_tijdelijk_wit(leds: list):
    stuur_tijdelijk_leds(255,255,255, leds, 3)

def stuur_wit(leds: list):
    stuur_leds(255, 255, 255, leds)

def stuur_blauw(leds: list):
    stuur_tijdelijk_leds(0, 0, 255, leds, 1)

def stuur_groen(leds: list):
    stuur_tijdelijk_leds(0,255, 0,leds, 1)



def do_reactie (mac, value, referentie, stap, al_correct) -> bool:
    # Controleer of het MAC-adres in de arduino_dict zit
    if mac not in arduino_dict:
        print(f"Ongeldig MAC-adres: {mac}")
        return False, False
    if value > sensor_max:
        stuur_fout(list(arduino_dict.keys()))
        time.sleep(1)
        wacht_op_alles_uit()
        return False
    
    if sensor_correct(mac, referentie,stap):
        #if mac not in al_correct:
        stuur_groen([mac])
        time.sleep(2)
            #al_correct.add(mac)
        #if al_correct:
        #stuur_wit([mac])
        #stuur_wit(list(al_correct))
        speel_muziek(stap)
        return True
    else:
        stuur_fout(list(arduino_dict.keys()))
        time.sleep(1)
        #wacht tot er nergens meer op gestaan wordt
        wacht_op_alles_uit()
        #volgorde_licht(referentie)
        #print(referentie)
        return False

def krijg_sensors_die_aanliggen() -> list:
    """
    Verkrijg een lijst van sensoren die aan staan
    """
    sensors_die_aanliggen = []
    for mac, sensor_waarde in tegel_sensor_waardes.items():
        if sensor_waarde < sensor_max:
            sensors_die_aanliggen.append(mac)
    return sensors_die_aanliggen

def wacht_op_alles_uit():
    """
    Blijf wachten tot alle sensoren zijn uitgeschakeld
    Ondertussen worden de sensoren die aan staan rood gekleurd
    """
    sensors_aan = krijg_sensors_die_aanliggen()
    while sensors_aan:
        print(f"Wachten tot alles uit is. Deze sensoren liggen nog aan: {sensors_aan}")
        stuur_fout(sensors_aan)
        time.sleep(1)
        sensors_aan = krijg_sensors_die_aanliggen()

def volgorde_licht(referentie):
    for mac_naam in referentie:
        for mac_adres,naam in arduino_dict.items():
            if naam == mac_naam:
                stuur_tijdelijk_wit([mac_adres])
                time.sleep (2)

def opstart_spel():
    #stuur_leds(0,255,0,['18:1F:3B:BD:9E:7C'])
    wacht_op_alles_uit()
    print("Alle sensoren zijn uit")
    stuur_blauw(list(arduino_dict.keys()))
    time.sleep(1)
    #stuur_leds(0,0,0,list(arduino_dict.keys()))
    print("We kunnen beginnen")

def sensor_correct (mac, referentie, stap) -> bool:
    mac_naam = referentie[stap]
    for amac, naam in arduino_dict.items():
        if naam == mac_naam and amac == mac:
            return True
    return False

def speel_het_spel(referentie):
    opstart_spel()

    volgorde_licht(referentie)
    stap = 0
    al_correct = set()

    while stap < len(referentie):
        mac,value = wacht_op_tegel_veranderd(0.5, sensor_max)

        correct = do_reactie(mac, value, referentie, stap, al_correct)
        print(f"Stap {stap} correct!")
        if correct:
            stap += 1
            al_correct.add(mac)
            print(f"Reeds correcte tegels: {len(al_correct)}")
        else:
            stap = 0
            al_correct.clear()
            print("Fout! Terug naar stap 0")
            time.sleep (5)
            print(referentie)
            volgorde_licht(referentie)

    print("Je hebt het spel perfect gespeeld")
    knipper_leds(0,255,0,list(al_correct),5,1)
    volledig_gespeeld = True
    return volledig_gespeeld

if __name__ == "__main__":
    # Initialiseer de pygame mixer voor audio
    pygame.mixer.init()

    # Maak een MQTT-client aan en verbind enkele functies
    #client = mqtt.Client()
    client = mqtt.Client()
    client.loop_start()
    client.on_connect = connect_mqtt
    client.on_message = on_message
    client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT, MQTT_KEEP_ALIVE)

    mqtt_connected.wait()  # wacht tot verbinding is gemaakt

    # Bedenk de puzzel die moet worden opgelost
    referentie = genereer_volgorde_tegels()
     
    # Speel het spel tot volledig gespeeld
    volledig_gespeeld = False

    while not volledig_gespeeld:
        volledig_gespeeld = speel_het_spel(referentie)

