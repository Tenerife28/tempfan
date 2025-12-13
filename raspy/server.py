from flask import Flask, render_template, jsonify, request
from time import sleep
import threading
from my_fan_lib import SmartFan, DS18B20Sensor

app = Flask(__name__)

# --- OBIECTE GLOBALE ---
fan = SmartFan()
sensor = DS18B20Sensor()

# Variabile pentru a stoca datele curente (ca să le trimitem rapid la site)
current_data = {
    "temp": 0,
    "rpm": 0,
    "speed_percent": 0,
    "mode": "AUTO"
}

# --- LOGICA DE CONTROL (Rulează în fundal) ---
def fan_control_loop():
    print("Background Control Loop Started...")
    while True:
        try:
            # 1. Citim temperatura
            temp = sensor.read_temp()
            current_data["temp"] = temp if temp else 0

            # 2. Decidem viteza
            if fan.is_turbo_active():
                target_speed = 1.0
                current_data["mode"] = "TURBO"
            elif fan.auto_mode:
                # Mod AUTO: Calculăm în funcție de temperatură
                target_speed = fan.calculate_target_speed(current_data["temp"])
                current_data["mode"] = "AUTO"
            else:
                # Mod MANUAL: Luăm valoarea setată din slider
                target_speed = fan.manual_speed
                current_data["mode"] = "MANUAL"

            # 3. Aplicăm viteza fizic
            fan.set_speed(target_speed)
            current_data["speed_percent"] = int(target_speed * 100)

            # 4. Măsurăm RPM (Aici stăm 1 secundă)
            sleep(1)
            rpm = fan.get_rpm(1)
            current_data["rpm"] = rpm

        except Exception as e:
            print(f"Eroare în loop: {e}")
            sleep(1)

# Pornim thread-ul imediat ce pornește serverul
thread = threading.Thread(target=fan_control_loop)
thread.daemon = True # Se oprește când oprim serverul
thread.start()

# --- RUTELE FLASK ---

@app.route("/")
def index():
    return render_template("index.html")

# Ruta 1: Trimite datele către site (GET)
@app.route("/api/data")
def get_data():
    # Returnăm direct ce a calculat thread-ul din spate
    # Adăugăm și starea curentă a setărilor pentru a sincroniza butoanele
    return jsonify({
        **current_data, 
        "is_auto": fan.auto_mode,
        "manual_val": fan.manual_speed
    })

# Ruta 2: Primește comenzi de la site (POST)
@app.route("/api/control", methods=['POST'])
def control_fan():
    data = request.json
    
    if 'auto_mode' in data:
        fan.auto_mode = data['auto_mode']
        print(f"Mod schimbat: {'AUTO' if fan.auto_mode else 'MANUAL'}")
        
    if 'speed' in data:
        # Viteza vine 0-100, noi vrem 0.0-1.0
        fan.manual_speed = float(data['speed']) / 100.0
        print(f"Viteză manuală setată: {fan.manual_speed}")
        
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)