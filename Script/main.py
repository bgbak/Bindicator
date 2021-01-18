import datetime
import sys
from Adafruit_IO import Client
import renovasjon

# Adafruit IO User/Key
ADAFRUIT_IO_USERNAME = ""
ADAFRUIT_IO_KEY = ""
MR_GATENAVN = ""
MR_GATEKODE = ""
MR_HUSNR = ""
MR_KOMMUNENR = ""

# Create Adafruit IO Client
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Colors
COLOR_NONE = "#000000"
COLOR_BLUE = "#000099"
COLOR_GREEN = "#009900"
COLOR_ORANGE = "#ff3300"
COLOR_WHITE = "#666666"

mappings = {
    'Restavfall': COLOR_GREEN,
    'Papir': COLOR_BLUE,
    'Glass/Metallemballasje': COLOR_ORANGE,
    'Plastemballasje': COLOR_WHITE
}

# Find next monday
DATE_FORMAT = "%Y-%m-%d"
today = datetime.date.today()
next_monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)

# Get next pickups
mr = renovasjon.MinRenovasjon(gatenavn=MR_GATENAVN, gatekode=MR_GATEKODE,
                              husnr=MR_HUSNR, kommunenr=MR_KOMMUNENR, date_format='%d/%m/%Y')

calender_list = mr.calender_list
pickup = []
for entry in calender_list:
    if entry[1] != 'Matavfall':
        if entry[3].strftime(DATE_FORMAT) == next_monday.strftime(DATE_FORMAT):
            pickup.append(entry[1])

# Test list length and send colors
if len(pickup) == 2:
    aio.send_data('bindicator-1', mappings[pickup[0]])
    print(mappings[pickup[0]])
    aio.send_data('bindicator-2', mappings[pickup[1]])
    print(mappings[pickup[1]])
elif len(pickup) == 1:
    print(mappings[pickup[0]])
    aio.send_data('bindicator-1', mappings[pickup[0]])
    aio.send_data('bindicator-2', mappings[pickup[0]])
else:
    sys.exit()
