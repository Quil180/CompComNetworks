#!/usr/bin/env python3
"""
Protection Strategies: CRC-8 and SEC-DED Implementation
HW6 - Computer Communications & Networks
Author: Yousef Alaa Awad

Implements:
  Task 2-1: CRC-8 (polynomial 0x107) and SEC-DED encoding for a 64-bit input.
  Task 2-2: Error injection & detection rate evaluation (1,000,000 trials each).
"""

import random

# ============================================================================
# Constants
# ============================================================================

# The fixed 64-bit input value
INPUT_VALUE = 0xFA7816EB87CC0911
INPUT_BITS = 64

# CRC polynomial: x^8 + x^2 + x + 1 = 0x107 (9 bits, degree 8)
CRC_POLY = 0x107
CRC_BITS = 8

# Number of trials for error detection evaluation
NUM_TRIALS = 1_000_000


# ============================================================================
# CRC-8 Implementation
# ============================================================================

def crc8_compute(data, data_bits=64):
    """
    Compute CRC-8 remainder for the given data using polynomial 0x107.
    
    The CRC is computed by appending 8 zero bits to the data and then
    performing polynomial long division (XOR-based) in GF(2).
    
    Args:
        data: Integer representing the data bits.
        data_bits: Number of bits in the data.
    
    Returns:
        The 8-bit CRC remainder as an integer.
    """
    # Shift data left by CRC_BITS to append zeros for division
    augmented = data << CRC_BITS
    total_bits = data_bits + CRC_BITS

    # Perform XOR-based polynomial division from MSB to LSB
    for i in range(total_bits - 1, CRC_BITS - 1, -1):
        if augmented & (1 << i):  # If the current bit is 1
            augmented ^= CRC_POLY << (i - CRC_BITS)

    # The remainder (lower 8 bits) is the CRC
    return augmented & 0xFF


def crc8_encode(data, data_bits=64):
    """
    Encode data with CRC-8 by appending the CRC remainder.
    Returns (crc_value, encoded_data) where encoded_data = data || CRC.
    """
    crc = crc8_compute(data, data_bits)
    encoded = (data << CRC_BITS) | crc
    return crc, encoded


def crc8_check(received, total_bits=72):
    """
    Check if received data (data + CRC) has errors.
    Divides the entire received message by the polynomial.
    If the remainder is 0, no error is detected.
    
    Returns:
        True if error is detected (remainder != 0), False otherwise.
    """
    # Divide the received value (which already includes the CRC) by the polynomial.
    # No zero-appending needed -- the CRC bits are already in place.
    value = received
    for i in range(total_bits - 1, CRC_BITS - 1, -1):
        if value & (1 << i):
            value ^= CRC_POLY << (i - CRC_BITS)
    remainder = value & 0xFF
    return remainder != 0


# ============================================================================
# SEC-DED (Hamming Code) Implementation
# ============================================================================

def secded_compute_parity_positions(data_bits):
    """
    Determine the number of parity bits needed for SEC-DED.
    For SEC-DED, we need r parity bits such that 2^r >= data_bits + r + 1,
    plus 1 extra overall parity bit for double error detection.
    
    For 64 data bits: r = 7 (since 2^7 = 128 >= 64 + 7 + 1 = 72),
    plus 1 overall parity = 8 total parity bits => 72 total bits.
    """
    r = 0
    while (1 << r) < data_bits + r + 1:
        r += 1
    return r


def secded_encode(data, data_bits=64):
    """
    Encode data using SEC-DED (Hamming code + overall parity).
    
    Parity bits are placed at positions that are powers of 2 (1-indexed):
    positions 1, 2, 4, 8, 16, 32, 64. Data bits fill the remaining positions.
    An overall parity bit is placed at position 0 for double error detection.
    
    Args:
        data: Integer representing the data.
        data_bits: Number of data bits.
    
    Returns:
        (encoded_value, total_bits): The encoded integer and its total bit count.
    """
    r = secded_compute_parity_positions(data_bits)
    total = data_bits + r + 1  # +1 for overall parity bit at position 0

    # Build the codeword as a list (1-indexed positions)
    # Position 0 = overall parity, positions 1..total-1 = Hamming positions
    codeword = [0] * total

    # Place data bits into non-parity positions (1-indexed)
    # Parity positions are powers of 2: 1, 2, 4, 8, 16, 32, 64
    data_idx = data_bits - 1  # MSB first
    for pos in range(1, total):
        if (pos & (pos - 1)) != 0:  # Not a power of 2 => data position
            if data_idx >= 0:
                codeword[pos] = (data >> data_idx) & 1
                data_idx -= 1

    # Compute each parity bit (covers positions where bit i of position is set)
    for i in range(r):
        parity_pos = 1 << i
        parity = 0
        for pos in range(1, total):
            if pos & parity_pos:
                parity ^= codeword[pos]
        codeword[parity_pos] = parity

    # Compute overall parity (position 0) = XOR of all bits
    codeword[0] = 0
    for pos in range(1, total):
        codeword[0] ^= codeword[pos]

    # Convert codeword list to integer (position 0 = MSB)
    encoded = 0
    for bit in codeword:
        encoded = (encoded << 1) | bit

    return encoded, total


def secded_check(received, total_bits=72):
    """
    Check received SEC-DED codeword for errors.
    
    Computes the syndrome (XOR of parity checks) and overall parity.
    - Syndrome == 0, overall parity OK => no error
    - Syndrome != 0, overall parity error => single-bit error (correctable)
    - Syndrome != 0, overall parity OK => double-bit error (detectable only)
    - Syndrome == 0, overall parity error => error in overall parity bit
    
    Returns:
        True if error is detected, False otherwise.
    """
    data_bits = 64
    r = secded_compute_parity_positions(data_bits)

    # Convert integer to bit list (MSB first, position 0 = MSB)
    bits = []
    for i in range(total_bits - 1, -1, -1):
        bits.append((received >> i) & 1)

    # Compute overall parity of all bits
    overall_parity = 0
    for b in bits:
        overall_parity ^= b

    # Compute syndrome from parity bit positions
    syndrome = 0
    for i in range(r):
        parity_pos = 1 << i
        parity = 0
        for pos in range(1, total_bits):
            if pos & parity_pos:
                parity ^= bits[pos]
        if parity != 0:
            syndrome |= (1 << i)

    # Detection logic:
    # If syndrome != 0 => error detected (single or double)
    # If syndrome == 0 and overall parity != 0 => error in overall parity bit
    # If syndrome == 0 and overall parity == 0 => no error
    if syndrome != 0:
        return True  # Error detected
    if overall_parity != 0:
        return True  # Error in overall parity bit
    return False  # No error detected


# ============================================================================
# Error Injection Functions
# ============================================================================

def inject_single_bit_error(value, num_bits):
    """Flip exactly 1 random bit."""
    pos = random.randint(0, num_bits - 1)
    return value ^ (1 << pos)


def inject_two_bit_error(value, num_bits):
    """Flip exactly 2 random distinct bits."""
    positions = random.sample(range(num_bits), 2)
    for p in positions:
        value ^= (1 << p)
    return value


def inject_three_bit_error(value, num_bits):
    """Flip exactly 3 random distinct bits."""
    positions = random.sample(range(num_bits), 3)
    for p in positions:
        value ^= (1 << p)
    return value


def inject_burst_error(value, num_bits, burst_len):
    """
    Inject an n-bit burst error.
    The first and last bits of the burst window are always flipped.
    Intermediate bits are flipped with 50% probability.
    The burst start position is chosen randomly.
    """
    # Choose a random starting position for the burst
    start = random.randint(0, num_bits - burst_len)
    # First bit of burst is always flipped
    value ^= (1 << start)
    # Last bit of burst is always flipped
    value ^= (1 << (start + burst_len - 1))
    # Intermediate bits flipped with 50% probability
    for i in range(1, burst_len - 1):
        if random.random() < 0.5:
            value ^= (1 << (start + i))
    return value


# ============================================================================
# Task 2-1: Compute and display CRC and SEC-DED outputs
# ============================================================================

def task2_1():
    """Compute and display CRC-8 and SEC-DED encoding for the fixed input."""
    print("=" * 70)
    print("  TASK 2-1: CRC-8 and SEC-DED Encoding")
    print("=" * 70)
    print(f"\n  Input value: 0x{INPUT_VALUE:016X}")
    print(f"  Input (binary): {INPUT_VALUE:064b}")

    # CRC-8
    crc, crc_encoded = crc8_encode(INPUT_VALUE, INPUT_BITS)
    print(f"\n  --- CRC-8 (Polynomial 0x107: x^8 + x^2 + x + 1) ---")
    print(f"  CRC-8 value:    0x{crc:02X} (binary: {crc:08b})")
    print(f"  Encoded data:   0x{crc_encoded:018X}")
    print(f"  Encoded (bin):  {crc_encoded:072b}")

    # Verify CRC: checking the encoded value should yield remainder 0
    has_error = crc8_check(crc_encoded, INPUT_BITS + CRC_BITS)
    print(f"  Verification:   {'ERROR' if has_error else 'OK (remainder = 0)'}")

    # SEC-DED
    secded_encoded, secded_total = secded_encode(INPUT_VALUE, INPUT_BITS)
    print(f"\n  --- SEC-DED (Hamming + overall parity) ---")
    print(f"  Total bits:     {secded_total} ({INPUT_BITS} data + "
          f"{secded_total - INPUT_BITS} parity)")
    print(f"  Encoded value:  0x{secded_encoded:018X}")
    print(f"  Encoded (bin):  {secded_encoded:0{secded_total}b}")

    # Verify SEC-DED: checking the encoded value should detect no error
    has_error = secded_check(secded_encoded, secded_total)
    print(f"  Verification:   {'ERROR' if has_error else 'OK (no error detected)'}")

    return crc_encoded, secded_encoded, secded_total


# ============================================================================
# Task 2-2: Error detection evaluation
# ============================================================================

def task2_2(crc_encoded, secded_encoded, secded_total):
    """
    Evaluate error detection rates for CRC-8 and SEC-DED.
    For each of 5 error types, inject errors into 1,000,000 random trials
    and record how often each scheme detects the error.
    """
    print("\n\n" + "=" * 70)
    print("  TASK 2-2: Error Detection Evaluation (1,000,000 trials each)")
    print("=" * 70)

    crc_total_bits = INPUT_BITS + CRC_BITS  # 72 bits for CRC-encoded data

    # Define the 5 error types as (name, injection_function)
    error_types = [
        ("Single-bit error",
         lambda v, n: inject_single_bit_error(v, n)),
        ("Two random-bit errors",
         lambda v, n: inject_two_bit_error(v, n)),
        ("Three random-bit errors",
         lambda v, n: inject_three_bit_error(v, n)),
        ("8-bit burst error",
         lambda v, n: inject_burst_error(v, n, 8)),
        ("16-bit burst error",
         lambda v, n: inject_burst_error(v, n, 16)),
    ]

    results = []

    for name, inject_fn in error_types:
        crc_detected = 0
        secded_detected = 0

        for _ in range(NUM_TRIALS):
            # Inject error into CRC-encoded value and check
            corrupted_crc = inject_fn(crc_encoded, crc_total_bits)
            if crc8_check(corrupted_crc, crc_total_bits):
                crc_detected += 1

            # Inject error into SEC-DED-encoded value and check
            corrupted_secded = inject_fn(secded_encoded, secded_total)
            if secded_check(corrupted_secded, secded_total):
                secded_detected += 1

        crc_rate = (crc_detected / NUM_TRIALS) * 100
        secded_rate = (secded_detected / NUM_TRIALS) * 100
        results.append((name, crc_rate, secded_rate))

        print(f"\n  {name}:")
        print(f"    CRC-8 detection rate:   {crc_rate:.4f}%"
              f"  ({crc_detected}/{NUM_TRIALS})")
        print(f"    SEC-DED detection rate:  {secded_rate:.4f}%"
              f"  ({secded_detected}/{NUM_TRIALS})")

    # Print summary table
    print("\n\n  " + "-" * 66)
    print(f"  {'Error Type':<28} {'CRC Rate (%)':>15} {'SEC-DED Rate (%)':>18}")
    print("  " + "-" * 66)
    for name, crc_rate, secded_rate in results:
        print(f"  {name:<28} {crc_rate:>14.4f}% {secded_rate:>17.4f}%")
    print("  " + "-" * 66)


# ============================================================================
# Main
# ============================================================================

def main():
    crc_encoded, secded_encoded, secded_total = task2_1()
    task2_2(crc_encoded, secded_encoded, secded_total)


if __name__ == "__main__":
    main()
