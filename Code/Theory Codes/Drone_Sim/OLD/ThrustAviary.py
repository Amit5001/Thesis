import numpy as np
import pybullet as p
from gym_pybullet_drones.envs.CtrlAviary import CtrlAviary
from gym_pybullet_drones.utils.enums import DroneModel, Physics


class ThrustAviary(CtrlAviary):
    """Aviary environment that accepts direct thrust values as input."""

    def __init__(self,
                 drone_model=DroneModel.RACE,
                 num_drones=1,
                 neighbourhood_radius=np.inf,
                 initial_xyzs=None,
                 initial_rpys=None,
                 physics=Physics.PYB,
                 pyb_freq=240,
                 ctrl_freq=240,
                 gui=False,
                 record=False,
                 obstacles=False,
                 user_debug_gui=True,
                 output_folder='results'
                 ):
        """Initialize the thrust-based aviary.

        Parameters are the same as CtrlAviary.
        """
        super().__init__(drone_model=drone_model,
                         num_drones=num_drones,
                         neighbourhood_radius=neighbourhood_radius,
                         initial_xyzs=initial_xyzs,
                         initial_rpys=initial_rpys,
                         physics=physics,
                         pyb_freq=pyb_freq,
                         ctrl_freq=ctrl_freq,
                         gui=gui,
                         record=record,
                         obstacles=obstacles,
                         user_debug_gui=user_debug_gui,
                         output_folder=output_folder
                         )

        # Print parameters for reference
        print(f"[INFO] Drone parameters - KF: {self.KF}, KM: {self.KM}")
        print(f"[INFO] Drone parameters - Mass: {self.M}, Gravity: {self.G}")
        print(f"[INFO] Drone parameters - Hover RPM: {self.HOVER_RPM}, Hover Thrust: {self.M * self.G / 4} N")

    def _preprocessAction(self, action):
        """Converts thrust values to RPM.

        Parameters
        ----------
        action : ndarray
            (NUM_DRONES, 4)-shaped array of thrust values in Newtons.

        Returns
        -------
        ndarray
            (NUM_DRONES, 4)-shaped array of RPM values.
        """
        # Calculate RPM from thrust
        # Thrust = KF * RPM^2
        # RPM = sqrt(Thrust / KF)
        rpms = np.zeros((self.NUM_DRONES, 4))

        for i in range(self.NUM_DRONES):
            # Ensure positive thrust
            thrust = np.clip(action[i], 0, None)
            # Convert thrust to RPM
            rpms[i] = np.sqrt(thrust / self.KF)

        return rpms