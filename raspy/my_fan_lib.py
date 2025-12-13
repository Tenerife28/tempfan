from gpiozero import PWMOutputDevice, Button
from time import sleep, time
import os

# --- ZONA DE CONFIGURARE (Aici modifici tot) ---
class Config:
    SENSOR_ID = '28-7975a6086461'
    PIN_PWM = 6
    PIN_TACH = 5
    PIN_BUTTON = 13
    
    PPR = 4           # Corecție pentru RPM
    WAIT_TIME = 1
    
    MIN_TEMP = 15
    MAX_TEMP = 35
    MIN_SPEED = 0.2
    TURBO_DURATION = 30

# --- Clasa Senzor (Fără parametri) ---
class DS18B20Sensor:
    def __init__(self):
        # Își ia singur adresa din Config
        base_dir = '/sys/bus/w1/devices/'
        self.sensor_file = os.path.join(base_dir, Config.SENSOR_ID, 'w1_slave')

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
        except Exception:
            return None

# --- Clasa Ventilator (Fără parametri) ---
# --- Clasa Ventilator ---
class SmartFan:
    def __init__(self):
        self.pwm_device = PWMOutputDevice(Config.PIN_PWM, frequency=100)
        self.tach_button = Button(Config.PIN_TACH, pull_up=True, bounce_time=None)
        
        self.ppr = Config.PPR
        self.min_temp = Config.MIN_TEMP
        self.max_temp = Config.MAX_TEMP
        self.min_speed = Config.MIN_SPEED
        
        self._tach_counter = 0
        self.turbo_end_time = 0
        self.current_speed_val = 0.0
        
        # --- MODIFICĂRI NOI ---
        self.auto_mode = True  # True = Auto (temp), False = Manual (slider)
        self.manual_speed = 0.5 # Viteza default pentru manual (50%)
        # ---------------------

        self.tach_button.when_pressed = self._pulse_callback

    # ... RESTUL METODELOR RĂMÂN NESCHIMBATE ...
    # (Păstrează _pulse_callback, activate_turbo, set_speed, get_rpm, etc.)
    
    def _pulse_callback(self):
        self._tach_counter += 1

    def activate_turbo(self):
        duration = Config.TURBO_DURATION
        self.turbo_end_time = time() + duration

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

# --- CLASA CONTROLLER (Fără parametri) ---
class FanController:
    def __init__(self):
        # Nu mai primim nimic, instanțiem direct
        self.fan = SmartFan()       # Se creează singur cu setările din Config
        self.sensor = DS18B20Sensor() # Se creează singur cu setările din Config
        
        self.wait_time = Config.WAIT_TIME
        
        self.turbo_btn = Button(Config.PIN_BUTTON, pull_up=True, bounce_time=0.1)
        self.turbo_btn.when_pressed = lambda: self.fan.activate_turbo()

    def run(self):
        print("Smart Fan Controller Started.")
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

                    sleep(self.wait_time)
                    rpm = self.fan.get_rpm(self.wait_time)

                    print(f"[{mode}] Temp: {temp:.1f}C | Speed: {int(self.fan.current_speed_val*100)}% | RPM: {rpm} {extra}")
                else:
                    print("Eroare citire senzor...")
                    sleep(1)
        except KeyboardInterrupt:
            print("\nOprire...")
            self.fan.stop()