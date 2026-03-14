from __future__ import annotations

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from django.conf import settings
from django.utils import timezone, translation

class LanguageTimezoneMiddleware:
    """
    Middleware для установки языка и часового пояса.
    Приоритет языка: Profile -> Query Param -> Accept-Language Header -> Default.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.supported_languages = set(code for code, _ in settings.LANGUAGES)

    def __call__(self, request):
        # 1. Определяем и активируем язык
        language = self._resolve_language(request)
        translation.activate(language)
        request.LANGUAGE_CODE = language

        # 2. Определяем и активируем таймзону
        self._activate_timezone(request)

        response = self.get_response(request)

        # Устанавливаем заголовок ответа для клиента
        response["Content-Language"] = language

        # Деактивируем перевод после формирования ответа (чистка потока)
        translation.deactivate()
        return response

    def _resolve_language(self, request) -> str:
        """Логика определения языка с учетом приоритетов."""
        # Приоритет 1: Настройки в профиле пользователя
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            user_language = getattr(user, "preferred_language", None)
            if user_language in self.supported_languages:
                return user_language

        # Приоритет 2: Параметр в URL (?lang=)
        query_lang = request.GET.get("lang")
        if query_lang in self.supported_languages:
            return query_lang

        # Приоритет 3: HTTP заголовок Accept-Language
        header_lang = translation.get_language_from_request(request)
        if header_lang in self.supported_languages:
            return header_lang

        # Приоритет 4: Язык по умолчанию из настроек
        return settings.LANGUAGE_CODE

    def _activate_timezone(self, request) -> None:
        """Логика активации часового пояса."""
        user = getattr(request, "user", None)
        tz_name = "UTC"

        if user and user.is_authenticated:
            # Пытаемся получить зону из профиля
            user_tz = getattr(user, "timezone", None)
            if user_tz:
                tz_name = user_tz

        try:
            # Активируем временную зону через zoneinfo
            current_tz = ZoneInfo(tz_name)
            timezone.activate(current_tz)
            request.activated_timezone = tz_name
        except (ZoneInfoNotFoundError, ValueError, TypeError):
            # Откат на UTC при любой ошибке в названии зоны
            timezone.activate(ZoneInfo("UTC"))
            request.activated_timezone = "UTC"