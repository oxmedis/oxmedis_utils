
import SimpleITK as sitk
import pydicom
from pathlib import Path
import matplotlib.pyplot as plt

class variability():
    def __init__(self, path1, path2, im_path='', points=5) -> None:
        self.path1 = path1
        self.path2 = path2
        self.im_path = im_path
        self.num_points = points

        self.points1, self.points2 = self._load()

    def _load(self):
        '''Opens text file from paths, and outputs ls format of points as integers'''
        f1 = open(self.path1, "r")
        f2 = open(self.path2, "r")
        pt_ls = f1.readlines()
        pt_ls2 = f2.readlines()
        pts = [pt_ls[s].replace('\n','') for s in range(len(pt_ls))]
        pts2 = [pt_ls2[s].replace('\n','') for s in range(len(pt_ls2))]
        
        pts_int = [(int(pts[s].split(',')[0]),int(pts[s].split(',')[1]))for s in range(len(pts))]
        pts2_int = [(int(pts2[s].split(',')[0]),int(pts2[s].split(',')[1]))for s in range(len(pts2))]

        return pts_int, pts2_int
    
    def plot(self, path, save=True):
        im = plt.imread(self.im_path)
        plt.imshow(im)
            
        try:
            for x in range(self.num_points):
                plt.scatter( self.points1[x][1],self.points1[x][0], color='r')
                plt.scatter( self.points2[x][1], self.points2[x][0], color='b')
                
            if save == True:
                plt.savefig(path)
            plt.close()

        except:
            print('check inputs')
        return

    def get_y_distance(self):
        if len(self.points1)>=self.num_points:
            y_ls = []
            for p in range(self.num_points):
                x, y = self.points1[p] 
                x2, y2 = self.points2[p]
                yd = abs(y-y2)
                y_ls.append(yd)
        else:
            y_ls = ['file one has <5 points']
        return y_ls

    def eucledian_dist_points(self):
        if len(self.points1)>=self.num_points:
            ed_ls = []
            for p in range(self.num_points):
                x, y = self.points1[p] 
                x2, y2 = self.points2[p]

                ed = ((x-x2)**2+(y-y2)**2)**0.5
                ed_ls.append(ed)
        else:
            ed_ls = ['file one has <5 points']
        return ed_ls
    
    def manhatten_dist_points(self):
        if len(self.points1)>=self.num_points:
            mand_ls = []
            for p in range(self.num_points):
                x, y = self.points1[p] 
                x2, y2 = self.points2[p]

                mand = abs(x-x2)+abs(y-y2)
                mand_ls.append(mand)
        else:
            mand_ls=['file one has <5 points']
        return mand_ls