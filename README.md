# Extractor de Historial de Navegadores

Aplicación web desarrollada con Flask que extrae y almacena el historial de navegación de Chrome, Edge, Firefox y Opera en una base de datos SQLite.

![Demo](https://raw.githubusercontent.com/urian121/imagenes-proyectos-github/refs/heads/master/browser-history-extractor-sqlite-python-flask.png)

## Características

- Extrae el historial de los últimos 30 días de múltiples navegadores
- Almacena el historial en una base de datos SQLite local
- Interfaz web simple con HTMX para interacciones dinámicas
- Visualización del historial en modales con tablas responsive
- Actualiza registros existentes automáticamente

## Navegadores Soportados

- Google Chrome
- Microsoft Edge
- Mozilla Firefox
- Opera

## Requisitos

- Python 3.7+
- Flask
- SQLite3 (incluido en Python)

## Instalación

```bash
pip install flask
```

## Uso

1. Ejecutar la aplicación:
```bash
python app.py
```

2. Abrir en el navegador: `http://localhost:5000`

3. Hacer clic en "Leer Historial de Navegadores" para extraer y guardar el historial

4. Hacer clic en "Ver Historial" en cada navegador para ver los registros almacenados

## Estructura

- `app.py` - Aplicación Flask principal
- `database.py` - Gestión de base de datos SQLite
- `leer_historial.py` - Extracción de historial de navegadores
- `templates/` - Plantillas HTML (Jinja2)
- `static/` - Archivos CSS y JavaScript
- `historial_navegadores.db` - Base de datos SQLite (se crea automáticamente)

## Notas

- El historial se filtra a los últimos 30 días
- Los registros duplicados se actualizan automáticamente

