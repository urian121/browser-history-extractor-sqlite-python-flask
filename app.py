from flask import Flask, render_template, jsonify, request
import leer_historial
import database

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
        
        # Guardar en base de datos
        total_insertados = 0
        resumen = {}
        
        for nav, info in resultados.items():
            if info["encontrado"] and info["datos"]:
                insertados = database.save_historial(nav, info["datos"])
                total_insertados += insertados
                resumen[nav] = {
                    "encontrado": True,
                    "total_leidos": info["cantidad"],
                    "insertados": insertados
                }
            else:
                resumen[nav] = {
                    "encontrado": info.get("encontrado", False),
                    "total_leidos": 0,
                    "insertados": 0
                }
        
        return jsonify({
            "success": True,
            "mensaje": f"Historial leído y guardado. Total insertados: {total_insertados}",
            "resumen": resumen,
            "total_insertados": total_insertados
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "mensaje": f"Error al leer historial: {str(e)}"
        }), 500


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


@app.route('/api/historial', methods=['GET'])
def obtener_historial():
    """Endpoint para obtener el historial almacenado"""
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


# Correr la aplicación
if __name__ == '__main__':
    app.run(debug=True, port=5000)