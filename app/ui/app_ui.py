from __future__ import annotations

import io
import os
from typing import Dict, Optional

import pandas as pd
from nicegui import ui

from app.executor.executor import QueryExecutor, ExecutionError
from app.parser.parser import Parser, ParseError
from app.semantic.validator import SemanticValidator, SemanticError
from app.lexer.lexer import LexError


def build_ui(sources: Dict[str, pd.DataFrame]) -> None:
    ui.dark_mode().enable()
    ui.add_head_html(
        """
        <style>
            body { background-color: #0f1115; color: #e6e6e6; }
            .panel { background: #151922; border: 1px solid #232a36; border-radius: 12px; }
            .title { font-weight: 700; letter-spacing: 0.5px; }
            .muted { color: #9aa4b2; }
            .result-count { font-size: 0.9rem; color: #9aa4b2; }
            .nicegui-textarea textarea { min-height: 220px; font-family: 'Fira Code', monospace; }
        </style>
        """
    )

    ui.label("MiniQL").classes("text-2xl title")
    ui.label("Lenguaje SQL-like académico para CSV/JSON").classes("muted")

    result_table = ui.table(columns=[], rows=[]).classes("w-full")
    result_count = ui.label("").classes("result-count")
    error_label = ui.label("").classes("text-red-400")

    last_result: Dict[str, Optional[pd.DataFrame]] = {"df": None}

    def refresh_file_list() -> None:
        file_list.clear()
        with file_list:
            if not sources:
                ui.label("Sin archivos cargados").classes("muted")
                return
            for name in sources.keys():
                ui.label(name).classes("px-2 py-1 rounded bg-[#1c2230]")

    async def handle_upload(e) -> None:
        filename = e.file.name
        content = await e.file.read()
        buffer = io.BytesIO(content)
        base = os.path.splitext(filename)[0]
        try:
            if filename.lower().endswith(".csv"):
                df = pd.read_csv(buffer)
            elif filename.lower().endswith(".json"):
                df = pd.read_json(buffer)
            else:
                ui.notify("Formato no soportado", color="negative")
                return
            sources[base] = df
            refresh_file_list()
            ui.notify(f"Cargado: {base}", color="positive")
        except Exception as exc:  # pragma: no cover
            ui.notify(f"Error al cargar archivo: {exc}", color="negative")

    def run_query(query_text: str) -> None:
        error_label.text = ""
        if not query_text.strip():
            error_label.text = "Consulta vacía"
            return
        try:
            parsed = Parser(query_text).parse()
            SemanticValidator(sources).validate(parsed)
            df = QueryExecutor(sources).execute(parsed)
        except (LexError, ParseError, SemanticError, ExecutionError) as exc:
            error_label.text = str(exc)
            result_table.columns = []
            result_table.rows = []
            result_count.text = ""
            return

        last_result["df"] = df
        result_table.columns = [
            {"name": c, "label": c, "field": c} for c in df.columns.astype(str)
        ]
        result_table.rows = df.to_dict(orient="records")
        result_count.text = f"Filas: {len(df)}"

    def export_result() -> None:
        df = last_result.get("df")
        if df is None:
            ui.notify("No hay resultados para exportar", color="warning")
            return
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        ui.download(buffer.getvalue(), filename="resultado_miniql.csv")

    with ui.row().classes("w-full gap-4 items-start"):
        with ui.card().classes("panel w-1/5 p-4"):
            ui.label("Archivos").classes("title")
            ui.upload(on_upload=handle_upload, auto_upload=True).props(
                "accept=.csv,.json"
            )
            ui.label("Disponibles").classes("muted")
            file_list = ui.column().classes("gap-2")
            refresh_file_list()

        with ui.card().classes("panel w-2/5 p-4"):
            ui.label("Editor MiniQL").classes("title")
            query_input = ui.textarea(
                value="OBTENER *\nDE archivo",
                placeholder="Escribe tu consulta MiniQL...",
            ).classes("w-full")
            with ui.row().classes("gap-2"):
                ui.button("Ejecutar", on_click=lambda: run_query(query_input.value)).classes(
                    "bg-[#3b82f6]"
                )
                ui.button("Exportar CSV", on_click=export_result).classes(
                    "bg-[#10b981]"
                )
            ui.label("Errores").classes("title")
            error_label

        with ui.card().classes("panel w-2/5 p-4"):
            ui.label("Resultados").classes("title")
            result_count
            result_table
