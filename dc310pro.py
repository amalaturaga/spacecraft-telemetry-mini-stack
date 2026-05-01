# dc310pro.py
"""
Module for communicating with the DC310PRO programmable DC power supply.

This module gives a simple Python interface to the instrument. It will be able to open the connection, 
ask the instrument for identity, and close cleanly.

"""

import pyvisa

class DC310PRO:
    EXPECTED_VENDOR = "KIPRIM"
    EXPECTED_MODEL = "DC310"

    def __init__(self, resource_string=None):
        """
        Connect to DC310PRO instrument. 

        A class here let's us keep the connection open and manage it more easily. 
        The constructor will handle connecting to the instrument, and we can add methods later 
        for controlling it.

        The leading underscore on _instrument is a Python convention meaning
        "this is internal — don't touch from outside the class."

        """
        self._rm = pyvisa.ResourceManager()
        
        if resource_string is None:
            resources = self._rm.list_resources()
            if not resources:
                raise RuntimeError(
                    "No instruments found. Please check the connection."
                )
            resource_string = resources[0]
        self._instrument = self._rm.open_resource(resource_string)

        # Validate that we are connected to the expected instrument before sending commands
        identity = self._instrument.query("*IDN?").strip()
        if (self.EXPECTED_VENDOR not in identity.upper() 
                or self.EXPECTED_MODEL not in identity.upper()):
            self._instrument.close()
            raise RuntimeError(
                f"Connected instrument is not a DC310PRO: {identity}"
            )
        
        # save the identity for later use
        self.identity = identity
        print(f"Connected to: {self.identity}")

    def measure_voltage(self):
        """ 
        Read the actual voltage coming from the output terminals, in volts.

        Returns a float.

        MEAS:VOLT? is the SCPI command to ask for the voltage measurement. 
        The instrument will return a string that we need to convert to a float.
        
        """
        response = self._instrument.query("MEAS:VOLT?")
        return float(response.strip())

    def measure_current(self):
        """ 
        Read the actual current coming from the output terminals, in amps.

        Returns a float.

        MEAS:CURR? is the SCPI command to ask for the current measurement. 
        The instrument will return a string that we need to convert to a float.
        
        """
        response = self._instrument.query("MEAS:CURR?")
        return float(response.strip())

    def measure_power(self):
        """ 
        Calculate the instantaneous power being delivered to the load, in watts.

        Some instruments support MEAS:POW? directly, which will return the power measurement. 
        If not, we can calculate it ourselves by multiplying the voltage and current measurements.
        This means, one fewer command to the instrument, but it will be slightly less accurate since the voltage 
        and current are measured separately and may fluctuate between measurements.
        
        """
        return self.measure_voltage() * self.measure_current()

    def close(self):
        """ 
        Close the connection to the instrument. Always call this when you're done 
        to free up resources and avoid leaving the instrument in an unknown state.
        
        """
        if self._instrument is not None:
            self._instrument.close()
            self._instrument = None

    def __enter__(self):
        """ 
        Support for context manager (with statement). This allows us to use the instrument in a with block, 
        which will automatically close the connection when we're done, even if an error occurs.
        
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ 
        Automatically close the connection when exiting a with block.
        
        """
        self.close()


if __name__ == "__main__":
    # Quick demo that is run when file is executed directly.
    with DC310PRO() as psu:
        v = psu.measure_voltage()
        i = psu.measure_current()
        p = psu.measure_power()
        print(f"Voltage: {v:.4f} V")
        print(f"Current: {i:.4f} A")
        print(f"Power: {p:.4f} W")