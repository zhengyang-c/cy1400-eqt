import h5py
import numpy as np

f = "100samples.hdf5"

hf = h5py.File(f, 'r')

d = hf.get('data/109C.TA_20070930222739_EV')
d1 = np.array(d)
print(d1)
print(d1.shape) #(6000, 3)
#d1 = np.array(d)

hf.close()