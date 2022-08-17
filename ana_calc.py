"Make full analytic calculation on folder"
from pathlib import Path
from take_wrap import take_wrap4

def gen_pcl(folder):
    "run the process"
    print("Starting analytic on folder", folder)

    take_wrap4(folder, 'scan_wrap1.npy', 'im_wrap1.png', 'image', -1)
    take_wrap4(folder, 'scan_wrap2.npy', 'im_wrap2.png', 'image', 3)
    #mask(folder)


folder = Path(__file__).parent / "testdata" / "analytic_test" / "data"

gen_pcl(folder)
