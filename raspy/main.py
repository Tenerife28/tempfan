from my_fan_lib import FanController

if __name__ == "__main__":
    try:
        app = FanController()
        app.run()
        
    except KeyboardInterrupt:
        print("\nProgram oprit de utilizator.")