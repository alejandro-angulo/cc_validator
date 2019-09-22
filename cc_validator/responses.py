from django.http import HttpResponse


class InvalidCardNumberTypeResponse(HttpResponse):
    def __init__(self):
        super().__init__("`card_number` must be passed in as either an integer or a string", status=400)


class InvalidCardNumberResponse(HttpResponse):
    def __init__(self):
        super().__init__("`card_number` string does not represent an integer", status=400)


class InvalidIssuerName(HttpResponse):
    def __init__(self):
        super().__init__("A non-empty `issuer` string is required", status=400)