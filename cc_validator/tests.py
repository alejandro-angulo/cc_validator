import json
from typing import Union

from django.test import Client, TestCase
from django.urls import reverse

from cc_validator import responses
from cc_validator.models import Issuer
from cc_validator.card_handler import get_card_info, reason_invalid_length, reason_unrecognized_issuer, reason_invalid_check_digit


class ValidationTests(TestCase):
    fixtures = [
        'cc_validator/major_industries.json',
        'cc_validator/issuers.json',
        'cc_validator/iins.json',
    ]

    def setUp(self):
        self.client = Client()

    def test_valid_cards(self):
        card_number = 5555555555554444
        expected_status = 200
        expected_response_content = {
            'is_valid': True,
            'mii_digit': 5,
            'issuer_category': "Banking and financial",
            'iin': 555555,
            'issuing_network': "Mastercard",
            'account_number': 555555444,
            'check_digit': 4,
        }

        self._check_validate_card_response(card_number, expected_status, expected_response_content)

    def test_valid_card_with_string(self):
        card_number = "5555555555554444"
        expected_status = 200
        expected_response_content = {
            'is_valid': True,
            'mii_digit': 5,
            'issuer_category': "Banking and financial",
            'iin': 555555,
            'issuing_network': "Mastercard",
            'account_number': 555555444,
            'check_digit': 4,
        }

        self._check_validate_card_response(card_number, expected_status, expected_response_content)

    def test_invalid_card_length(self):
        card_number = 3796169067397641  # AmEx with valid check digit and length of 16 (should be 15)
        expected_status = 200
        expected_response_content = {
            'is_valid': False,
            'reason': reason_invalid_length,
        }

        self._check_validate_card_response(card_number, expected_status, expected_response_content)

    def test_unrecognized_issuer(self):
        card_number = 38225190345942  # Diners club number
        expected_status = 200
        expected_response_content = {
            'is_valid': False,
            'reason': reason_unrecognized_issuer,
        }

        self._check_validate_card_response(card_number, expected_status, expected_response_content)

    def test_invalid_digit_card(self):
        card_number = 55555555555544445555555555554444
        expected_status = 200
        expected_response_content = {
            'is_valid': False,
            'reason': reason_invalid_check_digit,
        }

        self._check_validate_card_response(card_number, expected_status, expected_response_content)


    def test_invalid_credit_card_string(self):
        card_number = "sdfsdfsd"
        invalid_card_number_response = responses.InvalidCardNumberResponse()
        expected_status = invalid_card_number_response.status_code
        expected_response_content = invalid_card_number_response.content

        self._check_validate_card_response(card_number, expected_status, expected_response_content, decode_json=False)

    def test_invalid_credit_card_type(self):
        card_number = [1, 2, 3]
        invalid_card_number_type_response = responses.InvalidCardNumberTypeResponse()
        expected_status = invalid_card_number_type_response.status_code
        expected_response_content = invalid_card_number_type_response.content

        self._check_validate_card_response(card_number, expected_status, expected_response_content, decode_json=False)

    def _check_validate_card_response(self, card_number: Union[int, str], expected_status: int,
                                      expected_response_content: dict, decode_json: bool = True):
        request_body = {'card_number': card_number}
        response = self.client.post(reverse('cc_validator:validate_card'), data=json.dumps(request_body),
                                    content_type='application/json')
        assert response.status_code == expected_status

        response_content = response.content
        if decode_json:
            response_content = json.loads(response.content)
        assert response_content == expected_response_content


class NumberGenerationTests(TestCase):
    fixtures = [
        'cc_validator/major_industries.json',
        'cc_validator/issuers.json',
        'cc_validator/iins.json',
    ]
    def setUp(self):
        self.client = Client()

    def test_number_generation(self):
        issuer = Issuer.objects.order_by('?').first()
        response = self.client.get(reverse('cc_validator:generate_card'), data={'issuer': issuer.network_name})

        assert response.status_code == 200

        generated_card = json.loads(response.content)
        assert generated_card['generation_success'] == True
        card_info = get_card_info(generated_card['card_number'])

        assert card_info['is_valid'] == True
        assert card_info['issuing_network'] == issuer.network_name

    def test_invalid_issuer(self):
        issuer_name = 'sdfdsf'
        response = self.client.get(reverse('cc_validator:generate_card'), data={'issuer': issuer_name})

        assert response.status_code == 200

        generated_card = json.loads(response.content)

        assert generated_card['generation_success'] == False
        assert generated_card['reason'] == reason_unrecognized_issuer
