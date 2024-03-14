from pydicom import dcmread

def read_dicom_file(file_path):
    return pydicom.dcmread(file_path)