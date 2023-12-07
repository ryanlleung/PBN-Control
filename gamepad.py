
import time
from inputs import get_gamepad

# def main():
#     try:
#         while True:
#             events = get_gamepad()
#             for event in events:
#                 if event.ev_type == "Key":
#                     print("Button {} {}".format(event.code, "pressed" if event.state else "released"))
#                 elif event.ev_type == "Absolute":
#                     print("Axis {} moved to {}".format(event.code, event.state))

#     except KeyboardInterrupt:
#         pass

# if __name__ == "__main__":
#     main()

last_check_time = time.time()
check_interval = 1/60  # Adjust the check interval as needed
last_value = 0  # Initialize the last known value for the analog input

try:
    while True:
        current_time = time.time()
        if current_time - last_check_time >= check_interval:
            last_check_time = current_time

            events = get_gamepad()
            for event in events:
                if event.ev_type == "Absolute" and event.code == "ABS_RZ":
                    if event.state != last_value:
                        last_value = event.state
                        print("Current value for ABS_RZ: {}".format(last_value))

except KeyboardInterrupt:
    pass