import re
from django.core.exceptions import ValidationError


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            '"me" is invalid username.'
        )
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise ValidationError(
            'The username must consist of letters, digits'
            'and @/./+/-/_ only.'
        )
    return value
