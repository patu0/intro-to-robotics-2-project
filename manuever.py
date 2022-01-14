import sys
sys.path.append(r'/home/bhagatsj/RobotSystems/lib')
from utils import reset_mcu
reset_mcu()

from picarx_improved import Picarx
import time


def k_turn(px, speed):
    px.forward(speed)
    for angle in range(0, 90):
        px.set_dir_servo_angle(angle)
        time.sleep(0.1)

    px.backward(speed)
    for angle in range(90, 0, -1):
        px.set_dir_servo_angle(angle)
        time.sleep(0.1)

    px.forward(speed)
    for angle in range(0, 15):
        px.set_dir_servo_angle(angle)
        time.sleep(0.1)
    for angle in range(15, 0, -1):
        px.set_dir_servo_angle(angle)
        time.sleep(0.1)

    px.forward(0.5)
    px.stop_motors()

def parallel_park(px, speed):
    px.backward(speed)
    for angle in range(0, 35):
        px.set_dir_servo_angle(angle)
        time.sleep(0.1)

    px.forward(speed)
    for angle in range(35, 0, -1):
        px.set_dir_servo_angle(angle)
        time.sleep(0.1)    

    px.backward(speed)
    time.sleep(1)
    px.backward(0)

def forward_and_backwards(px, speed, sleep_time):
    px.forward(speed)
    time.sleep(sleep_time)
    px.backward(speed)
    time.sleep(sleep_time)
    px.backward(0)

if __name__ == "__main__":
    px = Picarx()
    while True:
        print("Please select a manuever:")
        print("\t1: Forwards and Backwards")
        print("\t2: Parallel Park")
        print("\t3: K-Turn")
        print("\t4: End program")
        print()
        option = input("Enter an manuever: ")

        if option == "1":
            forward_and_backwards(px, 50, 3)
        elif option == "2":
            parallel_park(px, 50)
        elif option == "3":
            k_turn(px, 50)
        elif option == "4":
            exit()
        else:
            print()
            print("Error: Invalid Option.")
        



