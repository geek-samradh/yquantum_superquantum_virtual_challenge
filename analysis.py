import math
import random
from collections import Counter
from main import qhash
import matplotlib.pyplot as plt

def test_determinism(qhash, input_data, runs=3):
    results = [qhash(input_data) for _ in range(runs)]
    is_deterministic = all(r == results[0] for r in results)
    print(f"[Determinism] {'Pass' if is_deterministic else 'Fail'}")
    return is_deterministic


def shannon_entropy(byte_list):
    counter = Counter(byte_list)
    total = sum(counter.values())
    return -sum((count / total) * math.log2(count / total) for count in counter.values())

def test_entropy_preservation(qhash, input_size, samples=100):
    outputs = [qhash(bytes([random.getrandbits(8) for _ in range(input_size)])) for _ in range(samples)]
    output_matrix = [list(o) for o in outputs]
    output_matrix = list(zip(*output_matrix))  # transpose: bytes per position

    entropies = [shannon_entropy(pos) for pos in output_matrix]
    avg_entropy = sum(entropies) / len(entropies)
    print(f"[Entropy Preservation] Avg entropy per byte: {avg_entropy:.2f}/8")
    return avg_entropy

import time

def test_computational_difficulty(qhash, sizes=[4, 5, 6]):
    print("[Computational Difficulty]")
    for N in sizes:
        input_data = bytes([random.getrandbits(8) for _ in range(2 ** N)])
        start = time.time()
        _ = qhash(input_data)
        elapsed = time.time() - start
        print(f"  N={N}, size={2**N} bytes -> Time: {elapsed:.4f}s")

def test_preimage_resistance(qhash, input_size, trials=1000):
    target = qhash(bytes([random.getrandbits(8) for _ in range(input_size)]))
    for _ in range(trials):
        guess = bytes([random.getrandbits(8) for _ in range(input_size)])
        if qhash(guess) == target:
            print("[Preimage Resistance] FAIL: Found preimage")
            return False
    print("[Preimage Resistance] PASS: No preimage found in small space")
    return True

def test_collision_resistance(qhash, input_size, samples=500):
    outputs = set()
    for _ in range(samples):
        h = qhash(bytes([random.getrandbits(8) for _ in range(input_size)]))
        if h in outputs:
            print("[Collision Resistance] FAIL: Collision detected")
            return False
        outputs.add(h)
    print("[Collision Resistance] PASS: No collisions")
    return True


def get_circuit_complexity(qhash:qhash, N_greaterthan5:int):
    infos = []
    for n in range(5, N_greaterthan5):
        print(f"executing for 2^{n}...")
        rand_input = input_data = bytes([i % 256 for i in range(2 ** n)])
        start_time = time.time()
        hash_output, info = qhash(rand_input, returnCircuitInfo=True)
        end_time = time.time()
        infos.append([n, info, end_time-start_time])
    return infos

def plot_complexity(infolist):
    Ns = [item[0] for item in infolist]
    qubits = [item[1]['qubits'] for item in infolist]
    depths = [item[1]['depth'] for item in infolist]
    u3_counts = [item[1]['gate_count'].get('u3', 0) for item in infolist]
    cx_counts = [item[1]['gate_count'].get('cx', 0) for item in infolist]
    times = [item[2] for item in infolist]

    plt.figure(figsize=(10, 5))
    plt.plot(Ns, qubits, label='Qubits', marker='o')
    plt.plot(Ns, depths, label='Depth', marker='s')
    plt.xlabel('N')
    plt.ylabel('Value')
    plt.title('Qubits and Depth vs N')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Plot 2: u3 and cx counts vs N
    plt.figure(figsize=(10, 5))
    plt.plot(Ns, u3_counts, label='u3 Count', marker='^')
    plt.plot(Ns, cx_counts, label='cx Count', marker='x')
    plt.xlabel('N')
    plt.ylabel('Gate Count')
    plt.title('u3 and cx Gate Counts vs N')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Plot 2: u3 and cx counts vs N
    plt.figure(figsize=(10, 5))
    plt.plot(Ns, times, label='time to run', marker='^')
    plt.xlabel('N')
    plt.ylabel('time (s)')
    plt.title('N vs Time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def check_io_size(input_data, hash_data):
    if len(input_data) == len(hash_data):
        return True
    else:
        return False


if __name__ == "__main__":
    N = 7
    input_data = bytes([i % 256 for i in range(2 ** N)])

    test_determinism(qhash, input_data)
    test_entropy_preservation(qhash, input_size=2 ** N)
    # test_computational_difficulty(qhash) # use this when using atleast N = 8, to see some lines
    # print("[CIRCUIT COMPLEXITY]")
    # complexity = get_circuit_complexity(qhash, N)
    # plot_complexity(complexity)
    test_preimage_resistance(qhash, input_size=2 ** N)
    test_collision_resistance(qhash, input_size=2 ** N)