import os
import sqlite3
import shutil
import platform
from pathlib import Path
from datetime import datetime, timedelta

# -------------------------
# Paths
# -------------------------
def get_os():
    """Detecta el sistema operativo"""
    return platform.system()

def chromium_path(app, vendor):
    """Busca el historial de navegadores basados en Chromium"""
    os_type = get_os()
    
    if os_type == "Windows":
        base = Path(os.getenv("LOCALAPPDATA") or "") / vendor / app / "User Data"
    elif os_type == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support" / vendor / app
    else:  # Linux
        if vendor == "Google" and app == "Chrome":
            base = Path.home() / ".config" / "google-chrome"
        elif vendor == "Microsoft" and app == "Edge":
            base = Path.home() / ".config" / "microsoft-edge"
        else:
            base = Path.home() / ".config" / app.lower()
    
    for p in ["Default"] + [f"Profile {i}" for i in range(10)]:
        h = base / p / "History"
        if h.exists():
            return str(h)
    return None


def opera_path():
    """Busca el historial de Opera/Opera GX"""
    os_type = get_os()
    
    if os_type == "Windows":
        base = Path(os.getenv("APPDATA") or "") / "Opera Software"
    elif os_type == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support" / "com.operasoftware.Opera"
    else:  # Linux
        base = Path.home() / ".config" / "opera"
    
    posibles = [
        "Opera Stable",
        "Opera GX Stable",
        "Opera",
        "Opera GX"
    ]
    
    for carpeta in posibles:
        h = base / carpeta / "History"
        if h.exists():
            return str(h)
    
    # En Linux, Opera puede estar directamente en .config/opera
    if os_type == "Linux":
        h = base / "History"
        if h.exists():
            return str(h)
    
    return None


def firefox_path():
    """Busca el historial de Firefox"""
    os_type = get_os()
    
    if os_type == "Windows":
        appdata = Path(os.getenv("APPDATA") or "") / "Mozilla" / "Firefox" / "Profiles"
    elif os_type == "Darwin":  # macOS
        appdata = Path.home() / "Library" / "Application Support" / "Firefox" / "Profiles"
    else:  # Linux
        appdata = Path.home() / ".mozilla" / "firefox"
    
    if not appdata.exists():
        return None
    
    for perfil in appdata.iterdir():
        if perfil.is_dir() and (perfil / "places.sqlite").exists():
            return str(perfil / "places.sqlite")
    return None


def brave_path():
    """Busca el historial de Brave (bonus)"""
    os_type = get_os()
    
    if os_type == "Windows":
        base = Path(os.getenv("LOCALAPPDATA") or "") / "BraveSoftware" / "Brave-Browser" / "User Data"
    elif os_type == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support" / "BraveSoftware" / "Brave-Browser"
    else:  # Linux
        base = Path.home() / ".config" / "BraveSoftware" / "Brave-Browser"
    
    for p in ["Default"] + [f"Profile {i}" for i in range(10)]:
        h = base / p / "History"
        if h.exists():
            return str(h)
    return None


# -------------------------
# Utils
# -------------------------
def copy_db(ruta):
    temp = ruta + ".tmp"
    try:
        shutil.copy2(ruta, temp)
        return temp
    except Exception:
        return None

def safe_ts_chromium(ts):
    try:
        if ts is None or ts <= 0:
            return "N/A"
        base = datetime(1601, 1, 1).timestamp()
        unix = base + ts / 1_000_000
        if unix < 0 or unix > 32503680000:
            return "N/A"
        return datetime.fromtimestamp(unix).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "N/A"

# -------------------------
# Lectores
# -------------------------
def read_chromium(ruta):
    tmp = copy_db(ruta)
    if not tmp:
        print("No pude copiar el archivo (¿navegador abierto?).")
        return []

    try:
        conn = sqlite3.connect(tmp)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(urls)")
        cols = [c[1] for c in cur.fetchall()]
        need = ["url", "title", "last_visit_time"]
        if not all(c in cols for c in need):
            print("La tabla urls no tiene las columnas necesarias.")
            return []

        cur.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 3000")
        rows = cur.fetchall()

        # límite en formato Chromium (microsegundos desde 1601)
        limite_dt = datetime.now() - timedelta(days=30)
        base = datetime(1601, 1, 1)
        limite_ts = int((limite_dt - base).total_seconds() * 1_000_000)

        datos = []
        for url, title, ts in rows:
            if not ts or ts <= 0:
                continue
            if ts < limite_ts:
                continue
            fecha = safe_ts_chromium(ts)
            datos.append({"url": url or "", "titulo": title or "", "fecha": fecha})
        return datos
    except Exception as e:
        print("Error leyendo Chromium DB:", e)
        return []
    finally:
        try:
            conn.close()
        except:
            pass
        try:
            os.remove(tmp)
        except:
            pass

def read_firefox(ruta):
    tmp = copy_db(ruta)
    if not tmp:
        print("No pude copiar places.sqlite (¿Firefox abierto?).")
        return []

    try:
        conn = sqlite3.connect(tmp)
        cur = conn.cursor()

        # límite en microsegundos unix
        limite = int((datetime.now() - timedelta(days=30)).timestamp() * 1_000_000)

        cur.execute("""
            SELECT p.url, p.title, hv.visit_date
            FROM moz_places p
            JOIN moz_historyvisits hv ON p.id = hv.place_id
            WHERE hv.visit_date >= ?
            ORDER BY hv.visit_date DESC
            LIMIT 2000
        """, (limite,))
        rows = cur.fetchall()

        datos = []
        for url, title, visit_date in rows:
            if not visit_date:
                continue
            try:
                ts = visit_date / 1_000_000
                fecha = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                fecha = "N/A"
            datos.append({"url": url or "", "titulo": title or "", "fecha": fecha})
        return datos
    except Exception as e:
        print("Error leyendo Firefox DB:", e)
        return []
    finally:
        try:
            conn.close()
        except:
            pass
        try:
            os.remove(tmp)
        except:
            pass

# -------------------------
# Guardar
# -------------------------
def save_txt(nav, datos):
    nombre = f"historial_{nav}.txt"
    with open(nombre, "w", encoding="utf-8") as f:
        for d in datos:
            f.write(f"{d['fecha']} - {d['url']} - {d['titulo']}\n")
    print(f"Guardado en {nombre}")

# -------------------------
# Función para Flask
# -------------------------
def leer_todos_navegadores():
    """Lee el historial de todos los navegadores y retorna un diccionario con los resultados"""
    resultados = {
        "chrome": {"encontrado": False, "ruta": None, "datos": [], "cantidad": 0},
        "edge": {"encontrado": False, "ruta": None, "datos": [], "cantidad": 0},
        "firefox": {"encontrado": False, "ruta": None, "datos": [], "cantidad": 0},
        "opera": {"encontrado": False, "ruta": None, "datos": [], "cantidad": 0},
    }
    
    navegadores = {
        "chrome": chromium_path("Chrome", "Google"),
        "edge": chromium_path("Edge", "Microsoft"),
        "opera": opera_path(),
        "firefox": firefox_path(),
    }
    
    for nav, ruta in navegadores.items():
        if not ruta:
            continue
        
        resultados[nav]["encontrado"] = True
        resultados[nav]["ruta"] = ruta
        
        try:
            if nav == "firefox":
                datos = read_firefox(ruta)
            else:
                datos = read_chromium(ruta)
            
            resultados[nav]["datos"] = datos
            resultados[nav]["cantidad"] = len(datos)
        except Exception as e:
            resultados[nav]["error"] = str(e)
    
    return resultados

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    print(f"Sistema operativo detectado: {get_os()}")
    print("=" * 50)
    
    navegadores = {
        "chrome": chromium_path("Chrome", "Google"),
        "edge":   chromium_path("Edge", "Microsoft"),
        "brave":  brave_path(),
        "opera":  opera_path(),
        "firefox": firefox_path(),
    }

    for nav, ruta in navegadores.items():
        print(f"\n=== {nav.upper()} ===")
        if not ruta:
            print("No encontrado.")
            continue

        print("Ruta:", ruta)
        if nav == "firefox":
            datos = read_firefox(ruta)
        else:
            datos = read_chromium(ruta)

        print("Encontrados:", len(datos))
        save_txt(nav, datos)