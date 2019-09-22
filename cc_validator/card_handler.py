from typing import List, Union
from random import randint, sample

from cc_validator.models import MajorIndustry, Issuer, IIN

reason_invalid_check_digit = "Check digit is not valid"
reason_unrecognized_issuer = "Card issuer is not recognized"
reason_invalid_length = "Card number length is not valid"


def get_check_digit(nums: List[int]) -> int:
    """
    Computes the check digit using the Luhn algorithm.
    See: https://en.wikipedia.org/wiki/Luhn_algorithm

    :param nums: A list of the numbers making up a card, (excluding the check digit)
    :return: The check digit
    """
    nums = list(nums)  # Avoid modifying whatever list was passed in (work on a copy)

    # Double every other digit, left-to-right and sum the resulting digits
    for i, num in enumerate(reversed(nums)):
        if i % 2 == 0:
            nums[i] = num * 2
            if nums[i] > 10:
                nums[i] -= 9  # Sum resulting digits

    # Sum `nums` and get the units digit (i.e. the "ones' place")
    total = sum(nums)
    unit_digit = total % 10

    # Check digit is whatever gets us to the next multiple of 10
    return 10 - unit_digit


def get_card_info(card_number: Union[int, str]) -> dict:
    """
    Determines a card's information based on its number.
    The following information is determined:
        - is_valid: whether or not this card number is valid (is check digit correct)
        - reason: if is_valid is False, the reason validation failed
        - check_digit: the cards check digit (the last digit in the card number)
        - mii_digit: the major industry identifier (this is the first digit in the card number)
        - issuer_category: the issuer category corresponding to mii_digit
        - iin: the issuer identifier number (the first 6 digits in the card number)
        - issuing_network: the issuing network corresponding to the iin
        - account_number: the personal account number (the digits after the 6th digit, excluding the last digit)

    If the card number is determined to be invalid, the return dictionary will only include 'is_valid' and 'reason'
    keys.

    Card information is determined using IOS/IEC 7812
    See: https://en.wikipedia.org/wiki/ISO/IEC_7812

    :param card_number: The card number either as a string or as an integer
    :return: A dictionary containing the determined information
    """
    card_nums = [int(x) for x in str(card_number)]
    is_number_valid = True
    valid_length = True
    issuer = None
    reason = None

    # Validate by checking the following:
    #   - check digit is correct
    #   - iin is recognized
    #   - card number has a valid length

    check_digit = get_check_digit(card_nums[:-1])
    if card_nums[-1] != check_digit:
        # perform first check, check digit check
        is_number_valid = False
        reason = reason_invalid_check_digit
    else:
        # perform second check, is iin recognized
        iin = None
        for i in range(6):
            iin_candidate = ''.join(str(x) for x in card_nums[:i + 1])
            if IIN.objects.filter(iin=iin_candidate).exists():
                iin = IIN.objects.get(iin=iin_candidate)
                issuer = iin.issuer
                break
        if iin is None:
            is_number_valid = False
            reason = reason_unrecognized_issuer

    if not reason and issuer:
        # perform final check, is length valid
        valid_length = len(card_nums) in issuer.get_valid_lengths()
        if not valid_length:
            reason = reason_invalid_length

    if not is_number_valid or not issuer or not valid_length:
        info = {'is_valid': False, 'reason': reason}
    else:
        major_industry = MajorIndustry.objects.get(pk=card_nums[0])
        info = {
            'is_valid': True,
            'mii_digit': card_nums[0],
            'issuer_category': major_industry.issuer_category,
            'iin': int(''.join(str(x) for x in card_nums[:6])),
            'issuing_network': issuer.network_name,
            'account_number': int(''.join(str(x) for x in card_nums[6:-1])),
            'check_digit': check_digit,
        }

    return info


def get_random_card(issuer: str) -> dict:
    """
    Generates a random card number given an issuer network name.

    :param issuer: The issuer network the card should belong to
    :return: A dictionary containing a 'generation_success' key indicating whether a card was able to be generated.
        If a card is generated, the number is stored in the 'card_number' key, otherwise a 'reason' key is returned.
    """
    response = {}
    reason = None
    issuer = Issuer.objects.filter(network_name=issuer).first()
    if issuer:
        iin = IIN.objects.filter(issuer=issuer).order_by('?').first()
        card_length =sample(issuer.get_valid_lengths(), 1)[0]

        # Need to generate random digits. Already have the iin and the check digit will be computed separately.
        card_digits = [int(x) for x in iin.iin]
        num_digits_left = card_length - len(iin.iin) - 1
        for _ in range(num_digits_left, 0, -1):
            card_digits.append(randint(0, 9))

        card_digits.append(get_check_digit(card_digits))
        response['card_number'] = int(''.join(str(x) for x in card_digits))
    else:
        reason = reason_unrecognized_issuer

    if reason:
        response['reason'] = reason
        response['generation_success'] = False
    else:
        response['generation_success'] = True

    return response
