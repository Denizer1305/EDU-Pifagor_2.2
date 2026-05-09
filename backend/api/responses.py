from __future__ import annotations

from rest_framework.response import Response


def success_response(
    data=None, message: str = "Успешно.", status_code: int = 200
) -> Response:
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status_code,
    )


def error_response(
    errors=None, message: str = "Ошибка.", status_code: int = 400
) -> Response:
    return Response(
        {
            "success": False,
            "message": message,
            "errors": errors,
        },
        status=status_code,
    )
