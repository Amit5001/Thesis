# File: test_indi.py
# Add to the top of INDI_Controller.py and INDI_Test.py
import sys
import os
from INDI_Controller import INDIControl  # Adjust import path

from gym_pybullet_drones.envs.CtrlAviary import CtrlAviary
from gym_pybullet_drones.utils.enums import DroneModel, Physics


def test_indi_controller():
    # Environment setup
    env = CtrlAviary(
        drone_model=DroneModel.SPEDIX,
        physics=Physics.PYB,
        gui=False
    )

    # Controller setup
    controller = INDIControl(DroneModel.SPEDIX)

    # Test loop
    # Your testing code here


if __name__ == "__main__":
    test_indi_controller()