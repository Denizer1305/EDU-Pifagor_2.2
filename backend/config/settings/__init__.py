#!/usr/bin/env python
from __future__ import annotations

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. Вы уверены, что он установлен и "
            "aдоступен в вашей переменной окружения PYTHONPATH? Вы не"
            "забыли активировать виртуальную среду?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
