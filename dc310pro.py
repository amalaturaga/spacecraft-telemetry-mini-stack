# pyright: reportAttributeAccessIssue=false
# dc310pro.py
"""
Module for communicating with the DC310PRO programmable DC power supply.

Provides a DC310Pro class that wraps pyvisa with a simple, focused interface:
- Connect to the instrument
- Read measurements (voltage, current, power)
- Disconnect cleanly

The DC310Pro uses a CH340 USB-to-serial bridge internally, so it appears
to the OS as a serial device (e.g., /dev/ttyUSB1 on Linux). Default
serial parameters: 115200 baud, 8 data bits, no parity, 1 stop bit,
LF (\\n) line termination.

Usage:
    with DC310Pro("ASRL/dev/ttyUSB1::INSTR") as psu:
        v = psu.measure_voltage()
        i = psu.measure_current()

"""

import pyvisa

class DC310PRO:
    # Identification strings to expect in *IDN? response
    EXPECTED_VENDOR = "KIPRIM"
    EXPECTED_MODEL = "DC310"

    # Serial parameters established by experiemnt with this device
    DEFAULT_BAUD_RATE = 115200
    DEFAULT_DATA_BITS = 8
    DEFAULT_TIMEOUT_MS = 2000 # default for slow serial responses

    def __init__(self, resource_string):
        """
        Connect to DC310PRO instrument. 

        A class here let's us keep the connection open and manage it more easily. 
        The constructor will handle connecting to the instrument, and we can add methods later 
        for controlling it.

        The leading underscore on _instrument is a Python convention meaning
        "this is internal — don't touch from outside the class."

        """
        self._rm = pyvisa.ResourceManager()
 
        # Open resource. Returned object is message-based
        self._instrument = pyvisa.resources.MessageBasedResource = (
            self._rm.open_resource(resource_string)
        )

        # Configure the serial connection parameters. Set AFTER open_resource()
        # since pyvisa creates the resource with default values
        self._instrument.baud_rate = self.DEFAULT_BAUD_RATE
        self._instrument.data_bits = self.DEFAULT_DATA_BITS
        self._instrument.timeout = self.DEFAULT_TIMEOUT_MS
        self._instrument.parity = pyvisa.constants.Parity.none
        self._instrument.stop_bits = pyvisa.constants.StopBits.one
        self._instrument.write_termination = "\n"
        self._instrument.read_termination = "\n"

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
    # Quick demo that is run when file is executed directly. The resource string
    # is harcoded for now; later it'll read it from a config

    RESOURCE = "ASRL/dev/ttyUSB1::INSTR"

    with DC310PRO(RESOURCE) as psu:
        v = psu.measure_voltage()
        i = psu.measure_current()
        p = psu.measure_power()
        print(f"Voltage: {v:.4f} V")
        print(f"Current: {i:.4f} A")
        print(f"Power: {p:.4f} W")