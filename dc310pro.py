# dc310pro.py
"""
Module for communicating with the DC310PRO device.

This module gives a simple Python interface to the instrument. It will be able to open the connection, 
ask the instrument for identity, and close cleanly.

"""

import pyvisa

def connect_to_instrument():
    # Create a resource manager to handle all instrument connections
    rm = pyvisa.ResourceManager()
    
    # Ask OS what instruments are visible
    resources = rm.list_resources()

    if not resources:
        raise RuntimeError("No instruments found. Please check the connection.")
    
    # Connect to first instrument found (for simplicity)
    resource_string = resources[0]
    # Open the connection to the instrument
    instrument = rm.open_resource(resource_string)
    # Ask the instrument for its identity
    identity = instrument.query("*IDN?").strip()

    # Verify that the instrument is the expected DC310PRO
    if "KIPRIM" not in identity.upper() or "DC310" not in identity.upper():
        instrument.close()
        raise RuntimeError(f"Connected to unexpected instrument: {identity}")
    
    print(f"Connected to: {identity}")
    return instrument


if __name__ == "__main__":
    # Only runs code when executed directly
    instrument = connect_to_instrument()
    instrument.close()
    print("Connection closed.")