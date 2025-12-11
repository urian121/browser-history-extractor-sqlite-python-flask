from flask import Flask, render_template, jsonify, request
import leer_historial
import database
import traceback

# Crear la aplicación
app = Flask(__name__)

# Inicializar la base de datos al iniciar
database.init_db()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/leer-historial', methods=['POST'])
def leer_historial_endpoint():
    """Endpoint para leer el historial de todos los navegadores y guardarlo en BD"""
    try:
        # Leer historial de todos los navegadores
        resultados = leer_historial.leer_todos_navegadores()
        
        # Guardar en base de datos y mantener orden consistente
        orden_navegadores = ['chrome', 'edge', 'firefox', 'opera']
        resumen = {}
        
        for nav in orden_navegadores:
            info = resultados.get(nav, {})
            datos = info.get("datos", [])
            encontrado = info.get("encontrado", False)
            
            if encontrado and datos and len(datos) > 0:
                try:
                    procesados = database.save_historial(nav, datos)
                    resumen[nav] = {
                        "encontrado": True,
                        "total_leidos": info.get("cantidad", len(datos)),
                        "insertados": procesados
                    }
                except Exception as e:
                    print(f"Error guardando historial de {nav}: {e}")
                    traceback.print_exc()
                    resumen[nav] = {
                        "encontrado": True,
                        "total_leidos": info.get("cantidad", len(datos)),
                        "insertados": 0,
                        "error": str(e)
                    }
            else:
                resumen[nav] = {
                    "encontrado": encontrado,
                    "total_leidos": info.get("cantidad", 0),
                    "insertados": 0
                }
                if "error" in info:
                    resumen[nav]["error"] = info["error"]
        
        # Devolver HTML para HTMX
        return render_template('resultados.html', resumen=resumen)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f'<div class="alert alert-danger">Error al leer historial: {str(e)}</div>', 500


# Endpoint para obtener estadísticas del historial almacenado
@app.route('/api/estadisticas', methods=['GET'])
def estadisticas():
    """Endpoint para obtener estadísticas del historial almacenado"""
    try:
        stats = database.get_stats()
        return jsonify({
            "success": True,
            "estadisticas": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "mensaje": f"Error al obtener estadísticas: {str(e)}"
        }), 500


# Endpoint para obtener el historial almacenado (JSON)
@app.route('/api/historial', methods=['GET'])
def obtener_historial():
    """Endpoint para obtener el historial almacenado en formato JSON"""
    try:
        navegador = request.args.get('navegador', None)
        limite = request.args.get('limite', 100, type=int)
        
        historial = database.get_historial(navegador=navegador, limite=limite)
        return jsonify({
            "success": True,
            "historial": historial,
            "cantidad": len(historial)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "mensaje": f"Error al obtener historial: {str(e)}"
        }), 500


# Endpoint para obtener el historial en formato HTML (modal)
@app.route('/api/historial/modal', methods=['GET'])
def obtener_historial_modal():
    """Endpoint para obtener el historial almacenado en formato HTML para modal"""
    try:
        navegador = request.args.get('navegador', None)
        limite = request.args.get('limite', 100, type=int)
        
        if not navegador:
            return '<div class="alert alert-danger">Navegador no especificado</div>', 400
        
        historial = database.get_historial(navegador=navegador, limite=limite)
        return render_template('modal_historial.html', navegador=navegador, historial=historial)
    except Exception as e:
        return f'<div class="alert alert-danger">Error al obtener historial: {str(e)}</div>', 500


# Correr la aplicación
if __name__ == '__main__':
    app.run(debug=True, port=5000)