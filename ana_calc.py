"Make full analytic calculation on folder"
from pathlib import Path
from shutil import rmtree, copy, copytree
import time
from take_wrap import take_wrap4
from mask import mask
from unwrap import unwrapping

_PERF = True
_DEBUG = True

def copy_input(fromfolder, tofolder):
    "copy analytic file set to new tofolder"
    rmtree(tofolder, ignore_errors=True)
    tofolder.mkdir()
    for i in range(10):
        file = fromfolder / ("image"+str(i)+'.png')
        copy(file, tofolder)

def calculate_pcl(folder):
    "run the process"
    if _PERF:
        proc_st = time.process_time()
        st_time = time.time()
    if _DEBUG:
        print("Starting analytic on folder", folder)

    take_wrap4(folder, 'scan_wrap1.npy', 'im_wrap1.png', 'image', -1)
    take_wrap4(folder, 'scan_wrap2.npy', 'im_wrap2.png', 'image', 3)
    mask(folder)
    unwrapping(folder)

    if _PERF:
        end_time = time.time()
        proc_end = time.process_time()
        print("CPU exec time:", proc_end-proc_st, "seconds")
        print("Elapsed time:", end_time-st_time, "seconds")

def calc_folders(folder, number):
    "pass a folder tree"
    for i in range(number):
        myfolder = Path(str(folder)+str(i))
        print(myfolder)
        if myfolder.exists():
            calculate_pcl(myfolder)


if __name__=='__main__':
    tmpfolder = Path(__file__).parent / 'tmp'
    # testfolder = Path(__file__).parent / "testdata" / "analytic_test" / "testtarget1" / "render0"
    # copy_input(testfolder, tmpfolder)
    # calculate_pcl(tmpfolder)

    testfolder = Path(__file__).parent / "testdata" / "analytic_test" / "testtarget1"
    tree = tmpfolder / 'testtarget'
    rmtree(tree, ignore_errors=True)
    copytree(testfolder, tree)
    calc_folders(tree / 'render', 5)

    # proc time 0.125
    # elap time 0.155
    