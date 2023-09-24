import sys
import time
import requests
import os.path
import shutil
from datetime import datetime
from inky import InkyWHAT
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math

def placeText(image, pos, y, text, font, fill):
    theSize = font.getsize(text)
    image.text(((pos * 100) + (50 - (theSize[0]/2)), y), text, font=font, fill=fill)

def fetchAndCacheImage(image):
    theName = image[image.rfind("/")+1:];
    if not os.path.isfile(theName):
        with open(theName, "wb") as out_file:
            rawImg = requests.get(image,stream=True)
            shutil.copyfileobj(rawImg.raw, out_file)
            del rawImg
    return theName
 

WIND_DIRECTIONS = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
    ]

result = requests.get("https://www.weatherlink.com/embeddablePage/getData/acf9850534924ff0915ce847633ab609");
print(result.json())

data = result.json()

inkyphat = InkyWHAT('black')
inkyphat.set_border(inkyphat.WHITE)
var = 1
iDeg = data["windDirection"]
if iDeg <= 11.25 :
    iPosition = 0;
elif iDeg <= 33.75 :
    iPosition = 1;
elif iDeg <= 56.25 :
    iPosition = 2;
elif iDeg <= 78.75 :
    iPosition = 3;
elif iDeg <= 101.25 :
    iPosition = 4;
elif iDeg <= 123.75 :
    iPosition = 5;
elif iDeg <= 146.25 :
    iPosition = 6;
elif iDeg <= 168.75 :
    iPosition = 7;
elif iDeg <= 191.25 :
    iPosition = 8;
elif iDeg <= 213.75 :
    iPosition = 9;
elif iDeg <= 236.25 :
    iPosition = 10;
elif iDeg <= 258.75 :
    iPosition = 11;
elif iDeg <= 281.25 :
    iPosition = 12;
elif iDeg <= 303.75 :
    iPosition = 13;
elif iDeg <= 326.25 :
    iPosition = 14;
elif iDeg <= 348.75 :
    iPosition = 15;
elif iDeg <= 360.00 :
    iPosition = 0;

fnt=ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Regular.ttf', 24)
smallfnt=ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Regular.ttf', 14)
widestSize = fnt.getsize("00KTS")
textSpacing = 100 
halfWidest = 50 
updateCount = 0
while var == 1 :
    updateCount = updateCount + 1
    for i in data["forecastOverview"]:
        morningImgUrl = i["morning"]["weatherIconUrl"]
        noonImgUrl = i["afternoon"]["weatherIconUrl"]
        eveningImgUrl = i["evening"]["weatherIconUrl"]
        nightImgUrl = i["night"]["weatherIconUrl"]


    theName = fetchAndCacheImage(morningImgUrl)
    morningImg = Image.open(theName)
    theName = fetchAndCacheImage(noonImgUrl)
    noonImg = Image.open(theName)
    theName = fetchAndCacheImage(eveningImgUrl)
    eveningImg = Image.open(theName)
    theName = fetchAndCacheImage(nightImgUrl)
    nightImg = Image.open(theName)

    image = Image.new('P', (inkyphat.WIDTH, inkyphat.HEIGHT))
    d = ImageDraw.Draw(image)
    image.paste(morningImg, (int((50-(morningImg.width/2))),190))
    image.paste(noonImg, (int(150-(noonImg.width/2)),190))
    image.paste(eveningImg, (int(250-(eveningImg.width/2)), 190))
    image.paste(nightImg, (int(350-(nightImg.width/2)),190))
    placeText(d, 0, 170, "Morning", smallfnt, inkyphat.BLACK)
    placeText(d, 1, 170, "Afternoon", smallfnt, inkyphat.BLACK)
    placeText(d, 2, 170, "Evening", smallfnt, inkyphat.BLACK)
    placeText(d, 3, 170, "Night", smallfnt, inkyphat.BLACK)
    if not data["temperatureFeelLike"] :
        data["temperatureFeelLike"] = str(math.floor((int(data["hiTemp"]) + int(data["loTemp"])) / 2))
    placeText(d, 0, 20, data["temperatureFeelLike"] + "F", fnt, inkyphat.BLACK) 
    placeText(d, 1, 20, data["humidity"] + "%", fnt, inkyphat.BLACK)
    placeText(d, 2, 20, data["wind"] + "KTS", fnt, inkyphat.BLACK)
    placeText(d, 3, 20, WIND_DIRECTIONS[iPosition], fnt, inkyphat.BLACK)
    placeText(d, 0, 80, data["hiTemp"] + "/" + data["loTemp"], fnt, inkyphat.BLACK)
    placeText(d, 2, 80, data["gust"] + "KTS", fnt, inkyphat.BLACK)
    now = datetime.now()
    lastUpdate = now.strftime("%H:%M")
    placeText(d, 3, 280, lastUpdate, smallfnt, inkyphat.BLACK)
#    placeText(d, 3.4, 280, "1.0", smallfnt, inkyphat.BLACK)
    inkyphat.set_image(image)
    inkyphat.show()
    time.sleep(1800)
    result = requests.get("https://www.weatherlink.com/embeddablePage/getData/acf9850534924ff0915ce847633ab609");
    data = result.json()
    del morningImg
    del noonImg
    del eveningImg
    del nightImg
