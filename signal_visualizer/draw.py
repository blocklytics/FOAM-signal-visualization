"""
Functions reponsible for drawing a dome, beacon and reflection on the map.
Miha Lotric, April 2020
"""


from PIL import Image, ImageDraw, ImageFilter
import math

from signal_visualizer.config import *


def draw_ellipse(ellipse_box, screen_size):
    """Return transparent screen with a ellipse on it.

    Args:
        ellipse_box [list]: Coordinates of top-left corner, bottom-right corner of box around the ellipse.
                            [x1, y1, x2, y2] where P1 is top-left and P2 is bottom-right.
        screen_size [tuple]: Pixel size of the image - (width, height).
    Return:
        PIL.Image: Transparent image with an ellipse drawn on it.
    """
    screen = Image.new('RGBA', screen_size, (0,)*4)  # Transparent screen
    draw = ImageDraw.Draw(screen)
    draw.ellipse(ellipse_box, fill=DOME_COLOR + (int(255 * TRANSPARENCY - 15),))

    return screen


def draw_dome(ellipse_box, circle_box, r, color, transparency, screen_size):
    """Return transparent screen with a dome on it.

    Args:
        ellipse_box [list]: Coordinates of top-left corner, bottom-right corner of box around the ellipse.
                            Like [x1, y1, x2, y2] where P1 is top-left and P2 is bottom-right.
        circle_box [list]: Coordinates of top-left corner, bottom-right corner of box around the circle.
        r [float]: Pixel radius of the dome.
        color [tuple]: RGB representation of dome color.
        transparency [float]: Intensity of the alpha channel. Ranges from 0 to 1.
        screen_size [tuple]: Pixel size of the image - (width, height).
    Return:
        PIL.Image: Transparent image with an dome drawn on it.
    """
    p1 = ellipse_box[:2]
    p2 = ellipse_box[2:]
    dome = Image.new('RGBA', screen_size, (0,)*4)
    dome_draw = ImageDraw.Draw(dome)
    # Draw top semi-circle
    dome_draw.chord(circle_box, fill=color+(int(255 * transparency),), width=2*r, start=180, end=0)
    # Draw bottom semi-ellipse
    dome_draw.chord(ellipse_box, fill=color+(int(255 * transparency),), width=2*r, start=0, end=180)
    
    # Draw arcs representing top ellipse outline
    dalpha = 25 / 200
    for i in range(200):
        # Transparency decreases with distance from initial arc
        # Eventually transparency of the arc and top semi-circle is the same
        alpha = int(255*transparency + 25 - dalpha*i)
        # Upper outline
        draw_arc(dome_draw, (p1[0], p1[1]+0.2*i, p2[0], p2[1]-0.2*i), fill=color+(alpha,), start=0, end=180, width=2)
        # Bottom outline
        draw_arc(dome_draw, (p1[0], p1[1]-0.2*i, p2[0], p2[1]+0.2*i), fill=color+(alpha,), start=0, end=-180, width=2)

    return dome


def draw_beacon(beacon_file, screen_size, r):
    """Return resized image of beacon with its position on the screen.

    Args:
        beacon_file [str]: Path to the image of the beacon.
        screen_size [tuple]: Pixel size of the image - (width, height).
        r [float]: Pixel radius of the dome.

    Return:
        tuple -> (PIL.Image, tuple): Transparent image with a beacon on it and tuple specifying its center
                                     position on the screen.
    """
    beacon = Image.open(beacon_file)
    baseheight = int(r/2)
    b_width, b_height = beacon.size
    hpercent = (baseheight / float(b_height))
    wsize = int((float(b_width) * float(hpercent)))
    beacon = beacon.resize((wsize, baseheight), Image.ANTIALIAS)
    offset = (-0.514*wsize, -0.881*baseheight)  # How far is beacon from the center (top left corner)
    position = (int(screen_size[0]/2 + offset[0]), int(screen_size[1]/2 + offset[1]))

    return beacon, position


def draw_sun_reflection(screen_size, r):
    """Return mask with bright white spot on it.

     Args:
        screen_size [tuple]: Pixel size of the image - (width, height).
        r [float]: Pixel radius of the dome.

    Return:
        PIL.Image: Transparent image with a white fading circle drawn on it.
    """
    w, h = screen_size
    x1, y1 = w/2 - 0.74*r, h/2 - 0.66*r
    x2, y2 = w/2 - 0.45*r, h/2 - 0.25*r
    blur_radius = 0.13 * r

    img = Image.new("RGBA", screen_size, color=(0,)*4)
    draw = ImageDraw.Draw(img)
    draw.ellipse((x1, y1, x2, y2), fill=(255,)*3+(150,))
    img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    return img


def draw_arc(draw, bbox, start, end, fill, width=1, segments=5000):
    """Hack that looks similar to PIL's draw.arc(), but can specify a line width.

    Based on code from Pieter Ennes from
    https://stackoverflow.com/questions/7070912/creating-an-arc-with-a-given-thickness-using-pils-imagedraw
    """
    # radians
    start *= math.pi / 180
    end *= math.pi / 180
    # angle step
    da = (end - start) / segments
    # shift end points with half a segment angle
    start -= da / 2
    end -= da / 2
    # ellipse radii
    rx = (bbox[2] - bbox[0]) / 2
    ry = (bbox[3] - bbox[1]) / 2
    # box centre
    cx = bbox[0] + rx
    cy = bbox[1] + ry
    # segment length
    ln = (rx+ry) * da / 2.0

    for i in range(segments):
        # angle centre
        a = start + (i+0.5) * da
        # x,y centre
        x = cx + math.cos(a) * rx
        y = cy + math.sin(a) * ry
        # derivatives
        dx = -math.sin(a) * rx / (rx+ry)
        dy = math.cos(a) * ry / (rx+ry)
        draw.line([(x-dx*ln, y-dy*ln), (x+dx*ln, y+dy*ln)], fill=fill, width=width)
