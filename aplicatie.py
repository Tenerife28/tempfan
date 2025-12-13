from gpiozero import PWMOutputDevice, Button
from time import sleep, time

sensorFile = '/sys/bus/w1/devices/28-7975a6086461/w1_slave'

pwm=6
tachPin=5
waitTime=1
ppr=2
currentSpeed = 1.0
buton=13
tachCounter=0
turboEndTime = 0

fan = PWMOutputDevice(pwm, frequency=100)
tach= Button(tachPin, pull_up=True, bounce_time=None)
turboButton = Button(buton, pull_up=True, bounce_time=0.1)

MIN_TEMP=15
MAX_TEMP=35
MIN_SPEED=0.2
TURBO_DURATION=30

def calculateSpeed(temp):
    if temp<MIN_TEMP:
        return MIN_SPEED
    if temp>=MAX_TEMP:
        return 1.0
    percentage=(temp-MIN_TEMP)/(MAX_TEMP-MIN_TEMP)
    targetSpeed= MIN_SPEED+(percentage*(1.0-MIN_SPEED))
    return round(targetSpeed,2)

def getTemp():
    try:
        with open(sensorFile, 'r') as f:
            lines = f.readlines()
        if lines[0].strip()[-3:] !='YES':
            return None
        eqPos=lines[1].find('t=')
        if eqPos!=-1:
            tempString=lines[1][eqPos+2:]
            tempC=float(tempString)/1000.00
            return tempC
    except Exception as e:
        print(f"Error reading sensor: {e}")
        return None
def pulseCounter():
    global tachCounter
    tachCounter+=1

def activateTurbo():
    global turboEndTime
    turboEndTime = time() + TURBO_DURATION
    print(f"\n>>> TURBO MODE ACTIVATED! (Max speed for {TURBO_DURATION}s) <<<")

tach.when_pressed = pulseCounter
turboButton.when_pressed = activateTurbo
try:
    print("Smart Fan Controller Started.")
    print(f" - Auto Mode: {MIN_TEMP} *C to {MAX_TEMP} *C")
    print(f" - Turbo Mode: Press button on GPIO {buton}")
    while True:
        currentTemp=getTemp()
        if currentTemp is not None:
            if time() < turboEndTime:
                newSpeed = 1.0
                mode = "TURBO"
                remaining = int(turboEndTime - time())
                mode_info = f"(Time left: {remaining}s)"
            else:
                newSpeed=calculateSpeed(currentTemp)
                mode="AUTO"
                mode_info = ""
            fan.value = newSpeed
            tachCounter=0
            sleep(waitTime)
            rpm=(tachCounter/ppr)*(60/waitTime)
            print(f"[{mode}] Temp: {currentTemp:.1f}C | Speed: {int(newSpeed*100)}% | RPM: {int(rpm)} {mode_info}")
        else:
            print("Sensor Error - Retrying...")
            sleep(1)
except KeyboardInterrupt:
    print("\nStopping...")
    fan.off()