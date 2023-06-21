
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
import datetime

class handy_preprocessing():
    def __init__(self, input_dir, output_dir=None) -> None:
        self.input_dir = Path(input_dir)
        self.output_dir = self.input_dir.parent.joinpath(Path(self.input_dir.name+'_organized'))
        #sub output folder names
        self.image_dir = 'Images'
        self.labels_dir = 'Lables'
        self.raw_dir = 'Raw'

        #what tag to check if it has burned in annotations (this means patient data in image)
        self.tag_burned = (0x0028,0x0301)

        #file naming, AccessionNumber_InstanceNumber
        self.name_ls=[(0x0008, 0x0050),(0x0020, 0x0013)]

        self.img_type ='.png'

        #To do: set theses as a dictionary with keys would make more s
        self.read_ls = [(0x0008, 0x0050), (0x0020, 0x0013), (0x0010, 0x0040), (0x0028,0x0301), (0x0040,0x730)]
        self.read_ls_names = ['Accession Number', 'Instance Number','Sex','','Burned in Annotation', 'TextField']
        #accession number = (0008, 0050) 
        #instance numbers (0020, 0013)
        #sex (0010, 0040)
        #sex (0010, 0040)
        #sex (0010, 0040)    
        
        #burned in annotation =  (0028,0301)
        return       
    
    def _clean_df_colnames(self, df):
        # first replace column names with read_ls_names, then also take columns if they havve break and split into other columns.
        for col in range(len(self.read_ls_names)):
            col_name_old = df.columns[col]
            col_name_new = self.read_ls_names[col]
            df.rename(columns={col_name_old: col_name_new}, inplace=True)
        return df
    
    def get_name_from_tags(self, dcm_meta):
        new_name = ''
        count = 0
        for tag in self.name_ls:
            if count == 0:
                new_name = dcm_meta[tag].split(':')[-1].strip("'").strip(" '")
            else:
                new_name = new_name+'_'+dcm_meta[tag].split(':')[-1].strip("'").strip(" '")
            count = count+1
        
        return new_name


    def _combine_csvs(self):
        return

    def _sort(self, save_dcmMeta_csv=True):

        all_tags = []
        all_patient_paths = list(self.input_dir.iterdir())

        for patient_path in all_patient_paths:
            #read all folders for each 
            if str(patient_path)[-3:]=='xml':
                pass
            else:
                patient_scans_ls = list(patient_path.iterdir())

                for patient_scan in patient_scans_ls:
                    dcm_meta, img = data_reader.data_reader(str(patient_scan)).read_DcmMetadata()

                    new_name = self.get_name_from_tags(dcm_meta)

                    #save raw data folder (copy original folder)
                    dest = self.output_dir.joinpath(self.image_dir).joinpath(patient_path.name,self.raw_dir)
                    if not dest.is_dir():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(patient_path+patient_scan,dest)

                    #save image dir
                    dest = self.output_dir.joinpath(self.image_dir).joinpath(patient_path.name,new_name+self.img_type)
                    if not dest.is_dir():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    img_arr = img.pixel_array
                    matplotlib.image.imsave(str(dest),img_arr)
                    
                    dcm_meta['original path']=patient_scan

                    all_tags.append(dcm_meta)
                    print(all_tags)
            
        df = pd.DataFrame(all_tags)
        df = self._clean_df_colnames(df)
        df = self._clean_df_text_column_split(df)

        if save_dcmMeta_csv == True:
            dest = self.output_dir.joinpath(self.labels_dir)
            if not dest.is_dir():
                dest.parent.mkdir(parents=True, exist_ok=True)

            df.to_csv(f"{self.labels_dir}/dataset_metadata_"+datetime.datetime+".csv", index=None)


if __name__ == "__main__":
    input_dir = "/home/allent/Desktop/repos/oxmedis_utils/data/hand"
    handy_preprocessing(input_dir)._sort()