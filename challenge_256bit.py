from main import qhash
from analysis import check_io_size
import random

import numpy as np
from scipy.fftpack import dct

def signal_scale_to_256_bytes(data: bytes) -> bytes:
    if len(data) == 0:
        return bytes([0]*256)

    # Normalizing byte data to floats in [-1, 1]
    x = np.array([b / 127.5 - 1.0 for b in data], dtype=np.float32)

    # Applying DCT
    coeffs = dct(x, type=2, norm='ortho')

    # Taking first 256 coefficients
    if len(coeffs) < 256:
        coeffs = np.pad(coeffs, (0, 256 - len(coeffs)), mode='constant')
    else:
        coeffs = coeffs[:256]

    # Normalizing and quantizing to 8-bit
    coeffs -= coeffs.min()
    if coeffs.max() > 0:
        coeffs /= coeffs.max()
    coeffs = (coeffs * 255).astype(np.uint8)

    return bytes(coeffs)

# since we have already have 2^N to 2^N hash function, we need to find a way to convert input
# into size of 256.

for i in range(50):
    input_data = bytes([i % 256 for i in range(random.randint(1, 1024))])
    input_data_scaled = signal_scale_to_256_bytes(input_data)
    generated_hash = qhash(input_data_scaled)
    print(f"{len(generated_hash)}")
    print(check_io_size(input_data_scaled, generated_hash))