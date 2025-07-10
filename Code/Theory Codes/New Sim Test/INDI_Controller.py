import numpy as np
from scipy.signal import lfilter
from typing import Tuple, Optional


class INDIRateController:

    def __init__(self, motor_directions = np.array([1,-1,1,-1]), b = 0.1, l=0.1, k1 = 1.0, k2 = 1.0, Ts =0.01, I = np.eye(3), Ir_zz = 0.1):
        self.motor_directions = motor_directions
        self.last_motor_rates = np.zeros(4)
        self.last_motor_rates_filtered = np.zeros(4)
        self.last_motor_rates_filtered2 = np.zeros(4)
        self.last_motor_rates_filtered3 = np.zeros(4)

        self.Ts = Ts  # Sample time [s]

        # Drone parameters
        self.b = np.array([1,1,1,1]) * b  # Drone parameter, Distance from COM to motor in y axis. [m]
        self.l = np.array([1,1,1,1]) * l  # Drone parameter, Distance from COM to motor in x axis. [m]

        # Motor parameters
        self.k1 = np.array([1,1,1,1]) * k1  # Force constant of the motor. [N/(rad/s)]
        self.k2 = np.array([1,1,1,1]) * k2  # Torque constant of the motor. [N/(rad/s)]

        
        # In the artible, I is written as Iv
        self.Inertia = I # Inertia matrix of the drone. [kg*m^2]

        self.Ir_zz = Ir_zz # Inertia of the rotor around the z axis. [kg*m^2]


        '''TODO:
        1. Understand the motors direction impact on the calculations.
        2. Implement the G and M matrices.
        3. Implement the 2nd order filter for the motor rates.
        4. find the rotor moment of inertia.
        '''