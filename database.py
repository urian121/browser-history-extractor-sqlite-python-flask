import sqlite3
import os
from datetime import datetime
from pathlib import Path

# Ruta de la base de datos
DB_PATH = Path("historial_navegadores.db")

def init_db():
    """Inicializa la base de datos y crea la tabla si no existe"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            navegador TEXT NOT NULL,
            url TEXT NOT NULL,
            titulo TEXT,
            fecha TEXT NOT NULL,
            fecha_extraccion TEXT NOT NULL,
            UNIQUE(navegador, url, fecha)
        )
    """)
    
    # Índices para mejorar las búsquedas
    cur.execute("CREATE INDEX IF NOT EXISTS idx_navegador ON historial(navegador)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fecha ON historial(fecha)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_url ON historial(url)")
    
    conn.commit()
    conn.close()

def save_historial(navegador, datos):
    """Guarda el historial de un navegador en la base de datos"""
    if not datos:
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    fecha_extraccion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insertados = 0
    
    for item in datos:
        try:
            cur.execute("""
                INSERT OR IGNORE INTO historial (navegador, url, titulo, fecha, fecha_extraccion)
                VALUES (?, ?, ?, ?, ?)
            """, (navegador, item['url'], item['titulo'], item['fecha'], fecha_extraccion))
            if cur.rowcount > 0:
                insertados += 1
        except Exception as e:
            print(f"Error insertando registro: {e}")
            continue
    
    conn.commit()
    conn.close()
    return insertados

def get_historial(navegador=None, limite=100):
    """Obtiene el historial de la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    if navegador:
        cur.execute("""
            SELECT navegador, url, titulo, fecha, fecha_extraccion
            FROM historial
            WHERE navegador = ?
            ORDER BY fecha DESC
            LIMIT ?
        """, (navegador, limite))
    else:
        cur.execute("""
            SELECT navegador, url, titulo, fecha, fecha_extraccion
            FROM historial
            ORDER BY fecha DESC
            LIMIT ?
        """, (limite,))
    
    resultados = cur.fetchall()
    conn.close()
    
    return [
        {
            'navegador': r[0],
            'url': r[1],
            'titulo': r[2],
            'fecha': r[3],
            'fecha_extraccion': r[4]
        }
        for r in resultados
    ]

def get_stats():
    """Obtiene estadísticas del historial"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Total de registros
    cur.execute("SELECT COUNT(*) FROM historial")
    total = cur.fetchone()[0]
    
    # Por navegador
    cur.execute("""
        SELECT navegador, COUNT(*) as cantidad
        FROM historial
        GROUP BY navegador
    """)
    por_navegador = {row[0]: row[1] for row in cur.fetchall()}
    
    conn.close()
    
    return {
        'total': total,
        'por_navegador': por_navegador
    }

