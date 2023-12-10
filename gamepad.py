
import time
from inputs import get_gamepad

def main():
    try:
        while True:
            events = get_gamepad()
            for event in events:
                if event.ev_type == "Key":
                    print("Button {} {}".format(event.code, "pressed" if event.state else "released"))
                elif event.ev_type == "Absolute":
                    print("Axis {} moved to {}".format(event.code, event.state))

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
