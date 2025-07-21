from flask import Flask, render_template, Response, jsonify, request
import cv2
import threading
import time
import os
from datetime import datetime
import secrets
from functools import wraps

# --- Configuración de la Aplicación ---
app = Flask(__name__)
# Token de autenticación (se genera uno nuevo cada vez que se inicia la app)
AUTH_TOKEN = secrets.token_urlsafe(32)

# ==============================================================================
# CLASE PARA GESTIONAR LA CÁMARA (Elimina las variables globales)
# ==============================================================================
class CameraManager:
    """
    Encapsula toda la lógica y el estado de la cámara en un solo lugar.
    """
    def __init__(self):
        self.camera = None
        self.recording = False
        self.out = None
        self.frame_lock = threading.Lock()
        self.current_frame = None
        
        # Inicia la cámara al crear el objeto
        if self._init_camera():
            print("✅ Cámara lista")
        else:
            print("⚠️ No se pudo inicializar la cámara")

    def _init_camera(self):
        """Método privado para inicializar la cámara."""
        try:
            for i in range(3): # Intenta diferentes índices
                camera_candidate = cv2.VideoCapture(i)
                if camera_candidate.isOpened():
                    camera_candidate.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    camera_candidate.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    camera_candidate.set(cv2.CAP_PROP_FPS, 30)
                    self.camera = camera_candidate
                    print(f"✅ Cámara inicializada en índice {i}")
                    return True
            return False
        except Exception as e:
            print(f"❌ Error inicializando cámara: {e}")
            return False

    def generate_frames(self):
        """Generador de frames para el stream de video."""
        while True:
            if self.camera is None or not self.camera.isOpened():
                if not self._init_camera():
                    time.sleep(1)
                    continue

            with self.frame_lock:
                success, frame = self.camera.read()

            if not success:
                print("⚠️ No se pudo leer frame de la cámara")
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1) # Efecto espejo

            # Agregar timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Indicador de grabación
            if self.recording:
                cv2.circle(frame, (frame.shape[1] - 30, 30), 10, (0, 0, 255), -1)
                cv2.putText(frame, "REC", (frame.shape[1] - 70, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                if self.out is not None:
                    self.out.write(frame)

            # Codificar frame a JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def start_recording(self):
        """Inicia la grabación de video."""
        if self.recording:
            return False, "Ya está grabando"
        
        try:
            recordings_dir = '/app/recordings'
            os.makedirs(recordings_dir, exist_ok=True)
            filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            filepath = os.path.join(recordings_dir, filename)
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.out = cv2.VideoWriter(filepath, fourcc, 20.0, (640, 480))
            self.recording = True
            
            print(f"▶️ Grabación iniciada: {filename}")
            return True, {"message": "Grabación iniciada", "filename": filename}
        except Exception as e:
            print(f"❌ Error iniciando grabación: {e}")
            return False, {"error": f"Error iniciando grabación: {str(e)}"}

    def stop_recording(self):
        """Detiene la grabación de video."""
        if not self.recording:
            return False, "No está grabando"
            
        self.recording = False
        if self.out is not None:
            self.out.release()
            self.out = None
        
        print("⏹️ Grabación detenida.")
        return True, {"message": "Grabación detenida"}

    def get_status(self):
        """Obtiene el estado actual de la cámara."""
        return {
            "camera_active": self.camera is not None and self.camera.isOpened(),
            "recording": self.recording,
            "timestamp": datetime.now().isoformat()
        }

# ==============================================================================
# DECORADOR PARA AUTENTICACIÓN (Evita repetir código)
# ==============================================================================
# ==============================================================================
# DECORADOR PARA AUTENTICACIÓN (Versión Simplificada para Depuración)
# ==============================================================================
def auth_required(f):
    """
    Decorador que verifica el token de autenticación.
    SOLO busca el token en el parámetro de la URL (?token=...).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token')

        if not token or token != AUTH_TOKEN:
            if request.path.startswith(('/start_recording', '/stop_recording', '/status', '/recordings')):
                 return jsonify({"error": "No autorizado o token inválido"}), 401
            return "❌ No autorizado. Token inválido o no proporcionado.", 401
            
        return f(*args, **kwargs)
    return decorated_function
# ==============================================================================
# INICIALIZACIÓN GLOBAL
# ==============================================================================
# Se crea una única instancia de CameraManager que será usada por toda la app
camera_manager = CameraManager()
print(f"🔑 Token de acceso: {AUTH_TOKEN}")
print(f"🌐 Guarda este token para acceder a la aplicación")

# ==============================================================================
# RUTAS DE LA APLICACIÓN FLASK
# ==============================================================================
@app.route('/')
@auth_required
def index():
    """Página principal (protegida por token)."""
    return render_template('index.html')

@app.route('/video_feed')
@auth_required
def video_feed():
    """Stream de video en tiempo real (protegido)."""
    return Response(camera_manager.generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_recording', methods=['POST'])
@auth_required
def start_recording_route():
    """Ruta para iniciar la grabación."""
    success, response_data = camera_manager.start_recording()
    return jsonify(response_data), 200 if success else 400

@app.route('/stop_recording', methods=['POST'])
@auth_required
def stop_recording_route():
    """Ruta para detener la grabación."""
    success, response_data = camera_manager.stop_recording()
    return jsonify(response_data), 200 if success else 400

@app.route('/status')
@auth_required
def status_route():
    """Ruta para obtener el estado de la aplicación."""
    return jsonify(camera_manager.get_status())

@app.route('/recordings')
@auth_required
def list_recordings():
    """Ruta para listar las grabaciones disponibles."""
    try:
        recordings_dir = '/app/recordings'
        if not os.path.exists(recordings_dir):
            return jsonify({"recordings": []})
        
        recordings_list = []
        for filename in sorted(os.listdir(recordings_dir), reverse=True): # Ordenar por más reciente
            if filename.endswith('.mp4'):
                filepath = os.path.join(recordings_dir, filename)
                recordings_list.append({
                    "filename": filename,
                    "size": os.path.getsize(filepath),
                    "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
        
        return jsonify({"recordings": recordings_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ==============================================================================
# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ==============================================================================
if __name__ == '__main__':
    # Esta función se ejecutará JUSTO ANTES de que Flask empiece a aceptar conexiones.
    def print_access_urls():
        # Un pequeño retraso para que nuestros mensajes aparezcan DESPUÉS de los de Flask.
        time.sleep(1) 
        
        # Obtenemos la IP de Tailscale desde la variable de entorno
        tailscale_ip = os.environ.get('TAILSCALE_IP')

        print("\n" + "="*50)
        print("✅ ¡APLICACIÓN LISTA! ACCEDE DESDE LAS SIGUIENTES URLS:")
        print("="*50)
        print(f"🏠 Local: http://localhost:5000/?token={AUTH_TOKEN}")
        
        if tailscale_ip:
            print(f"🌍 Tailscale: http://{tailscale_ip}:5000/?token={AUTH_TOKEN}")
        
        print("="*50 + "\n")

    print("🚀 Iniciando aplicación de cámara...")
    
    # Iniciamos nuestra función en un hilo para que no bloquee el inicio de Flask.
    threading.Thread(target=print_access_urls).start()
    
    # La aplicación se inicia con el servidor de desarrollo de Flask
    # En un entorno de producción, se usaría un servidor como Gunicorn o uWSGI
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)