# Under development, will be takin g shots for calibration
import cv2
import numpy as np
import time
# import pyntcloud
import math
import os.path
from os import path


rwidth = 160
rheight = 160


def sqdist(v1, v2):
    d = v1-v2
    return 1-d*d


def compute_quality(file, folder, c_range):
    file_path = folder + '/' + file
    wrap_data = np.load(file_path)
    quality = np.zeros((rheight, rwidth), dtype=np.float)
    for i in range(rheight):
        for j in range(rwidth):
            phi = wrap_data[i, j]
            quality[i, j] = (sqdist(phi, wrap_data[i+1, j]) + sqdist(phi, wrap_data[i-1, j]) +
                             sqdist(phi, wrap_data[i, j+1]) + sqdist(phi, wrap_data[i, j-1]))/c_range[i, j]
    file_path = folder + '/' + file[:-4] + '_quality.npy'
    np.save(file_path, quality, allow_pickle=False)



def get_A(im_arr):
    A = np.zeros((rwidth, rheight), dtype=np.float)
    for i in range(3):
        A = np.sum(A, im_arr[i])
    A = np.divide(A, 3)
    return A


def get_B(im_arr):
    for i in range(im_arr.length):
        B = np.multiply(im_arr[i], (np.sin(2*np.pi * i / im_arr.length)))

    return B


def get_average(array, n):
    b = np.add(array[0], array[1])
    average = 1/n * np.add(b, array[2])
    print('average size =', average.shape)
    return average


def avewrap(folder, file1, file2, average):
    a= np.load(folder+file1)
    b= np.load(folder+file2)
    c= (a+b)/2
    np.save(folder+average, c, allow_pickle=False)
    return

def distortion(folder):
    A = np.ones((rwidth, rheight))
    B = np.zeros((rwidth, rheight))
    im = np.zeros((rwidth,rheight))
    file = folder+'/image12.png'
    im = cv2.imread(file)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    B = (A-gray/255)*255
    cv2.imwrite(folder+'/distort.png', B )



def adjustLight(folder,myfile):
    A = np.ones((rwidth, rheight))
    B = np.zeros((rwidth, rheight))
    im = np.zeros((rwidth,rheight))
    im = cv2.imread(myfile)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    B = cv2.imread(folder+'/distort.png')
    B = cv2.cvtColor(B, cv2.COLOR_BGR2GRAY)
    result = np.multiply((B/255), gray)
    cv2.imwrite(myfile, result)


def take_wrap6(folder, numpy_file, png_file, preamble, offset):
    N=6
    mask = np.zeros((rheight, rwidth), dtype=np.bool)
    process = np.zeros((rheight, rwidth), dtype=np.bool)
    c_range = np.zeros((rheight, rwidth), dtype=np.float)
    nom = np.zeros((rheight, rwidth), dtype=np.float)
    denom = np.zeros((rheight, rwidth), dtype=np.float)
    

    noise_threshold = 0.1

    image_cnt = 6  # Number of images to be taken
    im0 = np.zeros((rwidth, rheight), dtype=np.float)
    im1 = np.zeros((rwidth, rheight), dtype=np.float)
    im2 = np.zeros((rwidth, rheight), dtype=np.float)
    im3 = np.zeros((rwidth, rheight), dtype=np.float)
    im4 = np.zeros((rwidth, rheight), dtype=np.float)
    im5 = np.zeros((rwidth, rheight), dtype=np.float)


    im_arr = [im0, im1, im2, im3, im4, im5]
    for i in range(image_cnt):
        my_file = folder + preamble + str(offset+i+1) + ".png"
        # adjustLight(folder, my_file)
        print(my_file)
        image = cv2.imread(my_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im_arr[i] = gray
        im_arr[i]= im_arr[i]*math.sin(2*np.pi*i/N)
    nom = sum(im_arr)

    im0 = np.zeros((rwidth, rheight), dtype=np.float)
    im1 = np.zeros((rwidth, rheight), dtype=np.float)
    im2 = np.zeros((rwidth, rheight), dtype=np.float)
    im3 = np.zeros((rwidth, rheight), dtype=np.float)
    im4 = np.zeros((rwidth, rheight), dtype=np.float)
    im5 = np.zeros((rwidth, rheight), dtype=np.float)


    im_arr = [im0, im1, im2, im3, im4, im5]

    for i in range(image_cnt):
        my_file = folder + preamble + str(offset+i+1) + ".png"
        # adjustLight(folder, my_file)
        print(my_file)
        image = cv2.imread(my_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im_arr[i] = gray
        im_arr[i]= im_arr[i]*math.cos(2*np.pi*i/N)
    denom = sum(im_arr)

    wrap = np.zeros((rheight, rwidth), dtype=np.float)
    im_wrap = np.zeros((rheight, rwidth), dtype=np.float)
    for i in range(rheight):
        for j in range(rwidth):
            phi_sum = float(
                int(im_arr[0][i, j]) + int(im_arr[1][i, j]) + int(im_arr[2][i, j])+ int(im_arr[3][i, j])+ int(im_arr[4][i, j])+ int(im_arr[5][i, j]))
            phi_max = float(
                max(im_arr[0][i, j],im_arr[1][i, j],im_arr[2][i, j],im_arr[3][i, j],im_arr[4][i, j],im_arr[5][i, j]))
            phi_min = float(
                min(im_arr[0][i, j],im_arr[1][i, j],im_arr[2][i, j],im_arr[3][i, j],im_arr[4][i, j],im_arr[5][i, j]))
            phi_range = float(phi_max - phi_min)
            if phi_sum == 0:
                phi_sum = .01
            noise = float(phi_range / phi_sum)
            mask[i, j] = (noise < noise_threshold)
            process[i, j] = not(mask[i, j])
            c_range[i, j] = phi_range
            c_range[i, j] = phi_range
            if process[i, j]:
                wrap[i, j] = np.arctan2(nom[i,j],denom[i,j])
                if wrap[i, j] < 0:
                    wrap[i, j] += 2*np.pi
                im_wrap[i, j] = 128/np.pi * wrap[i, j]
            else:
                wrap[i, j] = 0
                im_wrap[i, j] = 0
    file_path = folder + '/' + numpy_file
    np.save(file_path, wrap, allow_pickle=False)
    file_path = folder + '/' + numpy_file[:-4] + '_mask.npy'
    np.save(file_path, mask, allow_pickle=False)
    file_path = folder + '/' + numpy_file[:-4] + '_process.npy'
    np.save(file_path, process, allow_pickle=False)
    file_path = folder + '/' + numpy_file[:-4] + '_c_range.npy'
    np.save(file_path, c_range, allow_pickle=False)
    nom_file = folder + '/' + str(offset) + 'nom.png'
    cv2.imwrite(nom_file, nom)
    nom_file = folder + '/' + str(offset) + 'nom.npy'
    np.save(nom_file, nom, allow_pickle=False)
    denom_file = folder + '/' + str(offset) + 'denom.png'
    cv2.imwrite(denom_file, denom)
    denom_file = folder + '/' + str(offset) + 'denom.npy'
    np.save(denom_file, denom, allow_pickle=False)
    png_file = folder + '/' + png_file
    cv2.imwrite(png_file, im_wrap)
    mask_file = folder + '/' + str(offset) + 'mask.png'
    cv2.imwrite(mask_file, mask*128)
    cv2.destroyAllWindows()
    # print(c_range)
    # print(mask)
    # compute_quality()


def take_wrap12(folder, numpy_file, png_file, preamble, offset):
    N=12
    mask = np.zeros((rheight, rwidth), dtype=np.bool)
    process = np.zeros((rheight, rwidth), dtype=np.bool)
    c_range = np.zeros((rheight, rwidth), dtype=np.float)
    nom = np.zeros((rheight, rwidth), dtype=np.float)
    denom = np.zeros((rheight, rwidth), dtype=np.float)
    

    noise_threshold = 0.1

    image_cnt = 12  # Number of images to be taken
    im0 = np.zeros((rwidth, rheight), dtype=np.float)
    im1 = np.zeros((rwidth, rheight), dtype=np.float)
    im2 = np.zeros((rwidth, rheight), dtype=np.float)
    im3 = np.zeros((rwidth, rheight), dtype=np.float)
    im4 = np.zeros((rwidth, rheight), dtype=np.float)
    im5 = np.zeros((rwidth, rheight), dtype=np.float)
    im6 = np.zeros((rwidth, rheight), dtype=np.float)
    im7 = np.zeros((rwidth, rheight), dtype=np.float)
    im8 = np.zeros((rwidth, rheight), dtype=np.float)
    im9 = np.zeros((rwidth, rheight), dtype=np.float)
    im10 = np.zeros((rwidth, rheight), dtype=np.float)
    im11 = np.zeros((rwidth, rheight), dtype=np.float)

    im_arr = [im0, im1, im2, im3, im4, im5, im6, im7, im8, im9, im10, im11]
    for i in range(image_cnt):
        my_file = folder + preamble + str(offset+i+1) + ".png"
        print(my_file)
        image = cv2.imread(my_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im_arr[i] = gray
        im_arr[i]= im_arr[i]*math.sin(2*np.pi*i/N)
    nom = sum(im_arr)

    im0 = np.zeros((rwidth, rheight), dtype=np.float)
    im1 = np.zeros((rwidth, rheight), dtype=np.float)
    im2 = np.zeros((rwidth, rheight), dtype=np.float)
    im3 = np.zeros((rwidth, rheight), dtype=np.float)
    im4 = np.zeros((rwidth, rheight), dtype=np.float)
    im5 = np.zeros((rwidth, rheight), dtype=np.float)
    im6 = np.zeros((rwidth, rheight), dtype=np.float)
    im7 = np.zeros((rwidth, rheight), dtype=np.float)
    im8 = np.zeros((rwidth, rheight), dtype=np.float)
    im9 = np.zeros((rwidth, rheight), dtype=np.float)
    im10 = np.zeros((rwidth, rheight), dtype=np.float)
    im11 = np.zeros((rwidth, rheight), dtype=np.float)

    im_arr = [im0, im1, im2, im3, im4, im5, im6, im7, im8, im9, im10, im11]

    for i in range(image_cnt):
        my_file = folder + preamble + str(offset+i+1) + ".png"
        print(my_file)
        image = cv2.imread(my_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im_arr[i] = gray
        im_arr[i]= im_arr[i]*math.cos(2*np.pi*i/N)
    denom = sum(im_arr)

    wrap = np.zeros((rheight, rwidth), dtype=np.float)
    im_wrap = np.zeros((rheight, rwidth), dtype=np.float)
    for i in range(rheight):
        for j in range(rwidth):
            # c_range[i, j] = phi_range
            if True:#process[i, j]:
                wrap[i, j] = np.arctan2(nom[i,j],denom[i,j])
                if wrap[i, j] < 0:
                    wrap[i, j] += 2*np.pi
                im_wrap[i, j] = 128/np.pi * wrap[i, j]
            else:
                wrap[i, j] = 0
                im_wrap[i, j] = 0
    file_path = folder + '/' + numpy_file
    np.save(file_path, wrap, allow_pickle=False)
    file_path = folder + '/' + numpy_file[:-4] + '_mask.npy'
    np.save(file_path, mask, allow_pickle=False)
    file_path = folder + '/' + numpy_file[:-4] + '_process.npy'
    np.save(file_path, process, allow_pickle=False)
    file_path = folder + '/' + numpy_file[:-4] + '_c_range.npy'
    np.save(file_path, c_range, allow_pickle=False)
    nom_file = folder + '/' + str(offset) + 'nom.png'
    cv2.imwrite(nom_file, nom)
    nom_file = folder + '/' + str(offset) + 'nom.npy'
    np.save(nom_file, nom, allow_pickle=False)
    denom_file = folder + '/' + str(offset) + 'denom.png'
    cv2.imwrite(denom_file, denom)
    denom_file = folder + '/' + str(offset) + 'denom.npy'
    np.save(denom_file, denom, allow_pickle=False)
    png_file = folder + '/' + png_file
    cv2.imwrite(png_file, im_wrap)
    mask_file = folder + '/' + str(offset) + 'mask.png'
    cv2.imwrite(mask_file, mask*128)
    cv2.destroyAllWindows()
    # print(c_range)
    # print(mask)
    # compute_quality()

def take_wrap4(folder, numpy_file, png_file, preamble, offset):
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
        my_file = folder + preamble + str(offset+i+1) + ".png"
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
        my_file = folder + preamble + str(offset+i+1) + ".png"
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
    file_path = folder + '/' + numpy_file
    np.save(file_path, wrap, allow_pickle=False)
    file_path = folder + '/' + numpy_file[:-4] + '_mask.npy'
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
    png_file = folder + '/' + png_file
    cv2.imwrite(png_file, im_wrap)
    mask_file = folder + '/' + str(offset) + 'mask.png'
    cv2.imwrite(mask_file, mask*128)
    # cv2.destroyAllWindows()
    # print(c_range)
    # print(mask)
    # compute_quality()




def testwrap():
    N=4
    image_cnt = 4  # Number of images to be taken
    im0 = np.zeros((rwidth, rheight), dtype=np.float)
    im1 = np.zeros((rwidth, rheight), dtype=np.float)
    im2 = np.zeros((rwidth, rheight), dtype=np.float)
    im3 = np.zeros((rwidth, rheight), dtype=np.float)

    im_arr = [im0, im1, im2, im3]
    for i in range(image_cnt):
        my_file = folder + preamble + str(offset+i+1) + ".png"
        print(my_file)
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
        my_file = folder + preamble + str(offset+i+1) + ".png"
        print(my_file)
        image = cv2.imread(my_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im_arr[i] = gray
        im_arr[i]= im_arr[i]*math.cos(2*np.pi*i/N)
    denom = sum(im_arr)


def nn_wrap(nom, denom):
    # image = cv2.imread(nom)
    # greynom = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # image = cv2.imread(denom)
    # greydenom = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    wrap = np.zeros((rheight, rwidth), dtype=np.float)
    im_wrap = np.zeros((rheight, rwidth), dtype=np.float)
    # greynom = np.zeros((rheight, rwidth), dtype=np.float)
    # greydenom = np.zeros((rheight, rwidth), dtype=np.float)
    greynom = np.load(nom)
    greydenom = np.load(denom)
    for j in range(rwidth):
        for i in range(rheight):
            wrap[i, j] = np.arctan2(1.7320508 *greynom[i, j], greydenom[i, j])
            if wrap[i, j] < 0:
                if greynom[i, j] < 0:
                    wrap[i, j] += 2*np.pi
                else:
                    wrap[i, j] += 1 * np.pi
            im_wrap[i, j] = 128/np.pi * wrap[i, j]

    wrap = cv2.GaussianBlur(wrap, (3, 3), 0)
    im_wrap = cv2.GaussianBlur(im_wrap, (3, 3), 0)
    return(im_wrap)

def make_grayscale(img):
    # Transform color image to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray_img





def mask(folder):
    color = folder + 'image8.png'
    # print('color:', color)
    img1 = np.zeros((rheight, rwidth), dtype=np.float)
    img1 = cv2.imread(color, 1).astype(np.float32)
    gray = make_grayscale(img1)


    black = folder + 'image9.png'
    img2 = np.zeros((rheight, rwidth), dtype=np.float)
    img2 = cv2.imread(black, 0).astype(np.float32)
    diff1 = np.subtract(gray, .5*img2)
    mask =  np.zeros((rheight, rwidth), dtype=np.float)
    for i in range(rheight):
        for j in range(rwidth):
            if (diff1[i,j]<40):
                mask[i,j]= True
    np.save( folder+ 'mask.npy', mask, allow_pickle=False)
    cv2.imwrite( folder+ 'mask.png', 255*mask)
    return(mask)


def masktest(folder, thresh):
    color = folder + 'image8.png'
    print('color:', color)
    img1 = np.zeros((rheight, rwidth), dtype=np.float)
    img1 = cv2.imread(color, 1).astype(np.float32)
    gray = make_grayscale(img1)


    black = folder + 'image9.png'
    img2 = np.zeros((rheight, rwidth), dtype=np.float)
    img2 = cv2.imread(black, 0).astype(np.float32)
    diff1 = np.subtract(gray, .5*img2)
    mask =  np.zeros((rheight, rwidth), dtype=np.float)
    for i in range(rheight):
        for j in range(rwidth):
            if (diff1[i,j]<thresh):
                mask[i,j]= True
    np.save( folder+ 'mask.npy', mask, allow_pickle=False)
    cv2.imwrite( folder+ str(thresh)+'mask.png', 128*mask)
    return(mask)



def testarctan(folder):
    nominator = folder + '1nom.npy'
    denominator = folder + '1denom.npy'
    test_im_wrap = nn_wrap(nominator, denominator)
    png_file = folder + 'npy_im_wrap.png'
    cv2.imwrite(png_file, test_im_wrap)


# folder = '/home/samir/db2/scan/static/scan_folder/scan_im_folder/' 
# testarctan(folder)
# greynom = np.load(folder + '1denom.npy')
# cv2.imwrite(folder + 'npy1denom.png',
#             (greynom).astype(np.uint8))
# greynom = np.load(folder + '1nom.npy')
# cv2.imwrite(folder + 'npy1nom.png',
#             (greynom).astype(np.uint8))

# folder = '/home/samir/db2/scan/static/scan_folder/scan_im_folder/' 
# imagemask = cv2.imread(folder + 'image-1.png')
# graymask = cv2.cvtColor(imagemask, cv2.COLOR_BGR2GRAY)
# image1 = cv2.imread(folder + 'image0.png')
# gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
# image2 = cv2.imread(folder + 'image2.png')
# gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
# image3 = np.zeros((rwidth, rheight), dtype=np.float)
# image3 = gray2 - gray1
# image4 = cv2.imread(folder + 'mymaskimg.png')
# gray4 = cv2.cvtColor(image4, cv2.COLOR_BGR2GRAY)
# gray4 = np.transpose(gray4)
# image3 =np.transpose(image3)
# mask = np.zeros((rwidth, rheight), dtype=np.bool)
# maskimg = np.zeros((rwidth, rheight), dtype=np.int)
# for i in range(rwidth):
#     for j in range(rheight):
#         mask[i,j] = not((image3[i,j] < 55)  or (image3[i,j]> 240)) and (gray4[i,j] > 20)
#         maskimg[i,j] = mask[i,j]* 200
# maskimg = np.transpose(maskimg)
# image3 = np.transpose(image3)
# gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
# cv2.imwrite(folder + 'diff.png', image3)
# cv2.imwrite(folder + 'maskimg.png', maskimg)

# myfolder = '/data/testsave/'
myfolder = '/home/samir/Desktop/blender/pycode/bldev2/scans/30wand/lf/'
# myfolder = '/home/samir/db3/scan/static/scan_folder/scan_im_folder/'
count=len(os.listdir(myfolder))
# print(count)
# count = 100
start = 0
for i in range(start, start+count):
    print(i)
    folder = myfolder+'render'+ str(i)+'/'

    # if path.exists(folder):
    # distortion(folder)
    take_wrap4(folder, 'scan_wrap1.npy', 'im_wrap1.png', 'image', -1)
    take_wrap4(folder, 'scan_wrap2.npy', 'im_wrap2.png', 'image', 3)
    mask(folder)
    # take_wrap4(folder, 'scan_wrap1.npy', 'im_wrap1.png', 'blenderimage', -1)
    # take_wrap4(folder, 'scan_wrap2.npy', 'im_wrap2.png', 'blenderimage', 5)

    # images = glob.glob(folder+'*/image1.png', recursive= True)
    # print('image count:',len(images))
    # mresults=[[0,0,0,0,0,0,0]]
    # for fname in images:



#####################################################################################################################



# def take_wrap(folder, numpy_file, png_file, preamble, offset):
#     print('take_wrap !!!!!')
#     print(folder, png_file)
#     mask = np.zeros((rheight, rwidth), dtype=np.bool)
#     process = np.zeros((rheight, rwidth), dtype=np.bool)
#     c_range = np.zeros((rheight, rwidth), dtype=np.float)
#     depth = np.zeros((rheight, rwidth), dtype=np.float)

#     # folder = '/home/samir/db2/scan/static/scan_folder/scan_im_folder/' 
#     # imagemask = cv2.imread(folder + 'image-1.png')
#     # graymask = cv2.cvtColor(imagemask, cv2.COLOR_BGR2GRAY)
#     # image1 = cv2.imread(folder + 'image0.png')
#     # gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
#     # image2 = cv2.imread(folder + 'image2.png')
#     # gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
#     # image3 = np.zeros((rwidth, rheight), dtype=np.float)
#     # image3 = gray2 - gray1
#     # image4 = cv2.imread(folder + 'mymaskimg.png')
#     # gray4 = cv2.cvtColor(image4, cv2.COLOR_BGR2GRAY)
#     # gray4 = np.transpose(gray4)
#     # image3 =np.transpose(image3)
#     # mask = np.zeros((rwidth, rheight), dtype=np.bool)
#     # maskimg = np.zeros((rwidth, rheight), dtype=np.int)
#     # for i in range(rwidth):
#     #     for j in range(rheight):
#     #         mask[i,j] = not((image3[i,j] < 55)  or (image3[i,j]> 240)) and (gray4[i,j] > 20)
#     #         maskimg[i,j] = mask[i,j]* 200
#     # maskimg = np.transpose(maskimg)
#     # mask = np.transpose(mask)
#     # image3 = np.transpose(image3)
#     # gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
#     # cv2.imwrite(folder + 'diff.png', image3)
#     # cv2.imwrite(folder + 'maskimg.png', maskimg)

#     image_cnt = 3  # Number of images to be taken
#     im0 = np.zeros((rwidth, rheight), dtype=np.float)
#     im1 = np.zeros((rwidth, rheight), dtype=np.float)
#     im2 = np.zeros((rwidth, rheight), dtype=np.float)
#     imtexture = np.zeros((rheight, rwidth), dtype=np.float)
#     imblack = np.zeros((rheight, rwidth), dtype=np.float)
#     nom = np.zeros((rheight, rwidth), dtype=np.float)
#     denom = np.zeros((rheight, rwidth), dtype=np.float)
#     imtexture = cv2.imread(folder+'/blendertexture.png')
#     imblack = cv2.imread(folder+'/blenderblack.png')
#     imdiff = np.subtract(imtexture,imblack)
#     cv2.imwrite(folder+'/imdiff.png', imdiff)
#     im_arr = [im0, im1, im2]
#     for i in range(image_cnt):
#         my_file = folder + preamble + str(offset+i+1) + ".png"
#         print(my_file)
#         image = cv2.imread(my_file)
#         grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         im_arr[i] = grey
#     bkg_intensity = get_average(im_arr, image_cnt)
#     # bkg_intensity = get_A(im_arr)
#     wrap = np.zeros((rheight, rwidth), dtype=np.float)
#     im_wrap = np.zeros((rheight, rwidth), dtype=np.float)
#     for i in range(rheight):
#         for j in range(rwidth):
#             # phi_sum = float(
#             #     int(im_arr[0][i, j]) + int(im_arr[1][i, j]) + int(im_arr[2][i, j]))
#             # phi_max = float(
#             #     max(im_arr[0][i, j], im_arr[1][i, j], im_arr[2][i, j]))
#             # phi_min = float(
#             #     min(im_arr[0][i, j], im_arr[1][i, j], im_arr[2][i, j]))
#             # phi_range = float(phi_max - phi_min)
#             # if phi_sum == 0:
#             #     phi_sum = .01
#             # noise = float(phi_range / phi_sum)
#             if (imdiff[i,j][0]<55):
#                 mask[i,j]= True
#             # mask[i, j] = (imdiff[i,j] < 3)
#             process[i, j] = not(mask[i, j])
#             # c_range[i, j] = phi_range
#             if  process[i,j]: # True: #(maskimg[i,j]  > 30): #True:  # process[i, j]:
#                 a = (1.0*im_arr[1][i, j]-1.0*im_arr[2][i, j])
#                 b = (2.0*im_arr[0][i, j] - 1.0*im_arr[1][i, j] - 1.0*im_arr[2][i, j])
#                 nom[i, j] = a
#                 denom[i, j] = b
#                 wrap[i, j] =  np.arctan2(1.7320508*nom[i, j], denom[i, j])

#                 if wrap[i, j] < 0:
#                     if nom[i, j] < 0:
#                         wrap[i, j] += 2*np.pi
#                     else:
#                         wrap[i, j] += 1 * np.pi
#                 # wrap[i, j] =  math.atan(1.7320508*a/b) #np.arctan(1.7320508 * nom[i, j], denom[i, j])
#                 # if a>0 and b>0:
#                 #     wrap[i,j]
#                 # else:
#                 #     if a>0 and b<0:
#                 #         wrap[i,j] += np.pi
#                 #     else:
#                 #         if a<0 and b<0:
#                 #             wrap[i,j] -=np.pi
#                 #         else:
#                 #             if a<0 and b>0:
#                 #                 wrap[i,j]


#                 im_wrap[i, j] = 128*wrap[i, j]/np.pi
#             else:
#                 wrap[i, j] = 0
#                 im_wrap[i, j] = 0
#     print('wrap range:', np.ptp(wrap))
#     wrap = cv2.GaussianBlur(wrap, (3, 3), 0)
#     file_path = folder + '/' + numpy_file
#     np.save(file_path, wrap, allow_pickle=False)
#     file_path = folder + '/' + numpy_file[:-4] + '_mask.npy'
#     np.save(file_path, mask, allow_pickle=False)
#     file_path = folder + '/' + numpy_file[:-4] + '_process.npy'
#     np.save(file_path, process, allow_pickle=False)
#     file_path = folder + '/' + numpy_file[:-4] + '_c_range.npy'
#     np.save(file_path, c_range, allow_pickle=False)
#     png_file = folder + '/' + png_file
#     cv2.imwrite(png_file, im_wrap)
#     print('written im_wrap:', png_file)
#     nom_file = folder + '/' + str(offset) + 'nom.png'
#     cv2.imwrite(nom_file, nom)
#     nom_file = folder + '/' + str(offset) + 'nom.npy'
#     np.save(nom_file, nom, allow_pickle=False)
#     denom_file = folder + '/' + str(offset) + 'denom.png'
#     cv2.imwrite(denom_file, denom)
#     denom_file = folder + '/' + str(offset) + 'denom.npy'
#     np.save(denom_file, denom, allow_pickle=False)
#     bkg_file = folder + '/' + str(offset) + 'bkg.png'
#     cv2.imwrite(bkg_file, bkg_intensity)
#     mask_file = folder + '/' + str(offset) + 'mask.png'
#     cv2.imwrite(mask_file, mask*128)
#     process_file = folder + '/' + str(offset) + 'process.png'
#     cv2.imwrite(process_file, process*128)
#     cv2.destroyAllWindows()
#     print('nom', nom)
#     print('denom', denom)
#     # compute_quality()


# cv2.destroyAllWindows()
