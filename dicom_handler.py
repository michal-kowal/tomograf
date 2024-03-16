import pydicom
import numpy
from patient import Patient

def read_dicom_file(file_path):
    data = pydicom.dcmread(file_path)
    size = (int(data.Rows), int(data.Columns))
    image = numpy.zeros(size, dtype=data.pixel_array.dtype)
    image[:, :] = data.pixel_array
    return image, Patient(data.PatientName, '', '', '')

def save_dicom_file(image, name, id, date, comment):
    test_file = pydicom.data.get_testdata_files("rtplan.dcm")[0]
    data = pydicom.dcmread(test_file)
    data.PatientName = name
    data.PatientID = id
    data.StudyDate = date
    data.ImageComments = [comment]
    data.PixelData = image.tobytes()
    data.Rows = image.shape[0]
    data.Columns = image.shape[1]
    data.BitsAllocated = 8
    data.BitsStored = 8
    data.HighBit = 7

    file_path = "./dicom/result.dcm"
    data.save_as(file_path)