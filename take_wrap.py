"takewrap calulate wrap images"
import math
import numpy as np
import cv2
from ana_config import *


def take_wrap4(folder, numpy_file, png_file, preamble, offset):
    "folder is input folder with 10 images"
    if not folder.exists:
        raise FileNotFoundError("folder")
    N=4
    mask = np.zeros((rheight, rwidth), dtype=np.bool)
    process = np.zeros((rheight, rwidth), dtype=np.bool)
    c_range = np.zeros((rheight, rwidth), dtype=np.float)
    nom = np.zeros((rheight, rwidth), dtype=np.float)
    denom = np.zeros((rheight, rwidth), dtype=np.float)

    noise_threshold = 0.1

    image_cnt = 4  # Number of images to be taken
    im0 = np.zeros((rwidth, rheight), dtype=np.float)
    im1 = np.zeros((rwidth, rheight), dtype=np.float)
    im2 = np.zeros((rwidth, rheight), dtype=np.float)
    im3 = np.zeros((rwidth, rheight), dtype=np.float)

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
    im0 = np.zeros((rwidth, rheight), dtype=np.float)
    im1 = np.zeros((rwidth, rheight), dtype=np.float)
    im2 = np.zeros((rwidth, rheight), dtype=np.float)
    im3 = np.zeros((rwidth, rheight), dtype=np.float)

    im_arr = [im0, im1, im2, im3]
    for i in range(image_cnt):
        my_file = str(folder) + "/" + preamble + str(offset+i+1) + ".png"
        # print(my_file)
        image = cv2.imread(my_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im_arr[i] = gray
        im_arr[i]= im_arr[i]*math.cos(2*np.pi*i/N)
    denom = sum(im_arr)

    wrap = np.zeros((rheight, rwidth), dtype=np.float)
    im_wrap = np.zeros((rheight, rwidth), dtype=np.float)
    for i in range(rheight):
        for j in range(rwidth):
            # phi_sum = float(int(im_arr[0][i, j]) + int(im_arr[1]
            #                                            [i, j]) + int(im_arr[2][i, j] + int(im_arr[3][i, j])))
            # phi_max = float(
            #     max(im_arr[0][i, j], im_arr[1][i, j], im_arr[2][i, jrettet aktion
            # mask[i, j] = (signal < noise_threshold)
            # process[i, j] = not(mask[i, j])
            # c_range[i, j] = phi_range
            if True:#process[i, j]:
                wrap[i, j] = np.arctan2(nom[i,j],denom[i,j])
                if wrap[i, j] < 0:
                    wrap[i, j] += 2*np.pi
                im_wrap[i, j] = 128/np.pi * wrap[i, j]
            else:
                wrap[i, j] = 0
                im_wrap[i, j] = 0
    file_path = str(folder) + '/' + numpy_file
    np.save(file_path, wrap, allow_pickle=False)
    file_path = str(folder) + '/' + numpy_file[:-4] + '_mask.npy'
    np.save(file_path, mask, allow_pickle=False)
    # file_path = folder + '/' + numpy_file[:-4] + '_process.npy'
    # np.save(file_path, process, allow_pickle=False)
    # file_path = folder + '/' + numpy_file[:-4] + '_c_range.npy'
    # np.save(file_path, c_range, allow_pickle=False)
    # nom_file = folder + '/' + str(offset) + 'nom.png'
    # cv2.imwrite(nom_file, nom)
    # nom_file = folder + '/' + str(offset) + 'nom.npy'
    # np.save(nom_file, nom, allow_pickle=False)
    # denom_file = folder + '/' + str(offset) + 'denom.png'
    # cv2.imwrite(denom_file, denom)
    # denom_file = folder + '/' + str(offset) + 'denom.npy'
    # np.save(denom_file, denom, allow_pickle=False)
    png_file = str(folder) + '/' + png_file
    cv2.imwrite(png_file, im_wrap)
    mask_file = str(folder) + '/' + str(offset) + 'mask.png'
    cv2.imwrite(mask_file, mask*128)
    # cv2.destroyAllWindows()
    # print(c_range)
    # print(mask)
    # compute_quality()
