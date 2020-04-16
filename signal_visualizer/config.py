"""
Settings for fetching data from blockchain and APIs; drawing a dome and beacon; and converting radius from meters to
pixels.
Miha Lotric, April 2020
"""


from dotenv import load_dotenv
import os


# Specify absolute path, so files within module can be accessed from any location
pck_dir = os.path.dirname(os.path.dirname(__file__))
# Load env variables from .env file
load_dotenv()

# Ethereum
CONTRACT_ADDRESS = "0x36f16a0d35B866CdD0f3C3FA39e2Ba8F48b099d2"
CONTRACT_ABI_PATH = os.path.normpath(os.path.join(pck_dir, "abi/SignalToken.json"))
INFURA_TOKEN = os.getenv("WEB3_INFURA_PROJECT_ID")
INFURA_URL = f"https://mainnet.infura.io/v3/{INFURA_TOKEN}"

# Calibration settings
MIN_RADIUS_METERS = 1000  # Signal's minimal reach for a signal
MAX_RADIUS_METERS = 25000  # Signal's maximum reach for a signal
MIN_ABS_LAT = 0
MAX_ABS_LAT = 90
MIN_RADIUS_RATE = 0.15  # Ratio: dome_radius / min(screen_height, screen_width)
MAX_RADIUS_RATE = 0.45  # Ratio: dome_radius / min(screen_height, screen_width)
EARTH_CIRCUMFERENCE = 40075017

# Mapbox settings 
USERNAME = "mihalotric"
STYLE_UNDER = "ck6s9r9eo159o1imddog74tk7"
STYLE_LABELS_ONLY = "ck6s9wvs21d6h1invq8ehzo4d"
STYLE_ROADS_ONLY = "ck72j8rpq00z41jsdgw23c08f"
TOKEN = os.getenv('MAPBOX_TOKEN')
ATTRIBUTION = 'false'
LOGO = 'false'
PITCH = 50
BEARING = 0

# Graphics settings
IMAGE_SIZE = 1000, 750
DOME_COLOR = 255, 255, 255
TRANSPARENCY = .15  # Degree of transparency, 0-1
BEACON_IMG_PATH = os.path.normpath(os.path.join(pck_dir, "media/beacons/tower1.png"))
