#!/usr/bin/env python3
# Copyright 2019 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
# 
# You may not use this file except in compliance with the terms and conditions 
# set forth in the accompanying LICENSE.TXT file.
#
# THESE MATERIALS ARE PROVIDED ON AN "AS IS" BASIS. AMAZON SPECIFICALLY DISCLAIMS, WITH 
# RESPECT TO THESE MATERIALS, ALL WARRANTIES, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.

import os
import sys
import time
import logging
import json
import random
import threading

from enum import Enum
from agt import AlexaGadget

from ev3dev2.led import Leds
from ev3dev2.sound import Sound
from ev3dev2.motor import OUTPUT_B, OUTPUT_C, SpeedPercent, LargeMotor, MoveTank

# Set the logging level to INFO to see messages from AlexaGadget
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))
logger = logging.getLogger(__name__)

SemaphoreSpeed=20

class Direction(Enum):
    """
    The list of directional commands and their variations.
    These variations correspond to the skill slot values.
    """
    FORWARD = ['forward', 'forwards', 'go forward']
    BACKWARD = ['back', 'backward', 'backwards', 'go backward']
    LEFT = ['left', 'go left']
    RIGHT = ['right', 'go right']
    STOP = ['stop', 'brake']

class Position(Enum):
    """
    the list of flag semaphore positions and their respective variation
    these variations correspond to the skill slot value
    """
    A=['a','alfa']
    B=['b','bravo']
    C=['c','charlie']
    D=['d','delta']
    E=['e','echo']
    F=['f','foxtro']
    G=['g','golf']
    H=['h','hotel']
    I=['i','india']
    J=['j','juliett']
    K=['k','kilo']
    L=['l','lima']
    M=['m','mike']
    N=['n','november']
    O=['o','oscar']
    P=['p','papa']
    Q=['q','quebec']
    R=['r','romeo']
    S=['s','sierra']
    T=['t','tango']
    U=['u','uniform']
    V=['v','victor']
    W=['w','whisky']
    X=['x','x-ray']
    Y=['y','yankee']
    Z=['z','zulu']

class Command(Enum):
    """
    The list of preset commands and their invocation variation.
    These variations correspond to the skill slot values.
    """
    MOVE_CIRCLE = ['circle', 'spin']
    MOVE_SQUARE = ['square']
    PATROL = ['patrol', 'guard mode', 'sentry mode']
    FIRE_ONE = ['cannon', '1 shot', 'one shot']
    FIRE_ALL = ['all shot']


class MindstormsGadget(AlexaGadget):
    """
    A Mindstorms gadget that performs movement based on voice commands.
    Two types of commands are supported, directional movement and preset.
    """

    def __init__(self):
        """
        Performs Alexa Gadget initialization routines and ev3dev resource allocation.
        """
        super().__init__()

        # Gadget state
        self.patrol_mode = False

        # Ev3dev initialization
        self.leds = Leds()
        self.sound = Sound()
        self.left_motor = LargeMotor(OUTPUT_B)
        self.right_motor = LargeMotor(OUTPUT_C)
        """homing"""
        """self.right_motor.on_to_position(SemaphoreSpeed,0)"""
        """self.left_motor.on_to_position(SemaphoreSpeed,0)"""
        """self.drive = MoveTank(OUTPUT_B, OUTPUT_C)"""
        """self.weapon = MediumMotor(OUTPUT_A)"""

        # Start threads
        threading.Thread(target=self._patrol_thread, daemon=True).start()

    def on_connected(self, device_addr):
        """
        Gadget connected to the paired Echo device.
        :param device_addr: the address of the device we connected to
        """
        self.leds.set_color("LEFT", "GREEN")
        self.leds.set_color("RIGHT", "GREEN")
        logger.info("{} connected to Echo device".format(self.friendly_name))

    def on_disconnected(self, device_addr):
        """
        Gadget disconnected from the paired Echo device.
        :param device_addr: the address of the device we disconnected from
        """
        self.leds.set_color("LEFT", "BLACK")
        self.leds.set_color("RIGHT", "BLACK")
        logger.info("{} disconnected from Echo device".format(self.friendly_name))

    def on_custom_mindstorms_gadget_control(self, directive):
        """
        Handles the Custom.Mindstorms.Gadget control directive.
        :param directive: the custom directive with the matching namespace and name
        """
        try:
            payload = json.loads(directive.payload.decode("utf-8"))
            print("Control payload: {}".format(payload), file=sys.stderr)
            control_type = payload["type"]
            if control_type == "move":
                print("if control_ype=='move'")
                # Expected params: [direction, duration, speed]
                self._move(payload["direction"], int(payload["duration"]), int(payload["speed"]))

            if control_type == "command":
                # Expected params: [command]
                self._activate(payload["command"])

            if control_type=="position":
                #expercted params: [position]
                self._flagpostion(payload["position"])

        except KeyError:
            print("Missing expected parameters: {}".format(directive), file=sys.stderr)

    def _move(self, direction, duration: int, speed: int, is_blocking=False):
        """
        Handles move commands from the directive.
        Right and left movement can under or over turn depending on the surface type.
        :param direction: the move direction
        :param duration: the duration in seconds
        :param speed: the speed percentage as an integer
        :param is_blocking: if set, motor run until duration expired before accepting another command
        """
        print("Move command: ({}, {}, {}, {})".format(direction, speed, duration, is_blocking), file=sys.stderr)
        if direction in Direction.FORWARD.value:
            """self.drive.on_for_seconds(SpeedPercent(speed), SpeedPercent(speed), duration, block=is_blocking)"""
            """self.COMMAND_RUN_TO_ABS_POS(80)"""
            """self.right_motor.run_to_abs_pos(position_sp = 30)"""
            """0to180 CCW"""
            self.right_motor.on_to_position(SemaphoreSpeed,duration)
            """0to180 CW"""
            self.left_motor.on_to_position(SemaphoreSpeed,duration)
            print("direction:{}, Direction.Forward.value: {}".format(direction,Direction.FORWARD.value),file=sys.stderr)

        if direction in Direction.BACKWARD.value:
            """self.drive.on_for_seconds(SpeedPercent(-speed), SpeedPercent(-speed), duration, block=is_blocking)"""
            """use duration as degree for testing"""
            """aka when say move forward 20 sec is actually setting to 20 tacho turn"""
            self.right_motor.on_to_position(SemaphoreSpeed,duration)

        if direction in (Direction.RIGHT.value + Direction.LEFT.value):
            self._turn(direction, speed)
            """self.drive.on_for_seconds(SpeedPercent(speed), SpeedPercent(speed), duration, block=is_blocking)"""

        if direction in Direction.STOP.value:
            """self.drive.off()"""
            self.patrol_mode = False  
    
    def _flagpostion(self,position, speed=SemaphoreSpeed):
        """
        handles flag position
        """
        print("flag position position[0].lower():{},Position.A.value[0].lower():{}".format(position[0].lower(),Position.A.value[0].lower()),file=sys.stderr)
        if position[0].lower() in Position.A.value[0]:            
            self.right_motor.on_to_position(speed,135)
            self.left_motor.on_to_position(speed,180)
        if position[0].lower() in Position.B.value[0]:            
            self.right_motor.on_to_position(speed,90)
            self.left_motor.on_to_position(speed,180)
        if position[0].lower() in Position.C.value[0]:            
            self.right_motor.on_to_position(speed,45)
            self.left_motor.on_to_position(speed,180)
        if position[0].lower() in Position.D.value[0]:            
            self.right_motor.on_to_position(speed,0)
            self.left_motor.on_to_position(speed,180)
        if position[0].lower() in Position.E.value[0]:            
            self.right_motor.on_to_position(speed,180)
            self.left_motor.on_to_position(speed,45)
        if position[0].lower() in Position.F.value[0]:            
            self.right_motor.on_to_position(speed,180)
            self.left_motor.on_to_position(speed,90)
        if position[0].lower() in Position.G.value[0]:            
            self.right_motor.on_to_position(speed,180)
            self.left_motor.on_to_position(speed,135)
        if position[0].lower() in Position.H.value[0]: 
            """go home first before proceed to avoid clash"""  
            self.right_motor.on_to_position(speed,0)
            self.left_motor.on_to_position(speed,0)         
            self.right_motor.on_to_position(speed,90)
            self.left_motor.on_to_position(speed,225)
        if position[0].lower() in Position.I.value[0]:            
            """go home first before proceed to avoid clash"""  
            self.right_motor.on_to_position(speed,0)
            self.left_motor.on_to_position(speed,0)         
            self.right_motor.on_to_position(speed,45)
            self.left_motor.on_to_position(speed,225)
        if position[0].lower() in Position.J.value[0]:            
            self.right_motor.on_to_position(speed,0)
            self.left_motor.on_to_position(speed,90)
        if position[0].lower() in Position.K.value[0]:            
            self.right_motor.on_to_position(speed,135)
            self.left_motor.on_to_position(speed,0)
        if position[0].lower() in Position.L.value[0]:            
            self.right_motor.on_to_position(speed,135)
            self.left_motor.on_to_position(speed,45)
        if position[0].lower() in Position.M.value[0]:
            self.right_motor.on_to_position(speed,135)
            self.left_motor.on_to_position(speed,90)
        if position[0].lower() in Position.N.value[0]:            
            self.right_motor.on_to_position(speed,135)
            self.left_motor.on_to_position(speed,135)
        if position[0].lower() in Position.O.value[0]:
            self.right_motor.on_to_position(speed,45)
            self.left_motor.on_to_position(speed,225)
        if position[0].lower() in Position.P.value[0]:            
            self.right_motor.on_to_position(speed,45)
            self.left_motor.on_to_position(speed,0)
        if position[0].lower() in Position.Q.value[0]:
            print("flag position position[0].lower():{},Position.Q.value[0].lower():{}".format(position[0].lower(),Position.Q.value[0].lower()),file=sys.stderr)
            self.right_motor.on_to_position(speed,90)
            self.left_motor.on_to_position(speed,45)
        if position[0].lower() in Position.R.value[0]:
            print("flag position position[0].lower():{},Position.R.value[0].lower():{}".format(position[0].lower(),Position.R.value[0].lower()),file=sys.stderr)
            self.right_motor.on_to_position(speed,90)
            self.left_motor.on_to_position(speed,90)
        if position[0].lower() in Position.S.value[0]:
            print("flag position position[0].lower():{},Position.S.value[0].lower():{}".format(position[0].lower(),Position.S.value[0].lower()),file=sys.stderr)
            self.right_motor.on_to_position(speed,45)
            self.left_motor.on_to_position(speed,135)
        if position[0].lower() in Position.T.value[0]:
            print("flag position position[0].lower():{},Position.T.value[0].lower():{}".format(position[0].lower(),Position.T.value[0].lower()),file=sys.stderr)
            self.right_motor.on_to_position(speed,45)
            self.left_motor.on_to_position(speed,0)
        if position[0].lower() in Position.U.value[0]:
            self.right_motor.on_to_position(speed,45)
            self.left_motor.on_to_position(speed,45)
        if position[0].lower() in Position.V.value[0]:
            self.right_motor.on_to_position(speed,0)
            self.left_motor.on_to_position(speed,135)
        if position[0].lower() in Position.W.value[0]:
            """ homing of all motors """
            self.right_motor.on_to_position(SemaphoreSpeed,0)
            self.left_motor.on_to_position(SemaphoreSpeed,0)
            """ end of homing """
            self.right_motor.on_to_position(speed,270)
            self.left_motor.on_to_position(speed,45)
        if position[0].lower() in Position.X.value[0]:
            """ homing of all motors """
            self.right_motor.on_to_position(SemaphoreSpeed,0)
            self.left_motor.on_to_position(SemaphoreSpeed,0)
            """ end of homing """
            self.right_motor.on_to_position(speed,270)
            self.left_motor.on_to_position(speed,135)
        if position[0].lower() in Position.Y.value[0]:
            self.right_motor.on_to_position(speed,45)
            self.left_motor.on_to_position(speed,90)
        if position[0].lower() in Position.Z.value[0]:
            """ homing of all motors """
            self.right_motor.on_to_position(SemaphoreSpeed,0)
            self.left_motor.on_to_position(SemaphoreSpeed,0)
            """ end of homing """
            self.right_motor.on_to_position(speed,225)
            self.left_motor.on_to_position(speed,90)


    def _activate(self, command, speed=SemaphoreSpeed):
        """
        Handles preset commands.
        :param command: the preset command
        :param speed: the speed if applicable
        """
        print("Activate command: ({}, {})".format(command, speed), file=sys.stderr)
        if command in Command.MOVE_CIRCLE.value:
            """self.drive.on_for_seconds(SpeedPercent(int(speed)), SpeedPercent(5), 12)"""
            self.left_motor.on_to_position(SemaphoreSpeed,0)

        if command in Command.MOVE_SQUARE.value:
            for i in range(4):
                self._move("right", 2, speed, is_blocking=True)
        
        if command in Command.PATROL.value:
            # Set patrol mode to resume patrol thread processing
            self.patrol_mode = True

        if command in Command.FIRE_ONE.value:
            """self.weapon.on_for_rotations(SpeedPercent(100), 3)"""
            self.left_motor.on_to_position(SemaphoreSpeed,0)
            

        if command in Command.FIRE_ALL.value:
            """self.weapon.on_for_rotations(SpeedPercent(100), 10)"""
            self.left_motor.COMMAND_RUN_TO_ABS_POS(position_sp=0)

    def _turn(self, direction, speed):
        """
        Turns based on the specified direction and speed.
        Calibrated for hard smooth surface.
        :param direction: the turn direction
        :param speed: the turn speed
        """
        if direction in Direction.LEFT.value:
            """self.drive.on_for_seconds(SpeedPercent(0), SpeedPercent(speed), 2)"""
            self.left_motor.COMMAND_RUN_TO_ABS_POS(position_sp=0, stop_sp="brake")

        if direction in Direction.RIGHT.value:
            """self.drive.on_for_seconds(SpeedPercent(speed), SpeedPercent(0), 2)"""
            self.left_motor.COMMAND_RUN_TO_ABS_POS(position_sp=200, stop_sp="brake")

    def _patrol_thread(self):
        """
        Performs random movement when patrol mode is activated.
        """
        while True:
            while self.patrol_mode:
                print("Patrol mode activated randomly picks a path", file=sys.stderr)
                direction = random.choice(list(Direction))
                duration = random.randint(1, 5)
                speed = random.randint(1, 4) * 25

                while direction == Direction.STOP:
                    direction = random.choice(list(Direction))

                # direction: all except stop, duration: 1-5s, speed: 25, 50, 75, 100
                self._move(direction.value[0], duration, speed)
                time.sleep(duration)
            time.sleep(1)


if __name__ == '__main__':

    gadget = MindstormsGadget()

    # Set LCD font and turn off blinking LEDs
    os.system('setfont Lat7-Terminus12x6')
    gadget.leds.set_color("LEFT", "BLACK")
    gadget.leds.set_color("RIGHT", "BLACK")

    # Startup sequence
    gadget.sound.play_song((('C4', 'e'), ('D4', 'e'), ('E5', 'q')))
    gadget.leds.set_color("LEFT", "GREEN")
    gadget.leds.set_color("RIGHT", "GREEN")

    # Gadget main entry point
    gadget.main()

    # Shutdown sequence
    gadget.sound.play_song((('E5', 'e'), ('C4', 'e')))
    gadget.leds.set_color("LEFT", "BLACK")
    gadget.leds.set_color("RIGHT", "BLACK")

