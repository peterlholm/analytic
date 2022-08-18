import numpy as np
import cv2
import argparse
import sys
import os
from PIL import Image
# from pyntcloud import PyntCloud
import math
import os.path
from os import path
import shutil

# high_freq = 13.9
 #14
# low_freq = .72

high_freq = 22#14
low_freq = 1.1#.715
rwidth = 160
rheight = 160


# focalLength = 938.0
# centerX = 319.5
# centerY = 239.5
# scalingFactor = 5000

PI = np.pi

def getplys(infolder ):       
    count=len(os.listdir(infolder))-2
    for i in range(count):
        print(count)
        shutil.copyfile(infolder+'/render'+str(i)+'/pointcl-depth.ply', infolder +'/files/plyfolder/points'+str(i)+'.ply')
        # shutil.copyfile(infolder+'/render'+str(i)+'/depth.png', infolder +'files/depthfolder/image'+str(i)+'.png')
        
def getnnplys(infolder ):       
    count=len(os.listdir(infolder))-2
    for i in range(count):
        print(count)
        shutil.copyfile(infolder+'/render'+str(i)+'/pointcl-nndepth.ply', infolder +'files/nnplyfolder/points'+str(i)+'.ply')
        # shutil.copyfile(infolder+'/render'+str(i)+'/depth.png', infolder +'files/depthfolder/image'+str(i)+'.png')        



def unwrap_r(low_f_file, high_f_file, folder):
    filelow = folder + low_f_file
    filehigh = folder +  high_f_file
    wraplow = np.zeros((rheight, rwidth), dtype=np.float64)
    wraphigh = np.zeros((rheight, rwidth), dtype=np.float64)
    unwrapdata = np.zeros((rheight, rwidth), dtype=np.float64)
    im_unwrap = np.zeros((rheight, rwidth), dtype=np.float64)
    wraplow = np.load(filelow)  # To be continued
    wraphigh = np.load(filehigh)
    
    unwrapdata = np.zeros((rheight, rwidth), dtype=np.float64)
    kdata = np.zeros((rheight, rwidth), dtype=np.int64)

    for i in range(rheight):
        for j in range(rwidth):
            kdata[i, j] = round((high_freq/low_freq * (wraplow[i, j])- wraphigh[i, j])/(2*PI))

    unwrapdata = np.add(wraphigh, np.multiply(2*PI,kdata) )
    print('kdata:', np.ptp(np.multiply(1,kdata)))
    print('unwrap:', np.ptp(unwrapdata))
    # print("I'm in unwrap_r")
    print('kdata:', kdata[::40, ::40])
    wr_save = folder + 'unwrap.npy'
    print(wr_save)
    np.save(wr_save, unwrapdata, allow_pickle=False)
    print('unwrange=', np.ptp(unwrapdata), np.max(unwrapdata), np.min(unwrapdata) )
    k_save = folder + 'kdata.npy'
    print(k_save)
    np.save(k_save, kdata, allow_pickle=False)

    maxval = np.amax(unwrapdata)
    print('maxval:', maxval)
    # im_unwrap = 255*unwrapdata/ maxval# np.max(unwrapdata)*255)
    im_unwrap = 2.5*unwrapdata# np.max(unwrapdata)*255)
    # unwrapdata/np.max(unwrapdata)*255
    cv2.imwrite(folder + 'unwrap.png', im_unwrap)
    cv2.imwrite(folder + 'kdata.png', np.multiply(1,kdata))



def makennDDbase(infolder,count):
    print(infolder)
    phibase = np.zeros((rheight, rwidth,count), dtype=np.float64)
    for u in range(rwidth):
        for v in range(rheight):
            print('u=', u, 'v=', v)
            for i in range(count):
                # print('i=',i)
                folder = '/home/samir/Desktop/blender/pycode/bldev2/'+ infolder +'/render'+ str(i)+'/'
                unwrap = np.zeros((rheight, rwidth), dtype=np.float64)
                unwrap = np.load(folder+'nnunwrap.npy')   
                phibase[u,v,i] = unwrap[u,v]
    folder = '/home/samir/Desktop/blender/pycode/bldev2/'+ infolder+'/'
    wr_save = folder + 'nnDDbase.npy'
    np.save(wr_save, phibase, allow_pickle=False)


def makeDDbase(infolder,count):
    print(infolder)
    phibase = np.zeros((rheight, rwidth,count), dtype=np.float64)
    for u in range(rwidth):
        for v in range(rheight):
            print('u=', u, 'v=', v)
            for i in range(count):
                # print('i=',i)
                folder = '/home/samir/Desktop/blender/pycode/bldev2/'+ infolder +'/render'+ str(i)+'/'
                unwrap = np.zeros((rheight, rwidth), dtype=np.float64)
                unwrap = np.load(folder+'unwrap.npy')   
                phibase[u,v,i] = unwrap[u,v]
    folder = '/home/samir/Desktop/blender/pycode/bldev2/'+ infolder+'/'
    wr_save = folder + 'DDbase.npy'
    np.save(wr_save, phibase, allow_pickle=False)





def makeDepth(folder, basecount):
    basefile = '/home/samir/Desktop/blender/pycode/bldev/calplanes/DDbase.npy'
    DBase = np.load(basefile)
    unwrap = np.load(folder+'unwrap.npy' )
    # print('DBase:', np.amax(DBase), np.amin(DBase))
    # print('unwrap:', np.amax(unwrap), np.amin(unwrap))
    depth = np.zeros((rheight, rwidth), dtype=np.float64)
    for i in range(rwidth):
        # print('i:', i)
        for j in range(rheight):
            s=0
            for s in range(basecount-1):
                if (abs(unwrap[i,j]-DBase[i,j,s])<.05): #used -10 to offset scans449 to avoiod saturation
                    break
                else:
                    s+=1

            # print(i,j,unwrap[i,j],DBase[i,j,s])
            depth[i,j]=(s/30*-30 + 40)
            # print('found:',i,j, unwrap[i,j], DBase[i,j,s],s)
    
    # print('depth:', np.amax(depth), np.amin(depth))
    im_depth = depth# np.max(unwrapdata)*255)
    cv2.imwrite(folder + 'depth.png', im_depth)
    



    

def newnnDepth(folder, basecount):
    basefile = '/home/samir/Desktop/blender/pycode/bldev2/calplaneslow/nnDDbase.npy'
    DBase = np.load(basefile)
    unwrap = np.load(folder+'nnunwrap.npy' )
    mask = np.load(folder+'mask.npy' )
    # print('DBase:', np.amax(DBase), np.amin(DBase))
    # print('unwrap:', np.amax(unwrap), np.amin(unwrap))
    depth = np.zeros((rheight, rwidth), dtype=np.float64)
    zee=0
    for i in range(rwidth): #adressing edge noise, can not be explained yet!!!!
        # print('i:', i)
        for j in range(rheight):
            if not(mask[i,j]):

                s=0
                for s in range(0, basecount-1,1):
                    if (unwrap[i,j]< DBase[i,j,s]):
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
                depth[i,j]= (zee/basecount*-30 + 40)*1

    # print('depth:', np.amax(depth), np.amin(depth))
    print('nndepthrange=', np.ptp(depth), np.max(depth), np.min(depth) )

    im_depth = depth# np.max(unwrapdata)*255)
    cv2.imwrite(folder + 'nndepth.png', im_depth)
    np.save(folder+'nndepth.npy' ,im_depth , allow_pickle=False)



def newDepth(folder, basecount):
    basefile = '/home/samir/Desktop/blender/pycode/bldev2/calplaneslow/DDbase.npy'
    DBase = np.load(basefile)
    unwrap = np.load(folder+'unwrap.npy' )
    mask = np.load(folder+'mask.npy' )
    # print('DBase:', np.amax(DBase), np.amin(DBase))
    # print('unwrap:', np.amax(unwrap), np.amin(unwrap))
    depth = np.zeros((rheight, rwidth), dtype=np.float64)
    zee=0
    for i in range(rwidth): #adressing edge noise, can not be explained yet!!!!
        # print('i:', i)
        for j in range(rheight):
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
                depth[i,j]= (zee/basecount*-30 + 40)*1

    # print('depth:', np.amax(depth), np.amin(depth))
    print('nndepthrange=', np.ptp(depth), np.max(depth), np.min(depth) )

    im_depth = depth# np.max(unwrapdata)*255)
    cv2.imwrite(folder + 'depth.png', im_depth)
    np.save(folder+'depth.npy' ,im_depth , allow_pickle=False)


def newwandDepth(folder, basecount):
    basefile = '/home/samir/Desktop/blender/pycode/bldev2/scans/30wand/cal50lf/DDbase.npy'
    DBase = np.load(basefile)
    unwrap = np.load(folder+'unwrap.npy' )
    mask = np.load(folder+'mask.npy' )
    # print('DBase:', np.amax(DBase), np.amin(DBase))
    # print('unwrap:', np.amax(unwrap), np.amin(unwrap))
    depth = np.zeros((rheight, rwidth), dtype=np.float64)
    zee=0
    for i in range(rwidth): #adressing edge noise, can not be explained yet!!!!
        # print('i:', i)
        for j in range(rheight):
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
    cv2.imwrite(folder + 'depth.png', im_depth)
    np.save(folder+'depth.npy' ,im_depth , allow_pickle=False)


# def newWandDepth(folder, basecount):
#     basefile = '/home/samir/Desktop/cal/DDbase.npy'
#     DBase = np.load(basefile)
#     unwrap = np.load(folder+'unwrap.npy' )
#     mask = np.load(folder+'mask.npy' )
#     # print('DBase:', np.amax(DBase), np.amin(DBase))
#     # print('unwrap:', np.amax(unwrap), np.amin(unwrap))
#     depth = np.zeros((rheight, rwidth), dtype=np.float64)
#     zee=0
#     for i in range(rwidth): #adressing edge noise, can not be explained yet!!!!
#         # print('i:', i)
#         for j in range(rheight):
#             if not(mask[i,j]):

#                 s=0
#                 for s in range(0, basecount-1,1):
#                     if (unwrap[i,j]< DBase[i,j,s]):
#                         ds = (unwrap[i,j] - DBase[i,j,s])/( DBase[i,j,s]- DBase[i,j,s-1])
#                         zee = s+ds*1
#                         break
#                     else:
#                         s+=1
#                         if s==basecount:
#                             print('not found!')

#                 # print(i,j,unwrap[i,j],DBase[i,j,s])
#                 if zee == 0:
#                     print('not found')
#                 depth[i,j]= (zee/basecount*-30 + 40)*1

#     # print('depth:', np.amax(depth), np.amin(depth))
#     print('nndepthrange=', np.ptp(depth), np.max(depth), np.min(depth) )

#     im_depth = depth# np.max(unwrapdata)*255)
#     cv2.imwrite(folder + 'depth.png', im_depth)
#     np.save(folder+'depth.npy' ,im_depth , allow_pickle=False)




def newDepthFast(folder, basecount):
    basefile = '/home/samir/Desktop/blender/pycode/scanplanes/DDbase.npy'
    DBase = np.load(basefile)
    unwrap = np.load(folder+'unwrap.npy' )
    # print('DBase:', np.amax(DBase), np.amin(DBase))
    # print('unwrap:', np.amax(unwrap), np.amin(unwrap))
    depth = np.zeros((rheight, rwidth), dtype=np.float64)
    for i in range(rwidth):
        # print('i:', i)
        for j in range(rheight):
            s=0
            for s in range(0, basecount-1,1):
                if (unwrap[i,j]< DBase[i,j,s]):
                    ds = (unwrap[i,j] - DBase[i,j,s])/( DBase[i,j,s]- DBase[i,j,s-1])
                    s = s+ds*1
                    break
                else:
                    s+=1

            # print(i,j,unwrap[i,j],DBase[i,j,s])
            depth[i,j]=s
            # print('found:',i,j, unwrap[i,j], DBase[i,j,s],s)
    
    # print('depth:', np.amax(depth), np.amin(depth))
    im_depth = depth# np.max(unwrapdata)*255)
    cv2.imwrite(folder + 'depth.png', im_depth)


def wanddepth(myfolder,start, count, basecount):
    for i in range(start, start+count):
        print('new_progress:', str(i))
        folder = myfolder+'/render'+ str(i)+'/'
        newwandDepth(folder, basecount)
        # makeDepth(folder, basecount)


def depth(myfolder,start, count, basecount):
    for i in range(start, count):
        print('new_progress:', str(i))
        folder = myfolder+'/render'+ str(i)+'/'
        newDepth(folder, basecount)
        # makeDepth(folder, basecount)

def nndepth(myfolder,start, count, basecount):
    for i in range(start, count):
        print('new_progress:', str(i))
        folder = myfolder+'/render'+ str(i)+'/'
        newnnDepth(folder, basecount)
        # makeDepth(folder, basecount)



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


def unw(myfolder,start, count):
    for i in range(start, count):
        print('start')

        folder = myfolder+'/render'+ str(i)+'/'
        print(folder)
        # if path.exists(folder):
        unwrap_r('scan_wrap2.npy', 'scan_wrap1.npy', folder )
            # deduct_ref('scan_wrap2.npy', 'scan_wrap2.npy', folder, ref_folder)
            # threedpoints = make3dpoints(folder+'unwrap.npy', folder, ref_folder+'/unwrap.npy')
            # cv2.imwrite(folder + 'unwrap2.png', threedpoints)
            # generate_json_pointcloud(folder + 'blenderimage2.png', folder + 'unwrap.png', folder +'pointcl.json')
            # generate_pointcloud(folder + 'blendertexture.png', folder + '5mask.png' , folder + 'im_wrap1.png', folder +'pointcl-high.ply')
            # generate_pointcloud(folder + 'blendertexture.png', folder + '5mask.png' , folder + 'im_wrap2.png', folder +'pointcl-low.ply')
            # generate_pointcloud(folder + 'blendertexture.png', folder + '5mask.png', folder + 'unwrap.png', folder +'pointcl-unw.ply')
            # generate_pointcloud(folder + 'blendertexture.png', folder + '5mask.png', folder + 'depth.png', folder +'pointcl-depth.ply')
            # generate_pointcloud(folder + 'blendertexture.png', folder + '5mask.png', folder + 'kdata.png', folder +'pointcl-k.ply')
            # generate_pointcloud(folder + 'blendertexture.png', folder + '5mask.png', folder + 'unwrap2.png', folder +'pointcl-2.ply')


def makeclouds(myfolder,start, count):
     for i in range(start, start+count):
        print('start')
        folder = myfolder+'/render'+ str(i)+'/'
        print(folder)
        if path.exists(folder):
            print('i=', i)

            generate_pointcloud(folder + 'image8.png', folder + 'mask.png', folder + 'depth.npy', folder +'pointcl-depth.ply')


def makennclouds(myfolder,start, count):
     for i in range(start, count):
        print('start')
        folder = myfolder+'/render'+ str(i)+'/'
        print(folder)
        if path.exists(folder):
            print('i=', i)

            generate_pointcloud(folder + 'image8.png', folder + 'mask.png', folder + 'nndepth.npy', folder +'pointcl-nndepth.ply')


def mydepth():
    folder = '/home/samir/Desktop/blender/pycode/bldev2/'
    start = 0
    # unw(folder+'calplanesL100/', start,30)
    # makeDDbase(200)
    # Run multiphasewrap on the sim output prior to unwrapping
    makeDDbase('scans/30wand/cal25', 25)
# mydepth()



def mynndepth():
    folder = '/home/samir/Desktop/cal/peter/'
    start = 0
    # unw(folder, start,6)
    # makeDDbase(200)
    # Run multiphasewrap on the sim output prior to unwrapping
    makennDDbase('calplanes6', 6)
# mynnepth()


def myrun():
    folder = '/home/samir/Desktop/blender/pycode/bldev2/scans/30wand/lf'
    # folder = '/home/samir/Desktop/blender/pycode/bldev2/calplanesL100/'
    count= len(os.listdir(folder))-1
    # count=50
    # print(count)
    start = 0
    unw(folder,start, start+count)
    wanddepth(folder,start, count, 50)
    makeclouds(folder,start, count)
    
    # getplys(folder)

myrun()

def scaleunwrap():
    folder = '/home/samir/Desktop/blender/pycode/bldev2/scans/batchscans/'
    count= len(os.listdir(folder))
    for i in range(count):
        unwrap = np.load(folder+'render'+ str(i)+ '/unwrap.npy' )
        im_unwrap = 2.5*unwrap
        cv2.imwrite(folder +'render'+ str(i)+  '/unwrap.png', im_unwrap)

# scaleunwrap()

def offset():
    folderin = '/home/samir/Desktop/b1scans/'
    folderout = '/home/samir/Desktop/b1scans/'
    offset = 9000
    for i in range(4000):
        os.rename(folderin+'render'+str(i+offset),folderout+'render'+str(i))

# offset()

########################################################################################################################################
########################################################################################################################################

def unw_debug(low_f_file, high_f_file, folder, start, stop, step):
    print('debug!', start, stop, step)
    filelow = folder + low_f_file
    filehigh = folder +  high_f_file
    wraplow = np.zeros((rheight, rwidth), dtype=np.float64)
    wraphigh = np.zeros((rheight, rwidth), dtype=np.float64)
    unwrapdata = np.zeros((rheight, rwidth), dtype=np.float64)
    im_unwrap = np.zeros((rheight, rwidth), dtype=np.float64)
    wraplow = np.load(filelow)  # To be continued
    wraphigh = np.load(filehigh)
    print('highrange=', np.ptp(wraphigh), np.max(wraphigh), np.min(wraphigh) )
    print('lowrange=', np.ptp(wraplow), np.max(wraplow), np.min(wraplow) )
    # print('high:', wraphigh)
    # print('low:', wraplow)
    
    unwrapdata = np.zeros((rheight, rwidth), dtype=np.float64)
    kdata = np.zeros((rheight, rwidth), dtype=np.int64)
    # wrap1data = cv2.GaussianBlur(wrap1data, (0, 0), 3, 3)
    # wrap2data = cv2.GaussianBlur(wrap2data, (0, 0), 4, 4)
    for i in range(rheight):
        for j in range(rwidth):
            kdata[i, j] = round((high_freq/low_freq * (wraplow[i, j])- wraphigh[i, j])/(2*PI))
            # unwrapdata[i,j] = .1*(1.1*wraphigh[i, j]/np.max(wraphigh) +2*PI* kdata[i, j]/np.max(wraphigh))
            # unwrapdata[i,j] = 1*(1*wraphigh[i, j] +2*PI* kdata[i, j])
            if i== 150:       
                print('i =', i,
                'low:',(wraplow[i, j]),
                'high:',wraphigh[i, j],
                'round:',round((high_freq/low_freq * (wraplow[i, j])- wraphigh[i, j])/(2*PI))
                )
    unwrapdata = np.add(wraphigh, np.multiply(2*PI,kdata) )
    print('kdata:', np.ptp(np.multiply(1,kdata)))
    print('unwrap:', np.ptp(unwrapdata))
    # print("I'm in unwrap_r")
    print('kdata:', kdata[::40, ::40])
    wr_save = folder + 'unwrap.npy'
    print(wr_save)
    # np.save(wr_save, unwrapdata, allow_pickle=False)
    print('unwrange=', np.ptp(unwrapdata), np.max(unwrapdata), np.min(unwrapdata) )
    k_save = folder + 'kdata.npy'
    print(k_save)
    # np.save(k_save, kdata, allow_pickle=False)
    # print(wr_save)
    # np.save('wrap24.pickle', wrap24data, allow_pickle=True)
    # unwrapdata = np.multiply(unwrapdata, 1.0)
    # unwrapdata = np.unwrap(np.transpose(unwrapdata))
    # unwrapdata = cv2.GaussianBlur(unwrapdata,(0,0),3,3)
    # unwrapdata = np.multiply(unwrapdata, 1.0)
    maxval = np.amax(unwrapdata)
    print('maxval:', maxval)
    # im_unwrap = 255*unwrapdata/ maxval# np.max(unwrapdata)*255)
    im_unwrap = 3.0*unwrapdata# np.max(unwrapdata)*255)
    # unwrapdata/np.max(unwrapdata)*255
    # cv2.imwrite(folder + 'unwrap.png', im_unwrap)
    # cv2.imwrite(folder + 'kdata.png', np.multiply(2*PI,kdata))




def debug():
    folder = '/home/samir/Desktop/blender/pycode/400newplanes/render250/'
    unw_debug('scan_wrap2.npy', 'scan_wrap1.npy', folder, 140, 160, 2 )

# debug()

# folder = '/home/samir/db3/scan/static/scan_folder/scan_im_folder/'
# unwrap_r('scan_wrap2.npy', 'scan_wrap1.npy', folder )














#########################################################################################################################

def deduct_ref(unwrap, reference, folder1, folder2):
    file1 = folder1 + '/' + unwrap
    file2 = folder2 + '/' + reference
    maskfile = folder1 + '/'+ 'scan_wrap1_process.npy' 
    wrap_data = np.load(file1)  # To be continuedref_folder = '/home/samir/db3/scan/static/scan_folder/scan_ref_folder'

    ref_data = np.load(file2)
    mask_data = np.load(maskfile)
    ref_data = np.multiply(ref_data, mask_data)
    net_data = np.subtract(wrap_data, ref_data)
    print('abs_unwrap:', np.amax(net_data), np.amin(net_data))
    # print('reference:', ref_data)
    # print('wrap:',wrap_data)
    # print('abs:',net_data)
    net_save = folder1 + 'abs_unwrap.npy'
    np.save(net_save, net_data, allow_pickle=False)
    print(net_save)
    # np.save('wrap24.pickle', wrap24data, allow_pickle=True)
    # net_data = np.multiply(net_data, 1.0)
    cv2.imwrite(folder1 + 'abs_unwrap.png', 40*net_data)




# def unwrap(request):
#     # folder = ScanFolder.objects.last().folderName
#     folder = '/home/samir/db2/scan/static/scan_folder/scan_im_folder/'
#     ref_folder = '/home/samir/db2/scan/static/scan_folder/scan_ref_folder'
#     three_folder = '/home/samir/db2/3D/static/3scan_folder'
#     unwrap_r('scan_wrap2.npy', 'scan_wrap1.npy', folder )
#     deduct_ref('unwrap.npy', 'unwrap.npy', folder, ref_folder)
#     # generate_color_pointcloud(folder + 'image1.png', folder + '/abs_unwrap.png', folder + '/pointcl.ply')
#     generate_json_pointcloud(folder + 'image1.png', folder +
#                              '/abs_unwrap.png', three_folder + '/pointcl.json')
#     return render(request, 'scantemplate.html')


# def abs_unwrap_r(low_f, high_f, output_file,  folder):
#     filelow = folder + '/' + low_f
#     filehigh = folder + '/' + high_f
#     wraplow = np.load(filelow)  # To be continued
#     wraphigh = np.load(filehigh)
#     unwrapdata = np.zeros((rheight, rwidth), dtype=np.float)
#     kdata = np.zeros((rheight, rwidth), dtype=np.float)
#     # wrap1data = cv2.GaussianBlur(wrap1data, (0, 0), 3, 3)
#     # wrap2data = cv2.GaussianBlur(wrap2data, (0, 0), 4, 4)
#     for i in range(rheight):
#         for j in range(rwidth):
#             kdata[i, j] = round(
#                 (high_freq/low_f * wraplow[i, j] - 1.0 * wraphigh[i, j])/(2.0*np.pi))
#             unwrapdata[i, j] = 1.0 * wraplow[i, j] + 1.0*kdata[i, j]*np.pi

#     print(kdata[::20, ::20])
#     wr_save = folder + 'unwrap.npy'
#     np.save(wr_save, unwrapdata, allow_pickle=False)
#     print(wr_save)
#     # np.save('wrap24.pickle', wrap24data, allow_pickle=True)
#     unwrapdata = np.multiply(unwrapdata, 1.0)
#     # unwrapdata = np.unwrap(np.transpose(unwrapdata))
#     unwrapdata = cv2.GaussianBlur(unwrapdata,(0,0),3,3)
#     cv2.imwrite(folder + output_file, unwrapdata)