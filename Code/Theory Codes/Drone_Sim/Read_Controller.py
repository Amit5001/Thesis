import pygame
import numpy as np
from scipy.interpolate import interp1d


class RadiomasterController:
    """
    A library for reading data from Radiomaster Boxer controller and mapping the values.
    """

    def __init__(self, joystick_id=0, auto_init=True):
        """
        Initialize the RadiomasterController class.

        Args:
            joystick_id (int): ID of the joystick to use (default: 0, first joystick)
            auto_init (bool): Automatically initialize pygame and joystick (default: True)
        """

        """
        Ch0- Roll
        Ch1- Pitch
        Ch2- Throttle
        Ch3- Yaw
        Ch4- SA
        Ch5- SB
        Ch6- SC
        Ch7- SD
        """
        self.joystick_id = joystick_id
        self.joystick = None

        self.max_rate = 200 # deg/s
        self.max_angle = 15 # deg

        if auto_init:
            self.initialize()
        self.raw_axes = np.array(self.num_axes * [0.0])
        self.map_acro = np.array(self.num_axes * [0.0])
        self.map_stab = np.array(self.num_axes * [0.0])
        self.interp_thr = interp1d([-1.0, 1.0], [1000, 2000])
        self.interp_rate = interp1d([-1.0, 1.0], [-self.max_rate, self.max_rate])
        self.interp_angle = interp1d([-1.0, 1.0], [-self.max_angle, self.max_angle])

    def initialize(self):
        """Initialize pygame and joystick modules."""
        pygame.init()
        pygame.joystick.init()

        # Check if any joysticks are connected
        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            raise ValueError("No joystick detected. Please connect your Radiomaster Boxer controller.")

        if self.joystick_id >= joystick_count:
            raise ValueError(f"Joystick ID {self.joystick_id} out of range. Only {joystick_count} joysticks available.")

        # Initialize the joystick
        self.joystick = pygame.joystick.Joystick(self.joystick_id)
        self.joystick.init()

        # Store controller info
        self.name = self.joystick.get_name()
        self.num_axes = self.joystick.get_numaxes()
        self.num_buttons = self.joystick.get_numbuttons()
        self.num_hats = self.joystick.get_numhats()


    def get_controller_info(self):
        """Get basic information about the controller."""
        if not self.joystick:
            raise RuntimeError("Controller not initialized. Call initialize() first.")

        return {
            "name": self.name,
            "num_axes": self.num_axes,
            "num_buttons": self.num_buttons,
            "num_hats": self.num_hats
        }

    def read_gimbals(self):
        """
        Read all gimbal/axis values from the controller and return as a numpy array.

        Returns:
            numpy.ndarray: Array of axis values in range [-1.0, 1.0]
        """
        if not self.joystick:
            raise RuntimeError("Controller not initialized. Call initialize() first.")

        # Update pygame events to get fresh values
        pygame.event.pump()

        # Read all axis values into numpy array
        self.raw_axes = np.array([self.joystick.get_axis(i) for i in range(self.num_axes)])
        return self.raw_axes

    def map_gimbals_acro(self, in_min=-1.0, in_max=1.0):

        """
        Map gimbal values to a specified range with deadzone and expo.

        Args:
            in_min (float): Minimum input value (default: -1.0)
            in_max (float): Maximum input value (default: 1.0)
            out_min (float): Minimum output value (default: 0.0)
            out_max (float): Maximum output value (default: 1.0)

        Returns:
            numpy.ndarray: Mapped gimbal values
        """

        self.map_acro[2] = self.interp_thr(self.raw_axes[2])
        self.map_acro[0] = -self.interp_rate(self.raw_axes[0])
        self.map_acro[1] = self.interp_rate(self.raw_axes[1])
        self.map_acro[3] = self.interp_angle(self.raw_axes[3])

    def map_gimbals_stab(self, in_min=-1.0, in_max=1.0):
        """
        Map gimbal values to a specified range with deadzone and expo.

        Args:
            in_min (float): Minimum input value (default: -1.0)
            in_max (float): Maximum input value (default: 1.0)
            out_min (float): Minimum output value (default: 0.0)
            out_max (float): Maximum output value (default: 1.0)

        Returns:
            numpy.ndarray: Mapped gimbal values
        """
        self.map_stab[2] = self.interp_thr(self.raw_axes[2])
        self.map_stab[0] = self.interp_rate(self.raw_axes[0])
        self.map_stab[1] = self.interp_rate(self.raw_axes[1])
        self.map_stab[3] = self.interp_angle(self.raw_axes[3])

    def read_buttons(self):
        """Read all button values from the controller."""
        if not self.joystick:
            raise RuntimeError("Controller not initialized. Call initialize() first.")

        pygame.event.pump()
        return np.array([self.joystick.get_button(i) for i in range(self.num_buttons)])

    def read_hats(self):
        """Read all hat values from the controller."""
        if not self.joystick:
            raise RuntimeError("Controller not initialized. Call initialize() first.")

        pygame.event.pump()
        return [self.joystick.get_hat(i) for i in range(self.num_hats)]

    def close(self):
        """Clean up pygame resources."""
        if self.joystick:
            self.joystick.quit()
        pygame.quit()


# Example usage
if __name__ == "__main__":
    import time

    # Create controller object
    rc = RadiomasterController()

    # Print controller info
    info = rc.get_controller_info()
    print(f"Controller: {info['name']}")
    print(f"Axes: {info['num_axes']}, Buttons: {info['num_buttons']}, Hats: {info['num_hats']}")

    try:
        print("\nReading controller data. Press Ctrl+C to exit.")
        print("Move sticks to see values change...\n")

        while True:
            # Read raw gimbal values
            gimbal_values = rc.read_gimbals()

            # Map gimbal values to acro mode
            rc.map_gimbals_acro()

            # Print mapped values
            print(f"Raw Gimbal Values: {gimbal_values[0]}")
            print(f"Mapped Acro Values: {rc.map_acro[0]}")


    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        # Clean up
        rc.close()