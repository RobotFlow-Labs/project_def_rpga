"""Compatibility wrapper for the old scaffold namespace."""

import os

BACKEND = os.environ.get("ANIMA_BACKEND", "auto")


def get_backend() -> str:
    return BACKEND


def get_device() -> str:
    return BACKEND
