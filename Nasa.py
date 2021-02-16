import requests
from datetime import datetime
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from time import sleep
API_KEY = ""

"""This program displays potentially hazardous asteroids on a Raspberry LCD screen.

This program accesses NASA's public API to obtain daily information about
potential dangerous asteroids and information about them such as name, 
velocity, and miles from Earth. This program then sends the information to 
an LCD screen attached to a Raspberry Pi.

"""

# Gets asteroid data from NASA's API.
# Returns a JSON object of raw data
def getDailyAsteroidData():
    today = datetime.today().strftime("%Y-%m-%d")
    response = requests.get("https://api.nasa.gov/neo/rest/v1/feed?start_date=" + \
                            today + "&api_key=" + API_KEY)
    data = response.json()["near_earth_objects"][today]
    return data

# This function takes in a float in a string format and 
# returns a turnicated version of the string float.
def shortenStringFloat(i):
    return str(int(float(i)))

# This function takes in raw data from NASA's API and 
# extracts the potentially hazardous asteroids and
# returns the data in a list.
def getPotentiallyHazardousAsteroids(data):
    data_list = ["Today's potentially hazardous asteroids:"]
    for i in data:
        if i["is_potentially_hazardous_asteroid"]:
            close = i["close_approach_data"][0]
            text = i["name"] + " will barely miss earth today by " + \
                    shortenStringFloat(close["miss_distance"]["miles"]) + " miles travelling at " + \
                    shortenStringFloat(close["relative_velocity"]["miles_per_hour"]) + " miles per hour."
            data_list.append(text)
    if len(data_list) == 1:
        data_list.append("There are no dangerous asteroids today")
    return data_list

# Takes in the data returned from getPotentiallyHazardousAsteroids
# and cleans the data into a format that is easy to read on the 2 x 16
# LCD screen.
def cleanData(data):
    cleaned_data = []
    str1 = ""
    for i in data:
        list_of_words = i.split(" ")
        for j in list_of_words:
            if (len(str1) + len(j) + 1) <=16:
                str1 = str1 + j + " "
                if j == list_of_words[-1] and i == data[-1]:
                    cleaned_data.append(str1)
            else:
                cleaned_data.append(str1)
                str1 = j + " "
                if j == list_of_words[-1] and i == data[-1]:
                    cleaned_data.append(str1)
    return cleaned_data

# Main loop of the program
def loop():
    mcp.output(3,1) # turn on LCD backlight
    lcd.begin(16,2)
    while (True):
        data = getPotentiallyHazardousAsteroids(getDailyAsteroidData())
        for i in data:
            messages = cleanData(data)
            for j in range(len(messages) - 1):
                lcd.clear()
                lcd.setCursor(0,0)
                lcd.message(messages[j] + "\n")
                lcd.message(messages[j+1])
                sleep(2)


PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.    

# Create PCF8574 GPIO adapter.
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except:
        print ('I2C Address Error !')
        exit(1)
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

if __name__ =='__main__':
    try:
        loop()
    except KeyboardInterrupt:
        lcd.clear()
