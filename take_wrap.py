"takewrap calulate wrap images"
import math
import numpy as np
import cv2


_RWIDTH = 160
_RHEIGHT = 160

def take_wrap4(folder, numpy_file, png_file, preamble, offset):
    "folder is input folder with 10 images"
    if not folder.exists:
        raise FileNotFoundError("folder")
    N=4
    mask = np.zeros((_RHEIGHT, _RWIDTH), dtype=np.bool)
    #process = np.zeros((_RHEIGHT, _RWIDTH), dtype=np.bool)
    #c_range = np.zeros((_RHEIGHT, _RWIDTH), dtype=np.float)
    nom = np.zeros((_RHEIGHT, _RWIDTH), dtype=np.float)
    denom = np.zeros((_RHEIGHT, _RWIDTH), dtype=np.float)

    #noise_threshold = 0.1

    image_cnt = 4  # Number of images to be taken
    im0 = np.zeros((_RWIDTH, _RHEIGHT), dtype=np.float)
    im1 = np.zeros((_RWIDTH, _RHEIGHT), dtype=np.float)
    im2 = np.zeros((_RWIDTH, _RHEIGHT), dtype=np.float)
    im3 = np.zeros((_RWIDTH, _RHEIGHT), dtype=np.float)

    im_arr = [im0, im1, im2, im3]
    for i in range(image_cnt):
        my_file = str(folder) + '/' + preamble + str(offset+i+1) + ".png"
        # print(my_file)
        image = cv2.imread(my_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im_arr[i] = gray
        im_arr[i]= im_arr[i]*math.sin(2*np.pi*i/N)
    nom = sum(im_arr)

    image_cnt = 4  # Number of images to be taken
    im0 = np.zeros((_RWIDTH, _RHEIGHT), dtype=np.float)
    im1 = np.zeros((_RWIDTH, _RHEIGHT), dtype=np.float)
    im2 = np.zeros((_RWIDTH, _RHEIGHT), dtype=np.float)
    im3 = np.zeros((_RWIDTH, _RHEIGHT), dtype=np.float)

    im_arr = [im0, im1, im2, im3]
    for i in range(image_cnt):
        my_file = str(folder) + "/" + preamble + str(offset+i+1) + ".png"
        # print(my_file)
        image = cv2.imread(my_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im_arr[i] = gray
        im_arr[i]= im_arr[i]*math.cos(2*np.pi*i/N)
    denom = sum(im_arr)

    wrap = np.zeros((_RHEIGHT, _RWIDTH), dtype=np.float)
    im_wrap = np.zeros((_RHEIGHT, _RWIDTH), dtype=np.float)
    for i in range(_RHEIGHT):
        for j in range(_RWIDTH):
            wrap[i, j] = np.arctan2(nom[i,j],denom[i,j])
            if wrap[i, j] < 0:
                wrap[i, j] += 2*np.pi
            im_wrap[i, j] = 128/np.pi * wrap[i, j]

    file_path = str(folder) + '/' + numpy_file
    np.save(file_path, wrap, allow_pickle=False)
    file_path = str(folder) + '/' + numpy_file[:-4] + '_mask.npy'
    np.save(file_path, mask, allow_pickle=False)
    png_file = str(folder) + '/' + png_file
    cv2.imwrite(png_file, im_wrap)
    mask_file = str(folder) + '/' + str(offset) + 'mask.png'
    cv2.imwrite(mask_file, mask*128)
 