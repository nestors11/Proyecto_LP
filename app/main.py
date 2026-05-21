from __future__ import annotations

from fastapi import FastAPI

from app.ui.app_ui import build_ui


app = FastAPI()

sources = {}

# Vincula NiceGUI con FastAPI
from nicegui import ui  # noqa: E402


@ui.page("/")
def index() -> None:
	build_ui(sources)


ui.run_with(app)
