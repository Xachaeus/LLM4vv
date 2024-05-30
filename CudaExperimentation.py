from numba import cuda
import numpy as np
import random, string



def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

arr = np.empty(4000, dtype=str)
for i in range(4000):
    arr[i] = randomword(5)
    
dest_arr = np.empty(4000,dtype=str)

d_arr = cuda.to_device(arr)
d_dest_arr = cuda.to_device(dest_arr)


@cuda.jit
def test_func(arr, dest_arr):
    i = cuda.grid(1)
    if i<4000:
        dest_arr[i] = arr[i] + "haha"

print(arr)

test_func[256,64](d_arr, d_dest_arr)
dest_arr = d_dest_arr.copy_to_host()

print(dest_arr)
