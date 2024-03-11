from matplotlib.image import imread
import numpy as np
from skimage import color
from brasenham import bresenham_line
import os
import glob
from PIL import Image


def clear_directory(directory_path):
    files = glob.glob(directory_path + '/*')
    for f in files:
        os.remove(f)

def simulate(input_path, angle, detectors, span):
    output_dir = "./result"
    clear_directory(output_dir)

    image = imread(input_path)
    try:
        image = color.rgb2gray(image)
    except ValueError:
        pass

    x = image.shape[0] / 2 # współrzędna x środka obrazu
    y = image.shape[1] / 2 # współrzędna y środka obrazu
    r = np.sqrt(x**2 + y**2) # promień
    
    # zamiana na radiany
    angle = np.deg2rad(angle)
    span = np.deg2rad(span)
    sinogram = np.zeros((int(2 * np.pi / angle), detectors))

    for e_id, e_angle in zip(range(int(2 * np.pi / angle)), np.arange(0, 2 * np.pi, angle)):
        e_coords = [int (x + r * np.cos(e_angle)), int (y + r * np.sin(e_angle))] # współrzędne emitera
        
        detector_first = e_angle + np.pi - span / 2 # kąt pierwszego detektora
        detector_last = e_angle + np.pi + span / 2 # kąt ostatniego detektora
        for d_id, d_angle in zip(range(detectors), np.arange(detector_first, detector_last, span / detectors)):
            d_coords = [int (x + r * np.cos(d_angle)), int (y + r * np.sin(d_angle))]
            line_points = bresenham_line(e_coords[0], e_coords[1], d_coords[0], d_coords[1])
            points_counter = 0
            sum = 0
            for point in line_points: 
                # sprawdź czy punkt leży w obrazie
                if 0 <= point[0] < image.shape[0] and 0 <= point[1] < image.shape[1]:
                    sum += image[point[0]][point[1]]
                    points_counter += 1
            if points_counter > 0:
                sinogram[e_id][d_id] = sum / points_counter
            else:
                sinogram[e_id][d_id] = 0
    
    sinogram_scaled = (255.0 / np.amax(sinogram)) * sinogram
    sinogram_scaled = sinogram_scaled.astype(np.uint8)
    sinogram_image = Image.fromarray(sinogram_scaled.T, mode='L')
    sinogram_resized = sinogram_image.resize(image.shape, resample=Image.NEAREST)
    sinogram_resized.save(output_dir + "/sinogram.png")