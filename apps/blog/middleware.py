from django.utils import timezone,translation
from django.conf import settings

class LanguageQueryMiddleware:
    """Middleware to set language and timezone based on query parameters.
    Query Parameters:
        - lang: Language code to activate (e.g., 'en', 'ru', 'kk').
        - tz: Timezone string to activate (e.g., 'America/New_York', 'Europe/Paris')."""
    def __init__(self,get_response):
        self.get_response = get_response
    
    def __call__(self,request):
        lang_code = request.GET.get("lang")
        supported_languages = [lang[0] for lang in settings.LANGUAGES]

        if lang_code and lang_code in supported_languages:
            with translation.override(lang_code):
                request.LANGUAGE_CODE = lang_code
                return self.get_response(request)
        return self.get_response(request)
           