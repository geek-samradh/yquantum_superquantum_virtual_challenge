from qiskit.quantum_info.operators import Pauli
from qiskit.quantum_info import Statevector
from qiskit.circuit import Parameter
from qiskit import transpile
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
import numpy as np
import random
import math

# Function to convert floating point values to fixed-point integers
def toFixed(x: float, fraction_bits: int) -> int:
    fraction_mult = 1 << fraction_bits
    return int(x * fraction_mult + (0.5 if x >= 0 else -0.5))

# Quantum Hash Function: Takes bytes input of size 2^N and returns a quantum hash as bytes of size 2^N
def qhash(x: bytes, returnCircuitInfo:bool=False):
    # Number of qubits in the circuit
    N = int(np.ceil(np.log2(len(x))))
    NUM_QUBITS = N
    # Number of fractional bits for fixed-point conversion
    FRACTION_BITS = 15
    # Total number of bits for the output
    TOTAL_BITS = 2 ** N 

    # Initialize the quantum circuit
    qc = QuantumCircuit(NUM_QUBITS)
    params = []

    # Number of layers for quantum circuit
    NUM_LAYERS = 4
    for l in range(NUM_LAYERS):
        for i in range(NUM_QUBITS):
            theta = Parameter(f"theta_rx_{l}_{i}")
            params.append(theta)
            qc.rx(theta, i)
        
        for i in range(NUM_QUBITS):
            theta = Parameter(f"theta_ry_{l}_{i}")
            params.append(theta)
            qc.ry(theta, i)

        for i in range(NUM_QUBITS):
            theta = Parameter(f"theta_rz_{l}_{i}")
            params.append(theta)
            qc.rz(theta, i)
            
        for i in range(NUM_QUBITS - 1):
            qc.cx(i, i + 1)
    
    # Input data to the hash function
    input_data = x
    output_bits = []

    # Generate quantum hash output bits
    while len(output_bits) < TOTAL_BITS:
        
        param_values = {}
        for i in range(len(params)):
            
            byte_index = i // 2  
            if byte_index >= len(input_data):
                nibble = (input_data[-1] >> (4 * (1 - (i % 2)))) & 0x0F
            else:
                nibble = (input_data[byte_index] >> (4 * (1 - (i % 2)))) & 0x0F

            value = nibble * math.pi / 8  # Scaled rotation angle
            param_values[params[i]] = value

        # bind parameters to the quantum circuit
        bound_qc = qc.assign_parameters(param_values)

        # obtaining statevector of the system
        sv = Statevector.from_instruction(bound_qc)

        # measuring expectation values of Z on each qubit
        exps = [sv.expectation_value(Pauli("Z"), [i]).real for i in range(NUM_QUBITS)]
        
        # converting expectation values to fixed-point format
        fixed_exps = [toFixed(exp, FRACTION_BITS) for exp in exps]

        # converting fixed-point values to bytes and collecting the output bits
        bits = []
        for fixed in fixed_exps:
            for i in range(FRACTION_BITS // 8):
                bits.append((fixed >> (8 * i)) & 0xFF)

        output_bits.extend(bits)
        input_data = bytes(bits)  

    total_bytes = TOTAL_BITS
    output_bits = output_bits[:total_bytes]
    if returnCircuitInfo:
        transpiled = transpile(bound_qc, basis_gates=['u3','cx'])
        info = {
            "qubits": len(transpiled.qubits),
            "depth": transpiled.depth(),
            "gate_count": transpiled.count_ops()
        } 
        return bytes(output_bits), info
    else:
        return bytes(output_bits)

def check_io_size(input_data, hash_data):
    if len(input_data) == len(hash_data):
        return True
    else:
        return False

# hash your bytes in here :)
if __name__ == "__main__":
    # LEAST CONDITION
    N = 6 # using N = 5 as base condition
    input_data = bytes([i % 256 for i in range(2 ** N)]) # bytes of length 2^N
    quantum_hash_output = qhash(input_data)
    print(list(quantum_hash_output))
    print(check_io_size(input_data, quantum_hash_output))

    #----------------------------------------
    # SOME BIG CONDITION
    N = 12
    input_data = bytes([i % 256 for i in range(2 ** N)]) # bytes of length 2^N
    quantum_hash_output = qhash(input_data)
    print(list(quantum_hash_output))
    print(check_io_size(input_data, quantum_hash_output))