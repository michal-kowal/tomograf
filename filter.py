import scipy.signal as signal
import numpy as np

def filter_sinogram(sinogram):
    result = np.zeros_like(sinogram)
    kernel = [-4 / (49 * np.pi ** 2), 0,
              -4 / (25 * np.pi ** 2), 0,
              -4 / (9 * np.pi ** 2), 0,
              -4 / (np.pi ** 2), 1,
              -4 / (np.pi ** 2), 0,
              -4 / (9 * np.pi ** 2), 0,
              -4 / (25 * np.pi ** 2), 0,
              -4 / (49 * np.pi ** 2)]

    for i in range(sinogram.shape[0]):
        result[i, :] = signal.convolve(sinogram[i, :], kernel, mode='same', method='direct')

    return result
