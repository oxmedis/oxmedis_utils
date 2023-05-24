
from oxmedis_utils.preprocessing import data_reader
from pathlib import Path
import shutil
from glob import glob
import os
import pandas as pd
import matplotlib.image
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PIL import Image

class ddh_preprocessing():
    def __init__(self, input_dir, output_dir=None) -> None:
        self.input_dir = Path(input_dir)
        self.output_dir = self.input_dir.parent.joinpath(Path(self.input_dir.name+'_organized'))

        self.labeled_dir = 'labeled'
        self.unlabeled_dir = 'unlabeled'
        self.other = 'other'

        self.unlabed_val = 'unlabeled'

        #what tag to check if it has burned in annotations (this means patient data in image)
        self.tag_burned = (0x0028,0x0301)
        self.tag_burned_val= 'YES'
        self.burned_dir = 'burned'

        #file naming, accessionNumber_INstance Number
        self.name_ls=[(0x0008, 0x0050),(0x0020, 0x0013)]
        #modality is checked and put into other if SR (report)
        self.other_tag = (0x0008, 0x0060)
        self.other_tag_val = 'SR'

        self.img_type ='.png'

        self.read_ls = [(0x0008, 0x0050), (0x0028,0x0301),(0x0020, 0x0013), (0x0008, 0x0060), (0x0010, 0x0040),(0x0040,0x730)]
        #accession number = (0008, 0050) 
        #burned in annotation =  (0028,0301)
        #instance numbers (0020, 0013)
        #sex (0010, 0040)
        #MODALITY = (0008, 0060) 
        #breach graf deats in text (0x0040, 0xa730)
        self.im_arr_L='/home/allent/Desktop/repos/oxmedis_utils/data/left.png'
        return       
    
    def _check_arr2_in_arr1(self, img_arr):
        '''checks if array 2 is in array 1'''
        #loop in image for same size array and check the number of pixels = 255
        #checks left

        im_frame = Image.open(self.im_arr_L)
        im_arr_small=np.asarray(im_frame)
        im_arr_small = im_arr_small>200
        
        sw = sliding_window_view(img_arr, window_shape=(25,20))
        exists = None
        for i in range(sw.shape[0]):
            for j in range(sw.shape[1]):
                s=sw[i][j]>250
                if (s == im_arr_small).all():
                    exists=True     
                    #print('LARRY')  

        if exists==True:
            pass
        else:
            exists=False
            #print('rudy')
        
        return exists
    
    
    def add_LR(self,new_name,img_arr):
        '''takes array of image you define for right and left and checks the image array for the corresponding input image'''
        tag_val= self._check_arr2_in_arr1(img_arr)

        if tag_val == True:
            new_name = new_name+'_L'
        elif tag_val == False:
            new_name = new_name+'_R'
        else:
            new_name = new_name+'_noLR'
        return new_name

    def _sort(self, save_dcmMeta_csv=True):

        all_tags = []

        all_patient_paths = list(self.input_dir.iterdir())

        for patient_path in all_patient_paths:
            #read all folders for each 
            if str(patient_path)[-4:]=='xlsx':
                pass
            else:
                patient_scans_ls = list(patient_path.iterdir())

                for patient_scan in patient_scans_ls:
                    dcm_meta, img = data_reader.data_reader(str(patient_scan)).read_DcmMetadata(read_list = self.read_ls)

                    if dcm_meta[self.other_tag]==self.other_tag_val:
                        #put whatever contains the feild that you wanted to remove for other
                        #ex. modality = SR is report
                        tag_value = self.other
                    else:
                        tag_value = dcm_meta[self.tag_burned].split(':')[-1].strip("'").strip(" '")
                        tag_value=tag_value.upper()
                        #print(tag_value)
                    
                    new_name = ''

                    count = 0
                    for tag in self.name_ls:
                        if count == 0:
                            new_name = dcm_meta[tag].split(':')[-1].strip("'").strip(" '")
                        else:
                            new_name = new_name+'_'+dcm_meta[tag].split(':')[-1].strip("'").strip(" '")
                        count = count+1


                    #check/add if annotations are in im_array
                    if tag_value==self.other:
                        pass
                    elif tag_value==self.tag_burned_val:
                        pass
                    else:
                        img_arr = img.pixel_array
                        #print(img_arr[600:700,:100].mean())
                        if img_arr[600:700,:100].mean()==0:
                            tag_value = self.unlabed_val
                        else:
                            tag_value = 'labeled'
                        
                        new_name = self.add_LR(new_name,img_arr)


                    #save folder new location
                    #print(tag_value)
                    if tag_value==self.tag_burned_val:
                        dest = self.output_dir.joinpath(self.burned_dir).joinpath(patient_path.name,new_name+self.img_type)
                    elif tag_value ==self.unlabed_val:
                        dest = self.output_dir.joinpath(self.unlabeled_dir).joinpath(patient_path.name,new_name+self.img_type)
                    elif tag_value ==self.other:
                        dest = self.output_dir.joinpath(self.other).joinpath(patient_path.name,new_name+self.img_type)
                    else:
                        dest = self.output_dir.joinpath(self.labeled_dir).joinpath(patient_path.name,new_name+self.img_type)

                    if not dest.is_dir():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        if tag_value!=self.other:
                            img_arr = img.pixel_array
                            matplotlib.image.imsave(str(dest),img_arr)
                        else:
                            shutil.copyfile(patient_scan,dest)
                    
                    dcm_meta['original path']=patient_scan
                    all_tags.append(dcm_meta)
                    print(all_tags)
            
        df = pd.DataFrame(all_tags)
        if save_dcmMeta_csv == True:
            df.to_csv(f"{self.output_dir}/img_meta_data.csv", index=None)


if __name__ == "__main__":
    input_dir = "/home/allent/Desktop/repos/oxmedis_utils/data/coml0067"
    im_arr_L = "/home/allent/Desktop/repos/oxmedis_utils/data/"
    ddh_preprocessing(input_dir)._sort()
