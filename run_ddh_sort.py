
from oxmedis_utils.preprocessing import data_reader
from pathlib import Path
import shutil
from glob import glob
import os
import pandas as pd
import cv2

class ddh_preprocessing():
    def __init__(self, input_dir, output_dir=None) -> None:
        self.input_dir = Path(input_dir)
        self.output_dir = self.input_dir.parent.joinpath(Path(self.input_dir.name+'_organized'))

        self.labeled_dir = 'labeled'
        self.unlabeled_dir = 'unlabeled'
        self.other = 'other'

        #what tag to check if its unlabeled and sort by
        self.tag = 'BurnedInAnnotation'
        self.tag_unlabeled = 'NO'

        #file naming
        self.name_ls=['AccessionNumber','SOPInstanceUID']
        #check if contains L/R, added at the end of name
        self.name_ls_lr='TransducerData'

        self.other_tag = 'SeriesDescription'

        self.img_type ='.png'
        
        return       
    
    def add_LR(self,new_name, dcm_meta):
        tag_val_l= dcm_meta[self.name_ls_lr].find('L')
        tag_val_r= dcm_meta[self.name_ls_lr].find('R')
        if tag_val_l != -1:
            new_name = new_name+'_L'
        elif tag_val_r != -1:
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
                    patient_scan_name = patient_scan.name
                    
                    dcm_meta, img = data_reader.data_reader(str(patient_scan)).read_DcmMetadata()

                    if dcm_meta[self.other_tag]=='Carestream PACS Reports':
                        #remove pacs reports into sepearate folder
                        tag_value = self.other
                    else:
                        tag_value = dcm_meta[self.tag]

                    new_name = ''

                    count = 0
                    for tag in self.name_ls:
                        if count == 0:
                            new_name = dcm_meta[tag]
                        else:
                            if tag == 'SOPInstanceUID':
                                print(dcm_meta[tag].split(".")[8])
                                new_name = new_name+'_'+dcm_meta[tag].split(".")[8]
                            else:   
                                new_name = new_name+'_'+dcm_meta[tag]
                        count = count+1

                    #check/add if LR
                    if tag_value==self.other:
                        pass
                    else:
                        new_name = self.add_LR(new_name, dcm_meta)
                    
                    #save folder new location
                    if tag_value==self.tag_unlabeled:
                        dest = self.output_dir.joinpath(self.unlabeled_dir).joinpath(patient_path.name,new_name+self.img_type)
                    elif tag_value ==self.other:
                        dest = self.output_dir.joinpath(self.other).joinpath(patient_path.name,new_name+self.img_type)
                    else:
                        dest = self.output_dir.joinpath(self.labeled_dir).joinpath(patient_path.name,new_name+self.img_type)

                    if not dest.is_dir():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        img_arr = img.pixel_array
                        cv2.imwrite(str(dest),img_arr)

   
                    all_tags.append(dcm_meta)
            
        df = pd.DataFrame(all_tags)
        if save_dcmMeta_csv == True:
            df.to_csv(f"{self.output_dir}/img_meta_data.csv", index=None)


if __name__ == "__main__":
    input_dir = "/home/allent/Desktop/repos/oxmedis_utils/data/coml0067"

    ddh_preprocessing(input_dir)._sort()
