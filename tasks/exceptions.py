from rest_framework.views import exception_handler
import logging

logger = logging.getLogger("django")

def custom_exception_handler(exc, context):
    """
    Custom exception handler to log errors and return a proper API response.
    """
    response = exception_handler(exc, context)

    # Log the error
    if response is not None:
        logger.error(f"Exception occurred: {exc}, Context: {context}")

    # Return the standard response if DRF handled it
    if response is not None:
        return response

    # Handle other exceptions not caught by DRF
    return Response({"error": "An unexpected error occurred"}, status=500)
