from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def api_exception_handler(exc, context):
    """Return user-friendly API errors without Python stack traces."""
    response = exception_handler(exc, context)
    if response is not None:
        detail = response.data
        message = detail
        if isinstance(detail, dict):
            message = detail.get("detail", detail)
        return Response(
            {
                "success": False,
                "error_type": "VALIDATION_ERROR"
                if response.status_code == 400
                else "AUTHENTICATION_ERROR"
                if response.status_code in (401, 403)
                else "API_ERROR",
                "message": message,
                "errors": detail,
            },
            status=response.status_code,
        )

    return Response(
        {
            "success": False,
            "error_type": "DATABASE_ERROR",
            "message": "An unexpected server error occurred. Please try again.",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
