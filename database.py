import sqlite3
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

# Ruta de la base de datos
DB_PATH = Path("historial_navegadores.db")
_TABLA_INICIALIZADA = False

@contextmanager
def get_connection():
    """Context manager para manejar conexiones a la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Inicializa la base de datos y crea la tabla si no existe"""
    global _TABLA_INICIALIZADA
    if _TABLA_INICIALIZADA:
        return
    
    with get_connection() as conn:
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
    
    _TABLA_INICIALIZADA = True

def save_historial(navegador, datos):
    """Guarda el historial de un navegador en la base de datos, actualizando si ya existe"""
    if not datos:
        return 0
    
    # Asegurar que la tabla existe
    init_db()
    
    fecha_extraccion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Filtrar y preparar datos válidos
    datos_validos = [
        (navegador, item.get('url', ''), item.get('titulo', ''), item.get('fecha', ''), fecha_extraccion)
        for item in datos
        if item.get('url') and item.get('fecha')
    ]
    
    if not datos_validos:
        return 0
    
    procesados = 0
    errores = 0
    
    with get_connection() as conn:
        cur = conn.cursor()
        
        # Usar UPSERT (INSERT ... ON CONFLICT DO UPDATE) para mejor rendimiento
        # Esto elimina la necesidad de hacer SELECT por cada registro
        for datos_item in datos_validos:
            try:
                cur.execute("""
                    INSERT INTO historial (navegador, url, titulo, fecha, fecha_extraccion)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(navegador, url, fecha) 
                    DO UPDATE SET 
                        titulo = excluded.titulo,
                        fecha_extraccion = excluded.fecha_extraccion
                """, datos_item)
                procesados += 1
            except Exception as e:
                errores += 1
                print(f"Error procesando registro de {navegador}: {e}")
                continue
    
    if errores > 0:
        print(f"{navegador}: {procesados} procesados, {errores} errores")
    else:
        print(f"{navegador}: {procesados} procesados")
    
    return procesados

def get_historial(navegador=None, limite=100):
    """Obtiene el historial de la base de datos"""
    init_db()
    
    with get_connection() as conn:
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
    init_db()
    
    with get_connection() as conn:
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
    
    return {
        'total': total,
        'por_navegador': por_navegador
    }
