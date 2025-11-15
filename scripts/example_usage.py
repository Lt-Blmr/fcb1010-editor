#!/usr/bin/env python3
"""
Example usage of FCB1010 Editor library.

This script demonstrates how to use the FCB1010 library to interact with the
Behringer FCB1010 MIDI foot controller.
"""

# Remove unused imports and fix import order
import sys
import json
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.fcb1010 import FCB1010, Preset


def list_midi_ports():
    """List all available MIDI ports"""
    import rtmidi

    midi_in = rtmidi.MidiIn()
    midi_out = rtmidi.MidiOut()

    in_ports = midi_in.get_ports()
    out_ports = midi_out.get_ports()

    print("Available MIDI Input ports:")
    for i, port in enumerate(in_ports):
        print(f"  {i}: {port}")

    print("\nAvailable MIDI Output ports:")
    for i, port in enumerate(out_ports):
        print(f"  {i}: {port}")

    midi_in.delete()
    midi_out.delete()


def create_and_save_presets():
    """Create example presets and save them to a file"""
    presets = []

    # Create some example presets
    for i in range(5):
        preset = Preset(i, f"Example Preset {i}")

        # Add program changes
        preset.add_program_change(i * 10)

        # Add control changes
        preset.add_control_change(7, 100)  # Volume at max
        preset.add_control_change(10, 64)  # Pan center

        presets.append(preset.to_dict())

    # Save to file
    with open("example_presets.json", "w") as f:
        json.dump(presets, f, indent=2)

    print(f"Saved {len(presets)} presets to example_presets.json")


def simple_midi_monitor():
    """Simple MIDI monitor example using FCB1010 class"""
    print("Starting MIDI monitor...")
    print("Press Ctrl+C to exit")

    try:
        # Connect to the first available MIDI port
        fcb = FCB1010()

        # Keep the script running to receive MIDI messages
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Close the MIDI connection if it was created
        try:
            fcb.close()
        except NameError:
            pass


def send_program_changes():
    """Example of sending program changes to the FCB1010"""
    fcb = FCB1010()

    try:
        print("Sending program changes...")
        for i in range(5):
            fcb.send_program_change(i)
            print(f"Sent program change: {i}")
            time.sleep(1)
    finally:
        fcb.close()


def main():
    """Main function to demonstrate FCB1010 library usage"""
    logging.basicConfig(level=logging.INFO)

    print("FCB1010 Editor Example Usage")
    print("===========================")
    print("\n1. List MIDI Ports")
    print("2. Create and Save Example Presets")
    print("3. MIDI Monitor")
    print("4. Send Program Changes")
    print("q. Quit")

    choice = input("\nEnter your choice: ")

    if choice == "1":
        list_midi_ports()
    elif choice == "2":
        create_and_save_presets()
    elif choice == "3":
        simple_midi_monitor()
    elif choice == "4":
        send_program_changes()
    elif choice.lower() == "q":
        print("Exiting...")
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
