"Analytic unwrap module"
from pathlib import Path
#import os
from os import path
import numpy as np
import cv2
from PIL import Image
from ana_const import RHEIGHT, RWIDTH, HIGH_FREQ, LOW_FREQ, DB_HEIGHT

_DEBUG = False

PI = np.pi

def unwrap_r(low_f_file, high_f_file, folder):
    "Unwrap low_file.npy, high_file.npy  result folder"
    filelow = folder / low_f_file
    filehigh = folder /  high_f_file
    wraplow = np.zeros((RHEIGHT, RWIDTH), dtype=np.float64)
    wraphigh = np.zeros((RHEIGHT, RWIDTH), dtype=np.float64)
    unwrapdata = np.zeros((RHEIGHT, RWIDTH), dtype=np.float64)
    im_unwrap = np.zeros((RHEIGHT, RWIDTH), dtype=np.float64)
    wraplow = np.load(filelow)  # To be continued
    wraphigh = np.load(filehigh)

    unwrapdata = np.zeros((RHEIGHT, RWIDTH), dtype=np.float64)
    kdata = np.zeros((RHEIGHT, RWIDTH), dtype=np.int64)

    for i in range(RHEIGHT):
        for j in range(RWIDTH):
            kdata[i, j] = round((HIGH_FREQ/LOW_FREQ * (wraplow[i, j])- wraphigh[i, j])/(2*PI))

    unwrapdata = np.add(wraphigh, np.multiply(2*PI,kdata) )
    if _DEBUG:
        print('kdata:', np.ptp(np.multiply(1,kdata)))
        print('unwrap:', np.ptp(unwrapdata))
        print('kdata:', kdata[::40, ::40])
    wr_save = folder / 'unwrap.npy'
    np.save(wr_save, unwrapdata, allow_pickle=False)
    if _DEBUG:
        print('unwrange=', np.ptp(unwrapdata), np.max(unwrapdata), np.min(unwrapdata) )
    k_save = folder / 'kdata.npy'
    np.save(k_save, kdata, allow_pickle=False)
    maxval = np.amax(unwrapdata)
    if _DEBUG:
        print('maxval:', maxval)
    im_unwrap = 2.5*unwrapdata# np.max(unwrapdata)*255)
    if _DEBUG:
        cv2.imwrite(str(folder / 'unwrap.png'), im_unwrap)
        cv2.imwrite(str(folder / 'kdata.png'), np.multiply(1,kdata))

def unwrap_picture(folder):
    "unwrap a single file"
    unwrap_r('scan_wrap2.npy', 'scan_wrap1.npy', folder )


def newwand_depth(folder, basecount):
    "calculate depth"
    basefile = DB_HEIGHT
    height_db = np.load(basefile)
    if _DEBUG:
        print("height_db shape", height_db.shape)
    unwrap = np.load(folder / 'unwrap.npy' )
    mask = np.load(folder / 'mask.npy' )
    # print('height_db:', np.amax(height_db), np.amin(height_db))
    # print('unwrap:', np.amax(unwrap), np.amin(unwrap))
    depth = np.zeros((RHEIGHT, RWIDTH), dtype=np.float64)
    zee=0
    for i in range(RWIDTH): #adressing edge noise, can not be explained yet!!!!
        # print('i:', i)
        for j in range(RHEIGHT):
            if not(mask[i,j]):

                s=0
                for s in range(0, basecount-1,1):
                    if (unwrap[i,j]> height_db[i,j,s]):
                        ds = (unwrap[i,j] - height_db[i,j,s])/( height_db[i,j,s]- height_db[i,j,s-1])
                        zee = s+ds*1
                        break
                    else:
                        s+=1
                        if s==basecount:
                            print('not found!')
                # print(i,j,unwrap[i,j],height_db[i,j,s])
                if zee == 0:
                    print('not found')
                depth[i,j]= (zee/basecount*-20 + 35)*1
    # print('depth:', np.amax(depth), np.amin(depth))
    if _DEBUG:
        print('nndepthrange=', np.ptp(depth), np.max(depth), np.min(depth) )
    im_depth = depth# np.max(unwrapdata)*255)
    cv2.imwrite(str(folder / 'depth.png'), im_depth)
    np.save(folder / 'depth.npy' ,im_depth , allow_pickle=False)

def generate_pointcloud(rgb_file, mask_file,depth_file,ply_file):
    """
    Generate a colored point cloud in PLY format from a color and a depth image.

    Input:
    rgb_file -- filename of color image
    depth_file -- filename of depth image
    ply_file -- filename of ply file

    """
    if _DEBUG:
        print(ply_file)
    rgb = Image.open(rgb_file)
    depth = np.load(depth_file )
    mask = Image.open(mask_file).convert('I')
    points = []
    for v in range(rgb.size[1]):
        for u in range(rgb.size[0]):
            color =   rgb.getpixel((v,u))
            # Z = depth.getpixel((u,v)) / scalingFactor
            # if Z==0: continue
            # X = (u - centerX) * Z / focalLength
            # Y = (v - centerY) * Z / focalLength
            if mask.getpixel((v,u))<25:
                # Z = depth.getpixel((u, v))
                Z = depth[u,v]
                if Z < 0:
                    Z = 0
                else:
                    if Z> 80:
                        Z = 80
                if Z == 0:
                    continue
                Y = .306 * (v-80) *  Z/80 #.306 = tan(FOV/2) = tan(34/2)
                X = .306 * (u-80) *  Z/80
                if _DEBUG:
                    if (u==80 and v ==80):
                        print('80:z=', Z, X, Y)
                    else:
                        if (u==102 and v ==82):
                            print('82:z=', Z, X, Y)
                points.append("%f %f %f %d %d %d 0\n"%(X,Y,Z,color[0],color[1],color[2]))
    file = open(ply_file,"w")
    file.write('''ply
format ascii 1.0
element vertex %d
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
property uchar alpha
end_header
%s
'''%(len(points),"".join(points)))
    file.close()

def unwrapping(folder):
    "run through unwrapping process"
    unwrap_picture(folder)
    newwand_depth(folder, 50)
    generate_pointcloud(folder / 'image8.png', folder / 'mask.png', folder / 'depth.npy', folder / 'pointcl-depth.ply')

if __name__=='__main__':
    myfolder = Path(__file__).parent / 'tmp'
    unwrapping(myfolder)
 