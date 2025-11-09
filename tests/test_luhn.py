from app.luhn import validate_luhn, generate_luhn



def test_validate_luhn_valid_number():
    pan = "49927398716"
    assert validate_luhn(pan) == True


def test_validate_luhn_invalid_number():
    pan = "49927398717"
    assert validate_luhn(pan) == False


def test_validate_luhn_invalid_input():
    assert validate_luhn("4992739871A") == False
    assert validate_luhn("invalid-string") == False
    assert validate_luhn("") == False



def test_generate_luhn_length_and_prefix():
    bin_prefix = "4500"
    length = 16
    generated_pan = generate_luhn(bin_prefix, length)

    assert len(generated_pan) == length
    assert generated_pan.startswith(bin_prefix)


def test_generate_luhn_is_valid():
    bin_prefix = "5100"
    length = 16
    generated_pan = generate_luhn(bin_prefix, length)

    assert validate_luhn(generated_pan) == True


def test_generate_luhn_different_runs():
    gen1 = generate_luhn("6011", 16)
    gen2 = generate_luhn("6011", 16)
    assert gen1 != gen2
    assert validate_luhn(gen1)
    assert validate_luhn(gen2)
