"""
Testing map creation without actual signals. Parameters are coordinates of cities at different latitude, and radii of
range from 1km to 25km. At different latitude mapbox behaves differently, so it is important to test a large range of
different altitudes with different radii.
Miha Lotric, April 2020
"""

from signal_visualizer.visualizer import visual_from_data


places = {"Quito": (-0.140287, -78.478916),
          "New York": (40.717801, -73.998909),
          "Nairobi": (-1.288896, 36.825475),
          "Aberdeen": (57.164475, -2.107236),
          "London": (51.510950, -0.103222),
          "Tartu": (58.377172, 26.781315),
          "Baghdad": (33.306328, 44.334720),
          "Tokyo": (35.670280, 139.773867),
          "Jakarta": (-6.232227, 106.873743),
          "Lima District": (-12.077113, -77.063483),
          "Melburne": (-37.829621, 145.023435),
          "Longyearbyen": (78.223704, 15.635087),
          "Ushuaia": (-54.805557, -68.305552)}


# Make maps for all cities provided with radii of 1km, 5km and 25km (1km is min and 25km max for FOAM signals)
for name, coordinates in places.items():
    for i in (1, 5, 25):
        file_name = f"output/testing_images/{coordinates[0]:.1f}_{name}_{i}.png"
        main_custom(file_name, coordinates, 1000*i, save=1, show=0)
    print(name + " done")

# Uncomment to run for a single city
# ("output/testing_images/random_signal.png", places['Aberdeen'], 15000, save=0, show=1)
