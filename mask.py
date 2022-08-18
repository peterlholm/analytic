"analytic mask module"
import numpy as np
import cv2

_RWIDTH = 160
_RHEIGHT = 160


def make_grayscale(img):
    "Transform color image to grayscale"
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray_img

DIFF_CONSTANT = 40

def mask(folder):
    "generate analytic mask"
    color = folder / 'image8.png'
    # print('color:', color)
    img1 = np.zeros((_RHEIGHT, _RWIDTH), dtype=np.float)
    img1 = cv2.imread(str(color), 1).astype(np.float32)
    gray = make_grayscale(img1)

    black = folder / 'image9.png'
    img2 = np.zeros((_RHEIGHT, _RWIDTH), dtype=np.float)
    img2 = cv2.imread(str(black), 0).astype(np.float32)
    diff1 = np.subtract(gray, .5*img2)
    maskarr =  np.zeros((_RHEIGHT, _RWIDTH), dtype=np.float)
    for i in range(_RHEIGHT):
        for j in range(_RWIDTH):
            if (diff1[i,j]<DIFF_CONSTANT):
                maskarr[i,j]= True
    np.save( folder / 'mask.npy', maskarr, allow_pickle=False)
    cv2.imwrite( str(folder / 'mask.png'), 255*maskarr)
    return mask
