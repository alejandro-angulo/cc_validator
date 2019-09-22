cc_validator
============

cc_validator is a Django app meant to validate and generate credit/debit card numbers.

Quick Start
===========
0. Install `cc_validator` from the github repository
    `pip install git+https://github.com/vacuus/cc_validator`.

1. Add `cc_validator` to your `INSTALLED_APPS` setting like this:
    ```python
    INSTALLED_APPS: [
        # ...
        'cc_validator',
        # ...
    ]
    ```

2. Include the `cc_validator` URLconf in your project `urls.py` like
    this:
    ```python
    # ...
    from django.urls import include, path

    #...
    urlpatterns = [
        # ...
        path('cc_validator/', include('cc_validator.urls', namespace="cc_validator")),
        # ...
    ]
    ```

3. Run `python manage.py makemigrations cc_validator` to create the
    migrations and `python manage.py migrate cc_validator` to apply the
    migrations.

4. Seed the database with some initial data by loading the fixtures
    ```bash
    python manage.py loaddata cc_validator/major_industries.json
    python manage.py loaddata cc_validator/issuers.json
    python manage.py loaddata cc_validator/iins.json
    ```    
    **Note: It's important to load `cc_validators/issuers.json` before
    `cc_validators/iins.json`. The latter depends on the former.**

5. You're ready to use the app! Go ahead and run `python manage.py 
    runserver`. See below for more information on the endpoints.

Validating Card Numbers
=======================
A POST request can be made to the `validate_card` endpoint to validate a
card number. If the quick start instructions above were followed, the
path would be `/cc_validator/validate_card`. 

The POST request must have a JSON body with a `card_number` key. The
value can be either an integer or a string.

```JSON
{
  "card_number": "123"
}
```

**Note: If a project has the `CsrfViewMiddleware` middleware enabled,
a CSRF token will also be required in the request.**

The response of the `validate_card` will be a JSON string. The contents 
of the response depends on whether the passed in card number was valid.
If the number was not valid, the response will include a reason for
validation failing. Below is a sample response for an invalid number
(assuming an integer or valid string was sent for the `card_number`
value):

```JSON
{
    "is_valid": false,
    "reason": "Check digit is not valid"
}
```

A valid card number will not return a `reason` key, but will have other
information. Below is a sample request and response for a valid number:

```JSON
{
	"card_number": "5555555555554444"
}
```

which results in the following output

```JSON
{
    "is_valid": true,
    "mii_digit": 5,
    "issuer_category": "Banking and financial",
    "iin": 555555,
    "issuing_network": "Mastercard",
    "account_number": 555555444,
    "check_digit": 4
}
```

- `mii_digit` refers to the Major Industry Identifier (MII)
- `issuer_category` refers to the MII's corresponding issuer category
- `iin` refers to the Issuer Identifier Number (IIN)
- `issuing_network` refers to the issuer's network name (e.g. Visa,
    Mastercard, American Express, Discover Crd, etc.)
- `account_number` refers to the personal account number
- `check_digit` refers to the Luhn Algorithm's check digit (the last
    digit in the card number)
 


Generating Card Numbers
=======================
A GET request can be made to the `generate_card` endpoint to generate a
random card number for a specific issuer network. If the quick start
instructions above were followed, the path would be
`cc_validator/generate_card`.

The GET request must include an `issuer` parameter with its value set to
a valid issuer network name (see below for information regarding
recognized issuers).

The response will include a JSON string with a `generation_success` key.
If `generation_success` is true, a `card_number` key will also be
present with the generated card number. Otherwise, a `reason` key will
indicate what went wrong while generating the card number.

Below are sample responses;

Failed Generation
```JSON
{
    "reason": "Card issuer is not recognized",
    "generation_success": false
}
```

Successful Generation
```JSON
{
    "card_number": 24568956674695410,
    "generation_success": true
}
```

Recognized Issuers
==================
By default only `American Express`, `Visa`, `Mastercard`, and
`Discover Card` are recognized issuers. There is currently no exposed
functionality for end users to update what issuers are recognized.

Additional issuers can be added by inserting records into the `Issuer`
model's corresponding database table. The only required information is a
network name and a comma-delimited list of valid lengths (not all
issuers accept a contiguous range of lengths). In addition, the `IIN`
model's corresponding database table must also have records referencing
`Issuer` records. The `iin` for an `IIN` object refers to the `IIN`
range for an issuer. For example, Visa's IIN is 4 so all numbers 
beginning with 4 are recognized to be issued by Visa. Similarly, there
exist IIN records for the range 622126 - 622925 referencing the Discover
Card network.

Additional Reading
==================
The links below provide additional information on card numbers

- [The Luhn Algorithm](https://en.wikipedia.org/wiki/Luhn_algorithm) is
    used to validate card numbers.
- [ISO/IEC 7812](https://en.wikipedia.org/wiki/ISO/IEC_7812) provides an
    international standard for card numbers
- The table [here](https://en.wikipedia.org/wiki/Payment_card_number#Issuer_identification_number_(IIN))
    provides IIN ranges for additional issuing networks.

