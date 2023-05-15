
import SimpleITK as sitk
import pydicom
from pathlib import Path

class data_reader():
    def __init__(self,path) -> None:
        self.path = path
        pass

    def read_DcmtoSITK(self):
        image = sitk.ReadImage(
            sitk.ImageSeriesReader_GetGDCMSeriesFileNames(self.path)
        )
        return 

    def read_DcmMetadata(self):
        '''Reads filepath, returns dictionary'''
        ds = pydicom.read_file(self.path, force=True)
        dcm_meta_dic={}
        tags=(list(ds.dir()))

        for dcmtag in tags:
            if hasattr(ds, dcmtag):
                dcm_meta_dic[dcmtag] = str(getattr(ds, dcmtag))
            else:
                dcm_meta_dic[dcmtag] = None

        return dcm_meta_dic, img

    def readCsv(self):
        '''Reads csv
        Returns df'''
        return 
