from django.core.validators import validate_comma_separated_integer_list
from django.db import models


class MajorIndustry(models.Model):
    """
    Models for a card's major industry. Determined by a card's first digit.
    See: https://en.wikipedia.org/wiki/ISO/IEC_7812
    """
    issuer_category = models.CharField(max_length=128)


class Issuer(models.Model):
    """
    Models for a card's issuer. Determined by a card's first six digits.
    See: https://en.wikipedia.org/wiki/ISO/IEC_7812
    """
    network_name = models.CharField(primary_key=True, max_length=64)
    # Each Issuer has a range of accepted card lengths. See: https://en.wikipedia.org/wiki/Payment_card_number
    valid_lengths = models.CharField(max_length=256, validators=[validate_comma_separated_integer_list])

    def get_valid_lengths(self) -> set:
        """
        Gets a set of valid lengths.

        Some issuers may not have a contiguous range of valid lengths (e.g. for Solo and Switch valid lengths are 16,
        18, and 19), so a min/max tuple is purposefully not returned.


        :return: A set of valid lengths
        """
        return set([int(x) for x in self.valid_lengths.split(',')])


class IIN(models.Model):
    iin = models.CharField(primary_key=True, max_length=6)
    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE)

