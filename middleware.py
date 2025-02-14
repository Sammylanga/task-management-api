import logging
from django.http import JsonResponse

logger = logging.getLogger('django')

class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.error(f"Unhandled Exception: {exception}", exc_info=True)
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)
