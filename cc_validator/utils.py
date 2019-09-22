from typing import List, Union


def generate_iin_fixtures(network_name: str, iin_ranges: List[Union[int, tuple]]) -> List:
    """
    Generate fixture objects required to seed the database

    :param network_name: The name of the issuer network
    :param iin_ranges: The issuer network's identifier ranges (values are either a single value or an inclusive range)
    :return: A list of fixture objects
    """
    iin_objects = []
    for iin_range in iin_ranges:
        if isinstance(iin_range, int):
            iin_objects.append({
                "model": "cc_validator.IIN",
                "fields": {
                  "iin": iin_range,
                  "issuer": network_name,
                }
            })
        elif isinstance(iin_range, tuple):
            for i in range(iin_range[0], iin_range[1]+1):
                iin_objects.append({
                    "model": "cc_validator.IIN",
                    "fields": {
                        "iin": i,
                        "issuer": network_name,
                    }
                })

    return iin_objects
