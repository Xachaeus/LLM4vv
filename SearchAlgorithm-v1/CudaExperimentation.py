from numba import cuda
import numpy as np
import random, string



def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

arr = np.empty(4000, dtype=object)
for i in range(4000):
    arr[i] = randomword(5)
    
dest_arr = np.empty(4000,dtype=bool)

d_arr = cuda.to_device(arr)
d_dest_arr = cuda.to_device(dest_arr)


@cuda.jit
def test_func(arr, text, dest_arr):
    i = cuda.grid(1)
    if i<4000:
        arr[i]+""

print(arr)

test_func[256,64](d_arr, "hi", d_dest_arr)
dest_arr = d_dest_arr.copy_to_host()

print(dest_arr)
