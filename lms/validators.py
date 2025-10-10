from rest_framework.exceptions import ValidationError


def validate_youtube_link(value):
    if value and "youtube.com" not in value:
        raise ValidationError("Разрешены ссылки только на youtube.com")
    return value
