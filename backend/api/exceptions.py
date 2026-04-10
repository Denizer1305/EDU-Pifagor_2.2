from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {
                "success": False,
                "message": "Внутренняя ошибка сервера.",
                "errors": None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    detail = response.data

    if isinstance(detail, dict):
        message = detail.get("detail", "Ошибка запроса.")
        errors = detail
    else:
        message = "Ошибка запроса."
        errors = detail

    response.data = {
        "success": False,
        "message": message,
        "errors": errors,
    }
    return response
