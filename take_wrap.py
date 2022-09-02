"takewrap calulate wrap images"
import math
import numpy as np
import cv2
from ana_const import RHEIGHT, RWIDTH

_DEBUG_OUT = False

def take_wrap4(folder, numpy_file, png_file, preamble, offset):
    "folder is input folder with 10 images, numpy_file is output, png_file is output, preamble is input filename, offset is startnumber-1"
    if not folder.exists:
        raise FileNotFoundError("folder")
    n_konstant=4    # what is this
    mask = np.zeros((RHEIGHT, RWIDTH), dtype=np.bool)
    #process = np.zeros((_RHEIGHT, _RWIDTH), dtype=np.bool)
    #c_range = np.zeros((_RHEIGHT, _RWIDTH), dtype=np.float)
    nom = np.zeros((RHEIGHT, RWIDTH), dtype=np.float)
    denom = np.zeros((RHEIGHT, RWIDTH), dtype=np.float)

    #noise_threshold = 0.1

    image_cnt = 4  # Number of images to be taken
    im0 = np.zeros((RWIDTH, RHEIGHT), dtype=np.float)
    im1 = np.zeros((RWIDTH, RHEIGHT), dtype=np.float)
    im2 = np.zeros((RWIDTH, RHEIGHT), dtype=np.float)
    im3 = np.zeros((RWIDTH, RHEIGHT), dtype=np.float)

    im_arr = [im0, im1, im2, im3]
    for i in range(image_cnt):
        my_file = str(folder) + '/' + preamble + str(offset+i+1) + ".png"
        # print(my_file)
        image = cv2.imread(my_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im_arr[i] = gray
        im_arr[i]= im_arr[i]*math.sin(2*np.pi*i/n_konstant)
    nom = sum(im_arr)

    image_cnt = 4  # Number of images to be taken
    im0 = np.zeros((RWIDTH, RHEIGHT), dtype=np.float)
    im1 = np.zeros((RWIDTH, RHEIGHT), dtype=np.float)
    im2 = np.zeros((RWIDTH, RHEIGHT), dtype=np.float)
    im3 = np.zeros((RWIDTH, RHEIGHT), dtype=np.float)

    im_arr = [im0, im1, im2, im3]
    for i in range(image_cnt):
        my_file = str(folder) + "/" + preamble + str(offset+i+1) + ".png"
        # print(my_file)
        image = cv2.imread(my_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im_arr[i] = gray
        im_arr[i]= im_arr[i]*math.cos(2*np.pi*i/n_konstant)
    denom = sum(im_arr)

    wrap = np.zeros((RHEIGHT, RWIDTH), dtype=np.float)
    im_wrap = np.zeros((RHEIGHT, RWIDTH), dtype=np.float)
    for i in range(RHEIGHT):
        for j in range(RWIDTH):
            wrap[i, j] = np.arctan2(nom[i,j],denom[i,j])
            if wrap[i, j] < 0:
                wrap[i, j] += 2*np.pi
            im_wrap[i, j] = 128/np.pi * wrap[i, j]

    file_path = str(folder) + '/' + numpy_file
    np.save(file_path, wrap, allow_pickle=False)
    file_path = str(folder) + '/' + numpy_file[:-4] + '_mask.npy'
    np.save(file_path, mask, allow_pickle=False)
    if _DEBUG_OUT:
        png_file = str(folder) + '/' + png_file
        cv2.imwrite(png_file, im_wrap)
        mask_file = str(folder) + '/mask' + str(offset) + '.png'
        cv2.imwrite(mask_file, mask*128)
 