import sys
import time
import requests
import os.path
import shutil
from datetime import datetime, timedelta
from inky import InkyWHAT
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math

def processTide():
    startDayString = (datetime.now() + timedelta(days=-1)).strftime("%Y%m%d")
    endDayString = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    tide_url = (
        "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&begin_date="
        + startDayString
        + "&end_date="
        + endDayString
        + "&datum=MLLW&station=8514322&time_zone=lst_ldt&units=english&interval=hilo&format=json&application=NOS.COOPS.TAC.TidePred"
    )
    tidestring = "H -> L"
    nexttide = "00:00"
    try:
        tides = requests.get(tide_url, timeout=10).json()
        for i in range(0, len(tides["predictions"])):
            tide = tides["predictions"][i]
            tideTime = datetime.strptime(tide["t"], "%Y-%m-%d %H:%M")
            if tideTime > datetime.now():
                tide = tides["predictions"][i - 1]
                if tide["type"] == "H":
                    tidestring = "H > L"
                else:
                    tidestring = "L > H"
                nexttide = "(" + tideTime.strftime("%-I:%M") + ")"
                break
    except Exception:
        pass
    return [tidestring, nexttide]

def placeText(image, pos, y, text, font, fill):
    theSize = font.getsize(text)
    image.text(((pos * 100) + (50 - (theSize[0]/2)), y), text, font=font, fill=fill)

def fetchAndCacheImage(image):
    theName = image[image.rfind("/") + 1 :]
    if not os.path.isfile(theName):
        try:
            with open(theName, "wb") as out_file:
                rawImg = requests.get(image, stream=True, timeout=15)
                shutil.copyfileobj(rawImg.raw, out_file)
                del rawImg
        except Exception:
            return None
    return theName

def safe_get(source, keys, default=0):
    value = source
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value
 

WIND_DIRECTIONS = [
    'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
]

def default_data():
    return {
        "tempf": 0,
        "hiTemp": 0,
        "loTemp": 0,
        "humidity": 0,
        "windspeedmph": 0,
        "winddir": 0,
        "windgustmph": 0,
        "hl": {"tempf": {"h": 0, "l": 0}},
    }

data = default_data()
forecastResult = {"forecastOverview": []}
try:
    result = requests.get(
        "https://lightning.ambientweather.net/devices?public.slug=19f3efb7371679fea5c94c6733e52d7b",
        timeout=10,
    )
    print(result.json())
    data = result.json()["data"][0]["lastData"]
except Exception:
    pass

try:
    forecastResult = requests.get(
        "https://www.weatherlink.com/embeddablePage/getData/acf9850534924ff0915ce847633ab609",
        timeout=10,
    ).json()
except Exception:
    pass

inkyphat = InkyWHAT('black')
inkyphat.set_border(inkyphat.WHITE)
var = 1
iDeg = safe_get(data, ["winddir"], 0)
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
# convert knots
C_KTS = 0.868976
textSpacing = 100 
halfWidest = 50 
updateCount = 0
last_update_had_error = False
while var == 1 :

    tideData = processTide()
    tidestring = tideData[0]
    tidenext = tideData[1]

    updateCount = updateCount + 1
    morningImgUrl = None
    noonImgUrl = None
    eveningImgUrl = None
    nightImgUrl = None
    for i in forecastResult["forecastOverview"]:
        morningImgUrl = i["morning"]["weatherIconUrl"]
        noonImgUrl = i["afternoon"]["weatherIconUrl"]
        eveningImgUrl = i["evening"]["weatherIconUrl"]
        nightImgUrl = i["night"]["weatherIconUrl"]


    theName = fetchAndCacheImage(morningImgUrl) if morningImgUrl else None
    morningImg = Image.open(theName) if theName else None
    theName = fetchAndCacheImage(noonImgUrl) if noonImgUrl else None
    noonImg = Image.open(theName) if theName else None
    theName = fetchAndCacheImage(eveningImgUrl) if eveningImgUrl else None
    eveningImg = Image.open(theName) if theName else None
    theName = fetchAndCacheImage(nightImgUrl) if nightImgUrl else None
    nightImg = Image.open(theName) if theName else None

    image = Image.new('P', (inkyphat.WIDTH, inkyphat.HEIGHT))
    d = ImageDraw.Draw(image)
    if morningImg:
        image.paste(morningImg, (int((50 - (morningImg.width / 2))), 190))
    if noonImg:
        image.paste(noonImg, (int(150 - (noonImg.width / 2)), 190))
    if eveningImg:
        image.paste(eveningImg, (int(250 - (eveningImg.width / 2)), 190))
    if nightImg:
        image.paste(nightImg, (int(350 - (nightImg.width / 2)), 190))
    placeText(d, 0, 170, "Morning", smallfnt, inkyphat.BLACK)
    placeText(d, 1, 170, "Afternoon", smallfnt, inkyphat.BLACK)
    placeText(d, 2, 170, "Evening", smallfnt, inkyphat.BLACK)
    placeText(d, 3, 170, "Night", smallfnt, inkyphat.BLACK)
    tempf = safe_get(data, ["tempf"], 0)
    hiTemp = safe_get(data, ["hiTemp"], 0)
    loTemp = safe_get(data, ["loTemp"], 0)
    if not tempf :
        tempf = str(math.floor((int(hiTemp) + int(loTemp)) / 2))
    placeText(d, 0, 20, str(int(round(float(tempf)))) + "F", fnt, inkyphat.BLACK)
    placeText(d, 1, 20, str(int(round(safe_get(data, ["humidity"], 0)))) + "%", fnt, inkyphat.BLACK)
    placeText(d, 2, 20, str(int(round(safe_get(data, ["windspeedmph"], 0) * C_KTS))) + "KTS", fnt, inkyphat.BLACK)
    placeText(d, 3, 20, WIND_DIRECTIONS[iPosition], fnt, inkyphat.BLACK)
    placeText(
        d,
        0,
        80,
        str(int(round(safe_get(data, ["hl", "tempf", "h"], 0))))
        + "/"
        + str(int(round(safe_get(data, ["hl", "tempf", "l"], 0)))),
        fnt,
        inkyphat.BLACK,
    )
    placeText(d, 2, 80, str(int(round(safe_get(data, ["windgustmph"], 0) * C_KTS))) + "KTS", fnt, inkyphat.BLACK)
    placeText(d, 1, 80, tidestring, fnt, inkyphat.BLACK);
    placeText(d, 1, 110, tidenext, fnt, inkyphat.BLACK);
    now = datetime.now()
    lastUpdate = now.strftime("%H:%M")
    if last_update_had_error:
        lastUpdate = lastUpdate + "!"
    placeText(d, 3, 280, lastUpdate, smallfnt, inkyphat.BLACK)
#    placeText(d, 3.4, 280, "1.0", smallfnt, inkyphat.BLACK)
    inkyphat.set_image(image)
    inkyphat.show()
    time.sleep(300)
    last_update_had_error = False
    update_succeeded = False
    for _ in range(0, 3):
        try:
            result = requests.get(
                "https://lightning.ambientweather.net/devices?public.slug=19f3efb7371679fea5c94c6733e52d7b",
                timeout=10,
            )
            if not result.headers.get("content-type") == "application/json; charset=utf-8" :
                time.sleep(5)
                continue
            data = result.json()["data"][0]["lastData"]
        except Exception:
            last_update_had_error = True
            break

        try:
            forecastResult = requests.get(
                "https://www.weatherlink.com/embeddablePage/getData/acf9850534924ff0915ce847633ab609",
                timeout=10,
            )
            if not forecastResult.headers.get("content-type") == "application/json" : 
                time.sleep(5)
                continue
            forecastResult = forecastResult.json()
        except Exception:
            last_update_had_error = True
            break

        tideData = processTide()
        tidestring = tideData[0]
        tidenext = tideData[1]
        update_succeeded = True
        break

    if not update_succeeded:
        last_update_had_error = True
    
    if morningImg:
        del morningImg
    if noonImg:
        del noonImg
    if eveningImg:
        del eveningImg
    if nightImg:
        del nightImg
