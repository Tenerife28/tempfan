from flask import Flask, render_template, jsonify, request
from time import sleep
import threading
from my_fan_lib import SmartFan, DS18B20Sensor

app = Flask(__name__)

fan = SmartFan()
sensor = DS18B20Sensor()

current_data = {
    "temp": 0,
    "rpm": 0,
    "speed_percent": 0,
    "mode": "AUTO"
}

def fan_control_loop():
    print("Background Control Loop Started...")
    while True:
        try:
            temp = sensor.read_temp()
            current_data["temp"] = temp if temp else 0

            if fan.is_turbo_active():
                target_speed = 1.0
                current_data["mode"] = "TURBO"
            elif fan.auto_mode:
                target_speed = fan.calculate_target_speed(current_data["temp"])
                current_data["mode"] = "AUTO"
            else:
                target_speed = fan.manual_speed
                current_data["mode"] = "MANUAL"

            fan.set_speed(target_speed)
            current_data["speed_percent"] = int(target_speed * 100)

            sleep(1)
            rpm = fan.get_rpm(1)
            current_data["rpm"] = rpm

        except Exception as e:
            print(f"Eroare în loop: {e}")
            sleep(1)

thread = threading.Thread(target=fan_control_loop)
thread.daemon = True
thread.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def get_data():
    return jsonify({
        **current_data, 
        "is_auto": fan.auto_mode,
        "manual_val": fan.manual_speed
    })

@app.route("/api/control", methods=['POST'])
def control_fan():
    data = request.json
    
    if 'auto_mode' in data:
        fan.auto_mode = data['auto_mode']
        print(f"Mod schimbat: {'AUTO' if fan.auto_mode else 'MANUAL'}")
        
    if 'speed' in data:
        fan.manual_speed = float(data['speed']) / 100.0
        print(f"Viteză manuală setată: {fan.manual_speed}")

    if 'turbo' in data and data['turbo'] is True:
        fan.activate_turbo()
        print(">>> TURBO ACTIVAT DIN WEB! <<<")
        
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)