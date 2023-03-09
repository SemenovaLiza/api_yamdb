import re

from django.core.exceptions import ValidationError


def username_validation(value):
    """Check whether username corresponds to the requirements."""
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise ValidationError(
            'The username must consist of letters, digits'
            'and @/./+/-/_ only.')
    if value == 'me':
        raise ValidationError(
            '"me" is invalid username.')
    return value
