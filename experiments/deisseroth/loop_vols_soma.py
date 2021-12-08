from cloudvolume import CloudVolume
from skimage import io, measure
import numpy as np
import sys
import warnings
import subprocess
from tqdm import tqdm
import h5py
from joblib import Parallel, delayed
import multiprocessing
import os

chunk_size = [256, 256, 300]
ncpu = 11
dir = "precomputed://https://dlab-colm.neurodata.io/2021_10_06/8557/Ch_647"
progress_file = "/home/tathey1/progress_soma.txt" #"/Users/thomasathey/Documents/mimlab/mouselight/ailey/benchmark_formal/brain4/tracing/progress.txt" 
files_dir = "/data/tathey1/matt_wright/brainr1/"
somas_file = "/home/tathey1/somas.txt"

with open(progress_file) as f:
    for line in f:
        pass
    last_line = line

coords_list = last_line.split(' ')
coords = [int(coord) for coord in coords_list]

print(f"Number cpus: {multiprocessing.cpu_count()}")

warnings.filterwarnings("ignore")


def process_chunk(i, j, k):
    data_dir = "/data/tathey1/matt_wright/brainr1/"
    chunk_size = [256, 256, 300]
    mip = 0
    
    dir_fg = "precomputed://https://dlab-colm.neurodata.io/2021_10_06/8557/Ch_647"
    vol_fg = CloudVolume(dir_fg, parallel=1, mip=mip, fill_missing=True)

    shape = vol_fg.shape

    i2 = np.amin([i+chunk_size[0], shape[0]])
    j2 = np.amin([j+chunk_size[1], shape[1]])
    k2 = np.amin([k+chunk_size[2], shape[2]])
    image_1channel = np.squeeze(np.stack([vol_fg[i:i2,j:j2,k:k2]], axis=0))


    fname = data_dir + "/image_" + str(k) + ".h5"
    with h5py.File(fname, "w") as f:
        dset = f.create_dataset("image_3channel", data=image_1channel)
    
    subprocess.run(["/home/tathey1/ilastik-1.3.3post3-Linux/run_ilastik.sh", "--headless", "--project=/data/tathey1/matt_wright/ilastik/soma_model/matt_soma_rabies_pix_3ch.ilp", fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #subprocess.run(["/Applications/ilastik-1.3.3post3-OSX.app/Contents/ilastik-release/run_ilastik.sh", "--headless", "--project=/Users/thomasathey/Documents/mimlab/mouselight/ailey/benchmark_formal/brain3/matt_benchmark_formal_brain3.ilp", fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    f = h5py.File(data_dir + "image_" + str(k) + "_Probabilities.h5", "r")
    pred = f.get("exported_data")

    pred = pred[:,:,:,0]

    mask = pred > 0.65
    labels = measure.label(mask)
    props = measure.regionprops(labels)

    results = []
    for prop in props:
        if prop["area"] > 500:
            location = list(np.add((i,j,k), prop["centroid"]))
            results.append(location)
    return results




mip = 0
vol = CloudVolume(dir, parallel=True, mip=mip, fill_missing=True)
shape = vol.shape

for i in tqdm(range(coords[0], shape[0], chunk_size[0])):
    for j in tqdm(range(coords[1], shape[1], chunk_size[1]), leave=False):    
        results = Parallel(n_jobs=ncpu)(delayed(process_chunk)(i,j,k) for k in range(0,shape[2],chunk_size[2]))
        
        with open(somas_file, 'a+') as f:
            for results_chunk in results:
                for location in results_chunk:
                    f.write('\n')
                    f.write(f'{location}')

        with open(progress_file, 'a') as f:
            f.write('\n')
            f.write(f'{i} {j}')
        
        for f in os.listdir(files_dir):
            os.remove(os.path.join(files_dir, f))

    coords[1] = 0
        

