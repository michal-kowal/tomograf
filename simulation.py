from matplotlib.image import imread
import numpy as np
from skimage import color
import brasenham


def simulate(input_path, angle, detectors, span):
    image = imread(input_path)
    try:
        image = color.rgb2gray(image)
    except ValueError:
        pass

    x = image.shape[0] / 2 # współrzędna x środka obrazu
    y = image.shape[1] / 2 # współrzędna y środka obrazu
    r = np.sqrt(x**2 + y**2) # promień

    # zamiana na radiany
    angle = np.deg2rad(float(angle))
    span = np.deg2rad(float(span))

