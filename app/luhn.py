import random


def validate_luhn(pan: str) -> bool:
    if not pan.isdigit():
        return False

    digits = [int(d) for d in pan]
    checksum = 0

    for i in range(len(digits) - 2, -1, -2):
        doubled = digits[i] * 2
        if doubled > 9:
            checksum += (doubled % 10) + 1
        else:
            checksum += doubled

    for i in range(len(digits) - 1, -1, -2):
        checksum += digits[i]

    return checksum % 10 == 0


def generate_luhn(bin_prefix: str, length: int) -> str:
    random_part_length = length - len(bin_prefix) - 1

    if random_part_length < 0:
        raise ValueError("La longitud del BIN es mayor que la longitud total menos el checksum.")

    random_digits = "".join(str(random.randint(0, 9)) for _ in range(random_part_length))

    partial_pan = bin_prefix + random_digits + "0"

    digits = [int(d) for d in partial_pan]
    total = 0

    for i in range(length - 2, -1, -2):
        doubled = digits[i] * 2
        total += (doubled % 10) + (doubled // 10)

    for i in range(length - 1, -1, -2):
        total += digits[i]

    checksum_digit = (10 - (total % 10)) % 10

    return partial_pan[:-1] + str(checksum_digit)