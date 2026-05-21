# MiniQL

Lenguaje SQL-like académico para consultar CSV/JSON con un motor propio en Python.

## Ejecutar

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Luego abre http://localhost:8000

## Sintaxis

```sql
OBTENER nombre, edad
DE usuarios
DONDE edad > 18
ORDENAR edad DESC
LIMITE 5
```
