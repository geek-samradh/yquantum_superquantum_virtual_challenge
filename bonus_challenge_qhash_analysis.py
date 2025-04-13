import math
import random
import time
from collections import Counter
from qhash import qhash # qhash function
import matplotlib.pyplot as plt

# Most of the functions are similar from analysis.py, some are modified according to specific needs
# === Helper Functions ===

def to_bits(byte_array):
    return ''.join(f'{b:08b}' for b in byte_array)

def shannon_entropy(byte_list):
    counter = Counter(byte_list)
    total = sum(counter.values())
    return -sum((count / total) * math.log2(count / total) for count in counter.values())

# === Analysis Functions ===

def test_determinism(qhash, input_data, runs=3):
    print("[Test] Determinism")
    results = [qhash(input_data) for _ in range(runs)]
    is_deterministic = all(r == results[0] for r in results)
    print(f"  Result: {'PASS' if is_deterministic else 'FAIL'}")
    return is_deterministic

def test_entropy_preservation(qhash, input_size, samples=100):
    print("[Test] Entropy Preservation")
    outputs = [qhash(bytes([random.getrandbits(8) for _ in range(input_size)])) for _ in range(samples)]
    output_matrix = list(zip(*outputs))  # byte-wise columns
    entropies = [shannon_entropy(col) for col in output_matrix]
    avg_entropy = sum(entropies) / len(entropies)
    print(f"  Avg entropy per byte: {avg_entropy:.2f} / 8")
    
    # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(entropies, marker='o')
    plt.title("Shannon Entropy per Output Byte")
    plt.xlabel("Byte Index")
    plt.ylabel("Entropy (bits)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return avg_entropy

def test_preimage_resistance(qhash, input_size, trials=1000):
    print("[Test] Preimage Resistance")
    target = qhash(bytes([random.getrandbits(8) for _ in range(input_size)]))
    for _ in range(trials):
        guess = bytes([random.getrandbits(8) for _ in range(input_size)])
        if qhash(guess) == target:
            print("  Result: FAIL – Found preimage")
            return False
    print("  Result: PASS – No preimage found")
    return True

def test_collision_resistance(qhash, input_size, samples=500):
    print("[Test] Collision Resistance")
    seen = set()
    for _ in range(samples):
        h = qhash(bytes([random.getrandbits(8) for _ in range(input_size)]))
        if h in seen:
            print("  Result: FAIL – Collision detected")
            return False
        seen.add(h)
    print("  Result: PASS – No collisions")
    return True

def test_io_size(input_data, hash_data):
    print("[Test] Output Size Matches Input")
    match = len(input_data) == len(hash_data)
    print(f"  Result: {'PASS' if match else 'FAIL'}")
    return match

if __name__ == "__main__":
    N = 7
    input_data = bytes([i % 256 for i in range(2 ** N)])
    hash_data = qhash(input_data)

    print("=== Quantum Hash Analysis Suite ===")
    test_determinism(qhash, input_data)
    test_entropy_preservation(qhash, input_size=2 ** N)
    test_preimage_resistance(qhash, input_size=2 ** N)
    test_collision_resistance(qhash, input_size=2 ** N)
    test_io_size(input_data, hash_data)