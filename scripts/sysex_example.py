#!/usr/bin/env python3
"""
Example usage of FCB1010 SysEx interface.

This script demonstrates how to use the sysex interface to communicate
with the Behringer FCB1010 MIDI foot controller.
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.fcb1010 import FCB1010

logging.basicConfig(level=logging.INFO)


def example_send_sysex():
    """Example: Send raw sysex data to FCB1010"""
    print("\n=== Example: Send Raw SysEx Data ===")
    fcb = FCB1010()

    try:
        # Example: Send a simple sysex command
        # This sends: F0 00 20 29 02 0C 01 02 03 F7
        data = [0x01, 0x02, 0x03]
        success = fcb.send_sysex_data(data)
        print(f"Sent sysex data: {[hex(b) for b in data]}")
        print(f"Success: {success}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        fcb.close()


def example_read_preset():
    """Example: Read a preset using sysex"""
    print("\n=== Example: Read Preset via SysEx ===")
    fcb = FCB1010()

    try:
        preset_number = 0
        print(f"Reading preset {preset_number}...")
        preset_data = fcb.read_preset_sysex(preset_number)

        if preset_data:
            print(f"Received preset data: {[hex(b) for b in preset_data]}")
        else:
            print("No data received (device may not be connected)")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        fcb.close()


def example_write_preset():
    """Example: Write preset data using sysex"""
    print("\n=== Example: Write Preset via SysEx ===")
    fcb = FCB1010()

    try:
        preset_number = 0
        # Example preset data (format depends on FCB1010 specification)
        preset_data = [0x00, 0x01, 0x02, 0x03, 0x04]

        print(f"Writing preset {preset_number}...")
        success = fcb.write_preset_sysex(preset_number, preset_data)

        if success:
            print(f"Successfully wrote preset {preset_number}")
        else:
            print("Failed to write preset")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        fcb.close()


def example_read_preset_dict():
    """Example: Read preset using the high-level interface"""
    print("\n=== Example: Read Preset (High-Level) ===")
    fcb = FCB1010()

    try:
        preset_number = 0
        print(f"Reading preset {preset_number}...")
        preset = fcb.read_preset(preset_number)

        if preset:
            print(f"Preset: {preset}")
        else:
            print("Failed to read preset")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        fcb.close()


def example_write_preset_dict():
    """Example: Write preset using the high-level interface"""
    print("\n=== Example: Write Preset (High-Level) ===")
    fcb = FCB1010()

    try:
        preset_data = {
            "preset_number": 0,
            "sysex_data": [0x00, 0x01, 0x02, 0x03]
        }

        print(f"Writing preset {preset_data['preset_number']}...")
        success = fcb.write_preset(preset_data)

        if success:
            print("Successfully wrote preset")
        else:
            print("Failed to write preset")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        fcb.close()


def main():
    """Main function demonstrating sysex interface"""
    print("FCB1010 SysEx Interface Examples")
    print("=" * 40)

    examples = [
        ("1", "Send Raw SysEx Data", example_send_sysex),
        ("2", "Read Preset (SysEx)", example_read_preset),
        ("3", "Write Preset (SysEx)", example_write_preset),
        ("4", "Read Preset (High-Level)", example_read_preset_dict),
        ("5", "Write Preset (High-Level)", example_write_preset_dict),
        ("q", "Quit", None),
    ]

    while True:
        print("\nAvailable examples:")
        for key, desc, _ in examples:
            print(f"  {key}. {desc}")

        choice = input("\nEnter your choice: ").strip().lower()

        if choice == "q":
            print("Exiting...")
            break

        for key, desc, func in examples:
            if choice == key and func:
                func()
                break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
