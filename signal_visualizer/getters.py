"""
Functions that fetch and manipulate data.
Miha Lotric, April 2020
"""


from web3 import Web3
from PIL import Image
from io import BytesIO
import geohash2
import requests
import math
import json

from signal_visualizer.config import *
from signal_visualizer import draw


def get_signal_info(signal_id):
    """Call FOAM signal functions on Ethereum blockchain and FOAM API and return their results.

    Args:
        signal_id [int]: Unique identifier of a signal.
    Return:
        dict: Information about a signal. If signal exists; its radius, geohash, mint_time, coordinates, mint_time,
              burn_time, cst and how much was staked for it.
    """
    w3 = Web3(Web3.HTTPProvider(INFURA_URL))
    contract_abi = json.dumps(json.load(open(CONTRACT_ABI_PATH)))
    signals = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
    signal_info = {"exists": signals.functions.exists(signal_id).call(),  # Does signal exist [bool]
                   "radius": signals.functions.tokenRadius(signal_id).call(),  # Radius of a signal [int/float]
                   "geohash": signals.functions.tokenGeohash(signal_id).call(),  # Signal's geohash [hex]
                   "mint_time": signals.functions.tokenMintedOn(signal_id).call(),  # Time of creation - epoch [int]
                   "burn_time": signals.functions.tokenBurntOn(signal_id).call(),  # Time of deletion - epoch [int]
                   "cst": signals.functions.computeCST(CONTRACT_ADDRESS, signal_id).call().hex(),  # CST [hex]
                   "staked": signals.functions.tokenStake(signal_id).call()}  # How much FOAM staked - in WEI [int]
    if not signal_info['exists']:
        raise Exception('Invalid signal')
    # tokenGeohash from the blockchain is not an actual geohash, but Crypto-Spatial Coordinates
    # Geohash can be obtained from FOAM API 
    signal_info_api = requests.get(f"https://map-api-direct.foam.space/signal/details/{signal_info['cst']}").json()
    signal_info["geohash"] = signal_info_api["geohash"]
    signal_info["coordinates"] = geohash2.decode(signal_info_api["geohash"])
    
    return signal_info


def get_static_map(coordinates, zoom, style='dark-v10', username='mapbox'):
    """Return static Mapbox map.

    Args:
        coordinates [tuple]: Coordinates of the signal position - (latitude,longitude).
        zoom [float]: Zoom level on Mapbox map.
        style [str]: Style of Mapbox map.
        username [str]: Owner of the style.
    Return:
        bytes: Image of static map in bytes.
    """
    url = f"https://api.mapbox.com/styles/v1/{username}/{style}/static/" \
          f"{coordinates[1]},{coordinates[0]},{zoom},{BEARING},{PITCH}/" \
          f"{IMAGE_SIZE[0]}x{IMAGE_SIZE[1]}"
    payload = {"attribution": ATTRIBUTION, "logo": LOGO, "access_token": TOKEN}
    r = requests.get(url, params=payload, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        return r.content
    else:
        raise Exception("Mapbox API call failed")


def get_map(r, coordinates, zoom):
    """Return static Mapbox map with dome drawn on it.

    Args:
        r [float]: Pixel radius of the dome.
        coordinates [tuple]: Coordinates of the signal position - (latitude,longitude).
        zoom [float]: Zoom level on Mapbox map.
    Return:
        PIL.Image: Image of Mapbox static map with dome on it.
    """
    # Get under-map
    under_map = get_static_map(coordinates, zoom, username=USERNAME, style=STYLE_UNDER)
    under_map = Image.open(BytesIO(under_map)).convert("RGBA")
    # Get roads
    roads = get_static_map(coordinates, zoom, username=USERNAME, style=STYLE_ROADS_ONLY)
    roads_img = Image.open(BytesIO(roads)).convert("RGBA")
    # Get labels
    labels = get_static_map(coordinates, zoom, username=USERNAME, style=STYLE_LABELS_ONLY)
    labels_img = Image.open(BytesIO(labels)).convert("RGBA")
    # Screens
    white_screen = Image.new("RGB", IMAGE_SIZE, color=(255,)*3)
    gray_screen = Image.new("RGB", IMAGE_SIZE, 128*3)

    # Points of circle's box
    circle_box = [IMAGE_SIZE[0]/2-r,
                  IMAGE_SIZE[1]/2-r,
                  IMAGE_SIZE[0]/2+r,
                  IMAGE_SIZE[1]/2+r
                  ]
    # Points of ellipse's box
    a, b = r, r*math.cos(PITCH/180*math.pi)
    ellipse_box = [IMAGE_SIZE[0]/2-a,
                   IMAGE_SIZE[1]/2-b,
                   IMAGE_SIZE[0]/2+a,
                   IMAGE_SIZE[1]/2+b
                   ]

    # overlay = draw_ellipse(ellipse_box, IMAGE_SIZE)
    beacon, beacon_position = draw.draw_beacon(BEACON_IMG_PATH, IMAGE_SIZE, r)
    dome = draw.draw_dome(ellipse_box, circle_box, r, DOME_COLOR, TRANSPARENCY, IMAGE_SIZE)
    sun_reflection = draw.draw_sun_reflection(IMAGE_SIZE, r)

    # Put layers together
    img = under_map
    # img = Image.alpha_composite(img, overlay)  # Layer just above the bottom mapbox layer
    img = Image.alpha_composite(img, roads_img)  # Mapbox map with roads only
    img.paste(beacon, beacon_position, beacon)  # Beacon
    img = Image.alpha_composite(img, labels_img)  # Mapbox map with labels only
    img = Image.alpha_composite(img, dome)  # Dome layer
    img = Image.composite(white_screen, img, sun_reflection)  # Sun reflecting of the dome
    gray_screen.paste(img, (0, 0), img)  # Paste img on gray background to get rid of alpha channel

    return gray_screen


def get_zoom(latitude, px, meters):
    """Return appropriate zoom for latitude and distance.

    Args:
        latitude [float]: Latitude of a point.
        px [float]: Value in pixels.
        meters [float]: Value in meters.
    Return:
        float: Zoom level for Mapbox map.

    Note:
        Function gives a zoom level for which <px> pixels will be equivalent of <meters> meters in real distances.
        This changes with latitude due to Earth projection on the map.
        See more on https://docs.mapbox.com/help/glossary/zoom-level/
    """
    if abs(latitude) > 89:
        latitude = latitude/abs(latitude)*89
    zoom = math.log((EARTH_CIRCUMFERENCE*math.cos(latitude*math.pi/180)*px/meters), 2) - 9

    return zoom


def get_radius_px(radius_meters):
    """Convert and return radius from meters to pixels.

    Args:
        radius_meters [float]: Distance in meters.
    Return:
        float: Converted distance from meters to pixels.

    Note:
        The conversion works in such a way that the resulting radius has ratio with min(image_height, image_width)
        smaller than MAX_RADIUS_RATE and bigger than MIN_RADIUS_RATE.
    """
    radius = MAX_RADIUS_RATE - MIN_RADIUS_RATE
    radius /= MAX_RADIUS_METERS - MIN_RADIUS_METERS
    radius *= radius_meters - MIN_RADIUS_METERS
    radius += MIN_RADIUS_RATE
    radius *= min(IMAGE_SIZE)

    return radius
