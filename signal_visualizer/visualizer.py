"""
Functions connecting the whole process. 'main' should be run if signal visualization of certain signal is requested.
'main_custom' should be run if signal visualization of any point on Earth is requested.
Miha Lotric, April 2020
"""


import io

from signal_visualizer import getters as gt


def visual_from_signal(signal_id, show=0, save_as=None, return_bytes=0):
    """Save/Show static Mapbox map with dome representing reach and position of the signal.

    Args:
        signal_id [int]: Unique identifier of a signal.
        show [bool]: If true final image is shown by default OS image viewer.
        save_as [None/str]: Path to the location where image is stored. If it is left None image is not stored.
        return_bytes [bool]: If True image in bytes is returned.
    Return:
        BytesIO: Bytes image of Mapbox static map with dome on it.
    """
    signal_info = gt.get_signal_info(signal_id)
    coordinates = float(signal_info['coordinates'][0]), float(signal_info['coordinates'][1])
    radius_meters = signal_info['radius']

    map_bytes = visual_from_data(coordinates, radius_meters, save_as=save_as, show=show, return_bytes=return_bytes)
    return map_bytes if return_bytes else None


def visual_from_data(coordinates, radius_meters, show=1, save_as=None, return_bytes=0):
    """Save/Show static Mapbox map with dome representing specified radius and coordinates.

    Args:
        coordinates [tuple]: Coordinates of the signal position - (latitude,longitude).
        radius_meters [float]: Radius of the dome in meters.
        show [bool]: If true final image is shown by default OS image viewer.
        save_as [None/str]: Path to the location where image is stored. If it is left None image is not stored.
        return_bytes [bool]: If True image in bytes is returned.
    Return:
        BytesIO: Bytes image of Mapbox static map with dome on it.
    """
    radius_px = gt.get_radius_px(radius_meters)
    zoom = gt.get_zoom(coordinates[0], radius_px, radius_meters)
    map_img = gt.get_map(radius_px, coordinates, zoom)

    if show: map_img.show()
    if save_as: map_img.save(save_as)

    if return_bytes:
        map_bytes = io.BytesIO()
        map_img.save(map_bytes, format='PNG')
        return io.BytesIO(map_bytes.getvalue())
