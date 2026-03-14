import pytz
from rest_framework import serializers
from django.conf import settings
from django.utils.translation import gettext_lazy as _

def validate_language(value):
    supported_languages = [lang[0] for lang in settings.LANGUAGES]
    if value not in supported_languages:
        # Используем фигурные скобки для .format()
        error_msg = _('language "{value}" is not supported. accessible: {accessible}') 
        raise serializers.ValidationError(
            error_msg.format(
                value=value, 
                accessible=", ".join(supported_languages)
            )    
        )
    return value

def validate_timezone(value):
    if value not in pytz.all_timezones:
        # Используем фигурные скобки для .format()
        error_msg = _('timezone "{value}" is not valid. accessible: {accessible}') 
        raise serializers.ValidationError(
            error_msg.format(
                value=value, 
                accessible="UTC, Asia/Almaty, Europe/Moscow..." # Список слишком длинный, лучше сократить или давать ссылку
            )
        )
    return value