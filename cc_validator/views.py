import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_GET

from cc_validator import responses
from cc_validator.card_handler import get_card_info, get_random_card


@require_POST
def validate_card(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest()
    card_number = payload.get('card_number', None)
    if not card_number or not isinstance(card_number, (str, int)):
        return responses.InvalidCardNumberTypeResponse()

    if isinstance(card_number, str):
        # Strip spaces from the card number
        card_number = card_number.replace(' ', '')
        try:
            int(card_number)
        except ValueError:
            return responses.InvalidCardNumberResponse()

    return HttpResponse(json.dumps(get_card_info(card_number)), content_type="application/json")


@require_GET
def gen_random_card_number(request):
    issuer = request.GET.get('issuer')
    if not issuer:
        return responses.InvalidIssuerName()

    return HttpResponse(json.dumps(get_random_card(issuer)), content_type="application/json")
