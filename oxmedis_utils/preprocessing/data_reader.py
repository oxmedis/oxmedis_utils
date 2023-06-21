
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

    def read_DcmMetadata(self,read_list='ALL'):
        '''Reads filepath, returns dictionary'''
        #of read is a list it will only read those files.
        ds = pydicom.read_file(self.path, force=True)
        
        dcm_meta_dic={}
        
        if read_list == 'ALL':
            #this will read all/some duplicates
            tags=(list(ds.dir()))

            for dcmtag in tags:
                if hasattr(ds, dcmtag):
                    dcm_meta_dic[dcmtag] = str(getattr(ds, dcmtag))
                else:
                    dcm_meta_dic[dcmtag] = None

            #reads dcm based on values feild (captures more than just ds.dir())
            val = list(ds.values())
            for i in range(len(val)):
                dcmtag = str(val[i]).split(')')[0]
                dcmval= str(val[i]).split(')')[1]
                dcm_meta_dic[dcmtag] = str(dcmval)
        
        else:
            for i in read_list:
                try:
                    dcmval=ds[i].value
                    dcm_meta_dic[i] = str(dcmval)
                except:
                    if i == (40, 769):
                        dcm_meta_dic[i]= 'None'
                    else:
                        try:
                            #get breach data 
                            d = ds[0x0040, 0xa730][3]
                            tmp= {}
                            for j in d.iterall():
                                if str(j).find('(0040, a160)') == -1:
                                    pass
                                else:
                                    dcm_meta_dic[i]=str(j.value)
                                
                        except:
                            dcm_meta_dic[i] = None

        return dcm_meta_dic, ds

    def readCsv(self):
        '''Reads csv
        Returns df'''
        return 
