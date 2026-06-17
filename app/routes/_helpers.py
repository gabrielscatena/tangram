from __future__ import annotations


def get_container():
    """Return the demo dependency container from current Flask app."""
    from flask import current_app

    return current_app.extensions["tangram_container"]
