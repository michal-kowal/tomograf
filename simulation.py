from matplotlib.image import imread
import numpy as np
from skimage import color
from brasenham import bresenham_line
from filter import filter_sinogram
import os
import glob
from PIL import Image
from patient import Patient
from dicom_handler import read_dicom_file, save_dicom_file


def clear_directory(directory_path):
    files = glob.glob(directory_path + '/*')
    for f in files:
        os.remove(f)

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def simulate(input_path, angle, detectors, span, filter, step, dicom, patient: Patient = None):
    print("filtrowanie: " + str(filter))
    print("kroki pośrednie: " + str(step))
    print("dicom: " + str(dicom))
    output_dir = "./result"
    sinogram_iterations_dir = "./sinogram_iterations"
    result_iterations_dir = "./result_iterations"
    dicom_dir = "./dicom"
    create_folder_if_not_exists(output_dir)
    create_folder_if_not_exists(sinogram_iterations_dir)
    create_folder_if_not_exists(result_iterations_dir)
    create_folder_if_not_exists(dicom_dir)

    clear_directory(dicom_dir) if dicom == 1 else None
    if step == 1:
        clear_directory(sinogram_iterations_dir)
        clear_directory(result_iterations_dir)
    else:
        clear_directory(output_dir)
    
    step_counter = 0

    if input_path[-4:] == ".dcm":
        image_path = output_dir + "/image.png"
        image, _ = read_dicom_file(input_path)
        image_scaled = (255.0 / np.amax(image)) * image
        image_scaled = image_scaled.astype(np.uint8)
        image_dcm = Image.fromarray(image_scaled, mode='L')
        image_dcm.save(image_path)
    else:
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
        if step == 1:
            sinogram_step_scaled = (255.0 / np.amax(sinogram)) * sinogram
            sinogram_step_scaled = sinogram_step_scaled.astype(np.uint8)
            sinogram_step_image = Image.fromarray(sinogram_step_scaled.T, mode='L')
            sinogram_step_resized = sinogram_step_image.resize(image.shape, resample=Image.NEAREST)
            sinogram_step_resized.save(sinogram_iterations_dir + "/sinogram_iteration_" + str(step_counter) + ".png")
            step_counter += 1
    
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

    step_counter = 0
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
        if step == 1:
            result_step = result.copy()
            for k in range(result_step.shape[0]):
                for l in range(result_step.shape[1]):
                    if norm[k][l] != 0:
                        result_step[k][l] = result_step[k][l] / norm[k][l]
                    else:
                        result_step[k][l] = 0
            result_step_scaled = (255.0 / np.amax(result_step)) * result_step
            result_step_scaled = result_step_scaled.astype(np.uint8)
            result_step_image = Image.fromarray(result_step_scaled, mode='L')
            result_step_image.save(result_iterations_dir + "/result_iteration_" + str(step_counter) + ".png")
            step_counter += 1
    
    max_norm = max([max(row) for row in norm])
    for j in range(result.shape[0]):
        for i in range(result.shape[1]):
            if norm[j][i] != 0:
                result[j][i] = result[j][i] / norm[j][i]
            else:
                result[j][i] = 0
    
    result_scaled = (255.0 / np.amax(result)) * result
    result_scaled = result_scaled.astype(np.uint8)
    result_image = Image.fromarray(result_scaled, mode='L')
    result_image.save(output_dir + "/result.png")

    if dicom == 1:
        save_dicom_file(result_scaled, patient.name, patient.id, patient.date, patient.comment)
