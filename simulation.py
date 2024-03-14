from matplotlib.image import imread
import numpy as np
from skimage import color
from brasenham import bresenham_line
from filter import filter_sinogram
import os
import glob
from PIL import Image


def clear_directory(directory_path):
    files = glob.glob(directory_path + '/*')
    for f in files:
        os.remove(f)

def simulate(input_path, angle, detectors, span, filter):
    print("filtrowanie: " + str(filter))
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

    # dla każdej pary emiter-detektor oblicz sume intensywnosci pikseli na prostej miedzy nimi
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
    sinogram_scaled = sinogram_scaled.astype(np.uint8) # konwersja na uint8
    sinogram_image = Image.fromarray(sinogram_scaled.T, mode='L')
    sinogram_resized = sinogram_image.resize(image.shape, resample=Image.NEAREST)
    sinogram_resized.save(output_dir + "/sinogram.png")

    # dodac filtrowanie
    if filter == 1:
        sinogram_filtered = filter_sinogram(sinogram)
    else:
        sinogram_filtered = sinogram
    result = np.zeros(image.shape)
    norm = np.zeros(image.shape)

    for i in range(sinogram_filtered.shape[0]):
        e_coords = [int (x + r * np.cos(i * angle)), int (y + r * np.sin(i * angle))] # współrzędne emitera
        for j in range(sinogram_filtered.shape[1]):
            d_angle = angle * i + np.pi - span / 2 + j * span / sinogram_filtered.shape[1]
            d_coords = [int (x + r * np.cos(d_angle)), int (y + r * np.sin(d_angle))]

            line_points = bresenham_line(e_coords[0], e_coords[1], d_coords[0], d_coords[1])

            for p in line_points:
                if 0 <= p[0] < image.shape[0] and 0 <= p[1] < image.shape[1]:
                    result[p[0]][p[1]] += sinogram_filtered[i][j]
                    norm[p[0]][p[1]] += 1
    
    max_norm = max([max(row) for row in norm])
    for x in range(result.shape[0]):
        for y in range(result.shape[1]):
            if norm[x][y] != 0:
                result[x][y] = result[x][y] / norm[x][y]
            else:
                result[x][y] = 0
    
    result_scaled = (255.0 / np.amax(result)) * result
    result_scaled = result_scaled.astype(np.uint8)
    result_image = Image.fromarray(result_scaled, mode='L')
    result_image.save(output_dir + "/result.png")
