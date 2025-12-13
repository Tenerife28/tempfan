from gpiozero import PWMOutputDevice, Button
from time import sleep, time
import os

# --- Clasa Senzor ---
class DS18B20Sensor:
    def __init__(self, sensor_address):
        base_dir = '/sys/bus/w1/devices/'
        self.sensor_file = os.path.join(base_dir, sensor_address, 'w1_slave')

    def read_temp(self):
        try:
            with open(self.sensor_file, 'r') as f:
                lines = f.readlines()
            if lines[0].strip()[-3:] != 'YES':
                return None
            eq_pos = lines[1].find('t=')
            if eq_pos != -1:
                return float(lines[1][eq_pos+2:]) / 1000.00
            return None
        except Exception as e:
            return None

# --- Clasa Ventilator ---
class SmartFan:
    def __init__(self, pwm_pin, tach_pin, ppr=4, min_temp=15, max_temp=35, min_speed=0.2):
        self.pwm_device = PWMOutputDevice(pwm_pin, frequency=100)
        self.tach_button = Button(tach_pin, pull_up=True, bounce_time=None)
        
        # Parametri
        self.ppr = ppr
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.min_speed = min_speed
        
        # Stare internă
        self._tach_counter = 0
        self.turbo_end_time = 0
        self.current_speed_val = 0.0
        
        self.tach_button.when_pressed = self._pulse_callback

    def _pulse_callback(self):
        self._tach_counter += 1

    def activate_turbo(self, duration=30):
        self.turbo_end_time = time() + duration
        print(f"\n>>> TURBO MODE ACTIVATED! ({duration}s) <<<")

    def is_turbo_active(self):
        return time() < self.turbo_end_time

    def get_turbo_remaining(self):
        return int(max(0, self.turbo_end_time - time()))

    def calculate_target_speed(self, temp):
        if temp < self.min_temp: return self.min_speed
        if temp >= self.max_temp: return 1.0
        percentage = (temp - self.min_temp) / (self.max_temp - self.min_temp)
        return round(self.min_speed + (percentage * (1.0 - self.min_speed)), 2)

    def set_speed(self, speed):
        self.current_speed_val = max(0.0, min(1.0, speed))
        self.pwm_device.value = self.current_speed_val

    def get_rpm(self, elapsed_seconds):
        if elapsed_seconds <= 0: return 0
        rpm = (self._tach_counter / self.ppr) * (60 / elapsed_seconds)
        self._tach_counter = 0
        return int(rpm)
    
    def stop(self):
        self.pwm_device.off()

# --- CLASA CONTROLLER (Aici sunt field-urile cerute) ---
class FanController:
    def __init__(self):
        # AICI AM BĂGAT SETĂRILE CA FIELD-URI
        self.sensor_id = '28-7975a6086461'
        self.pin_pwm = 6
        self.pin_tach = 5
        self.pin_button = 13
        self.wait_time = 1
        
        # Inițializare componente folosind field-urile de mai sus
        self.sensor = DS18B20Sensor(self.sensor_id)
        self.fan = SmartFan(self.pin_pwm, self.pin_tach)
        self.turbo_btn = Button(self.pin_button, pull_up=True, bounce_time=0.1)
        
        # Legare buton turbo
        self.turbo_btn.when_pressed = lambda: self.fan.activate_turbo(30)

    def run(self):
        """Bucla principală a programului"""
        print("Smart Fan Controller Started.")
        print(f" - Configurat pe PWM Pin: {self.pin_pwm}")
        
        try:
            while True:
                temp = self.sensor.read_temp()
                
                if temp is not None:
                    if self.fan.is_turbo_active():
                        self.fan.set_speed(1.0)
                        mode = "TURBO"
                        extra = f"(Left: {self.fan.get_turbo_remaining()}s)"
                    else:
                        target = self.fan.calculate_target_speed(temp)
                        self.fan.set_speed(target)
                        mode = "AUTO"
                        extra = ""

                    # Folosim field-ul wait_time pentru pauză
                    sleep(self.wait_time)
                    rpm = self.fan.get_rpm(self.wait_time)

                    print(f"[{mode}] Temp: {temp:.1f}C | Speed: {int(self.fan.current_speed_val*100)}% | RPM: {rpm} {extra}")
                else:
                    print("Eroare citire senzor...")
                    sleep(1)
        except KeyboardInterrupt:
            print("\nOprire...")
            self.fan.stop()

# ==========================================
# Execuție
# ==========================================
if __name__ == "__main__":
    app = FanController()
    app.run()