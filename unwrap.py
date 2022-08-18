"Analytic unwrap module"
from pathlib import Path
import os
from os import path
import numpy as np
import cv2
from PIL import Image
from ana_const import RHEIGHT, RWIDTH, HIGH_FREQ, LOW_FREQ, DB_HEIGHT

PI = np.pi

def unwrap_r(low_f_file, high_f_file, folder):
    "Unwrap...."
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
    print('kdata:', np.ptp(np.multiply(1,kdata)))
    print('unwrap:', np.ptp(unwrapdata))
    # print("I'm in unwrap_r")
    print('kdata:', kdata[::40, ::40])
    wr_save = folder / 'unwrap.npy'
    print(wr_save)
    np.save(wr_save, unwrapdata, allow_pickle=False)
    print('unwrange=', np.ptp(unwrapdata), np.max(unwrapdata), np.min(unwrapdata) )
    k_save = folder / 'kdata.npy'
    print(k_save)
    np.save(k_save, kdata, allow_pickle=False)

    maxval = np.amax(unwrapdata)
    print('maxval:', maxval)
    # im_unwrap = 255*unwrapdata/ maxval# np.max(unwrapdata)*255)
    im_unwrap = 2.5*unwrapdata# np.max(unwrapdata)*255)
    # unwrapdata/np.max(unwrapdata)*255
    cv2.imwrite(str(folder / 'unwrap.png'), im_unwrap)
    cv2.imwrite(str(folder / 'kdata.png'), np.multiply(1,kdata))

def unw(myfolder, start, count):
    "Unwrap folder"
    for i in range(start, count):
        print('start')

        folder = myfolder / ('render'+ str(i))
        print(folder)
        # if path.exists(folder):
        unwrap_r('scan_wrap2.npy', 'scan_wrap1.npy', folder )

def unwrap_picture(folder):
        unwrap_r('scan_wrap2.npy', 'scan_wrap1.npy', folder )


def newwandDepth(folder, basecount):
    "calculate depth"
    basefile = DB_HEIGHT
    #basefile = '/home/samir/Desktop/blender/pycode/bldev2/scans/30wand/cal50lf/DDbase.npy'
    DBase = np.load(basefile)
    print("DBase shape", DBase.shape)
    unwrap = np.load(folder / 'unwrap.npy' )
    mask = np.load(folder / 'mask.npy' )
    # print('DBase:', np.amax(DBase), np.amin(DBase))
    # print('unwrap:', np.amax(unwrap), np.amin(unwrap))
    depth = np.zeros((RHEIGHT, RWIDTH), dtype=np.float64)
    zee=0
    for i in range(RWIDTH): #adressing edge noise, can not be explained yet!!!!
        # print('i:', i)
        for j in range(RHEIGHT):
            if not(mask[i,j]):

                s=0
                for s in range(0, basecount-1,1):
                    if (unwrap[i,j]> DBase[i,j,s]):
                        ds = (unwrap[i,j] - DBase[i,j,s])/( DBase[i,j,s]- DBase[i,j,s-1])
                        zee = s+ds*1
                        break
                    else:
                        s+=1
                        if s==basecount:
                            print('not found!')

                # print(i,j,unwrap[i,j],DBase[i,j,s])
                if zee == 0:
                    print('not found')
                depth[i,j]= (zee/basecount*-20 + 35)*1

    # print('depth:', np.amax(depth), np.amin(depth))
    print('nndepthrange=', np.ptp(depth), np.max(depth), np.min(depth) )

    im_depth = depth# np.max(unwrapdata)*255)
    cv2.imwrite(str(folder / 'depth.png'), im_depth)
    np.save(folder / 'depth.npy' ,im_depth , allow_pickle=False)




def generate_pointcloud(rgb_file, mask_file,depth_file,ply_file):
    print(ply_file)
    """
    Generate a colored point cloud in PLY format from a color and a depth image.

    Input:
    rgb_file -- filename of color image
    depth_file -- filename of depth image
    ply_file -- filename of ply file

    """
    rgb = Image.open(rgb_file)
    # depth = Image.open(depth_file)
    # depth = Image.open(depth_file).convert('I')
    depth = np.load(depth_file )
    mask = Image.open(mask_file).convert('I')

    # if rgb.size != depth.size:
    #     raise Exception("Color and depth image do not have  same resolution.")
    # if rgb.mode != "RGB":
    #     raise Exception("Color image is not in RGB format")
    # if depth.mode != "I":
    #     raise Exception("Depth image is not in intensity format")


    points = []
    for v in range(rgb.size[1]):
        for u in range(rgb.size[0]):
            color =   rgb.getpixel((v,u))
            # Z = depth.getpixel((u,v)) / scalingFactor
            # if Z==0: continue
            # X = (u - centerX) * Z / focalLength
            # Y = (v - centerY) * Z / focalLength
            if (mask.getpixel((v,u))<25):
                # Z = depth.getpixel((u, v))
                Z = depth[u,v]
                if Z < 0:
                    Z = 0
                else:
                    if Z> 80:
                        Z = 80
                if Z == 0: continue
                Y = .306 * (v-80) *  Z/80 #.306 = tan(FOV/2) = tan(34/2)
                X = .306 * (u-80) *  Z/80
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


def wanddepth(myfolder,start, count, basecount):
    for i in range(start, start+count):
        print('new_progress:', str(i))
        folder = myfolder+'/render'+ str(i)+'/'
        newwandDepth(folder, basecount)
        # makeDepth(folder, basecount)

def makeclouds(myfolder,start, count):
    for i in range(start, start+count):
        print('start')
        folder = myfolder+'/render'+ str(i)+'/'
        print(folder)
        if path.exists(folder):
            print('i=', i)

            generate_pointcloud(folder + 'image8.png', folder + 'mask.png', folder + 'depth.npy', folder +'pointcl-depth.ply')



def myrun():
    #folder = '/home/samir/Desktop/blender/pycode/bldev2/scans/30wand/lf'
    folder = Path(__file__).parent / 'tmp'
    # folder = '/home/samir/Desktop/blender/pycode/bldev2/calplanesL100/'
    count= len(os.listdir(folder))-1
    # count=50
    # print(count)
    start = 0
    unw(folder,start, start+count)
    wanddepth(folder,start, count, 50)
    makeclouds(folder,start, count)

    # getplys(folder)

#myrun()

folder = Path(__file__).parent / 'tmp'

unwrap_picture(folder)
newwandDepth(folder, 30)    # todo change to 50
           
generate_pointcloud(folder / 'image8.png', folder / 'mask.png', folder / 'depth.npy', folder / 'pointcl-depth.ply')
