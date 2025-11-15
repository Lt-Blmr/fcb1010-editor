"""
FCB1010 Editor - A Python library for interfacing with the Behringer FCB1010 MIDI foot controller.

This module provides classes and functions to read, write, and edit presets for the FCB1010 midi foot controller.
"""

import rtmidi
import logging
import time
from typing import List, Optional, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FCB1010 SysEx constants
SYSEX_START = 0xF0
SYSEX_END = 0xF7
FCB1010_MANUFACTURER_ID = [0x00, 0x20, 0x29]  # Behringer
FCB1010_DEVICE_ID = 0x02
FCB1010_MODEL_ID = 0x0C


class FCB1010:
    """
    Main class for interfacing with the Behringer FCB1010 MIDI foot controller.
    """

    def __init__(self, input_port=None, output_port=None):
        """
        Initialize the FCB1010 interface.

        Args:
            input_port (int, optional): MIDI input port index. If not provided, the first available port is used.
            output_port (int, optional): MIDI output port index. If not provided, the first available port is used.
        """
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()

        # Get available ports
        available_in_ports = self.midi_in.get_ports()
        available_out_ports = self.midi_out.get_ports()

        logger.info(f"Available MIDI Input ports: {available_in_ports}")
        logger.info(f"Available MIDI Output ports: {available_out_ports}")

        # Connect to MIDI ports
        if input_port is not None and 0 <= input_port < len(available_in_ports):
            self.midi_in.open_port(input_port)
            logger.info(
                f"Connected to MIDI Input port: {available_in_ports[input_port]}"
            )
        elif available_in_ports:
            # Find a port containing "FCB1010" if possible
            fcb_ports = [
                i for i, port in enumerate(available_in_ports) if "FCB1010" in port
            ]
            if fcb_ports:
                self.midi_in.open_port(fcb_ports[0])
                logger.info(
                    f"Connected to FCB1010 MIDI Input port: {available_in_ports[fcb_ports[0]]}"
                )
            else:
                self.midi_in.open_port(0)
                logger.info(
                    f"Connected to default MIDI Input port: {available_in_ports[0]}"
                )
        else:
            logger.warning("No MIDI Input ports available. Creating virtual port.")
            self.midi_in.open_virtual_port("FCB1010 Input")

        # Set up MIDI output port similarly
        if output_port is not None and 0 <= output_port < len(available_out_ports):
            self.midi_out.open_port(output_port)
            logger.info(
                f"Connected to MIDI Output port: {available_out_ports[output_port]}"
            )
        elif available_out_ports:
            fcb_ports = [
                i for i, port in enumerate(available_out_ports) if "FCB1010" in port
            ]
            if fcb_ports:
                self.midi_out.open_port(fcb_ports[0])
                logger.info(
                    f"Connected to FCB1010 MIDI Output port: {available_out_ports[fcb_ports[0]]}"
                )
            else:
                self.midi_out.open_port(0)
                logger.info(
                    f"Connected to default MIDI Output port: {available_out_ports[0]}"
                )
        else:
            logger.warning("No MIDI Output ports available. Creating virtual port.")
            self.midi_out.open_virtual_port("FCB1010 Output")

        # Set up a callback function for incoming MIDI messages
        self.midi_in.set_callback(self._midi_callback)

        # Current preset
        self.current_preset = None

        # Sysex response storage
        self._sysex_responses = []
        self._sysex_timeout = 2.0  # seconds

    def _midi_callback(self, message, time_stamp):
        """
        Callback function for MIDI messages.

        Args:
            message (tuple): MIDI message data
            time_stamp (float): Timestamp of the message
        """
        logger.debug(f"MIDI message received: {message} at {time_stamp}")
        # Process MIDI message here
        if len(message) > 0:
            msg_data = message[0]
            if len(msg_data) > 0:
                status = msg_data[0] & 0xF0  # Extract status byte
                if status == 0xC0:  # Program Change
                    preset_num = msg_data[1]
                    logger.info(f"Program Change: Preset {preset_num}")
                    self.current_preset = preset_num
                elif msg_data[0] == SYSEX_START:  # SysEx message
                    logger.debug(f"SysEx message received: {msg_data}")
                    self._sysex_responses.append((msg_data, time_stamp))

    def send_program_change(self, program_number, channel=0):
        """
        Send a Program Change message to the FCB1010.

        Args:
            program_number (int): The program number (0-127)
            channel (int, optional): MIDI channel (0-15). Defaults to 0.
        """
        if 0 <= program_number <= 127 and 0 <= channel <= 15:
            status = 0xC0 | channel  # Program Change status byte
            message = [status, program_number]
            self.midi_out.send_message(message)
            logger.info(f"Sent Program Change: {program_number} on channel {channel}")
        else:
            logger.error(
                f"Invalid program number ({program_number}) or channel ({channel})"
            )

    def send_control_change(self, controller, value, channel=0):
        """
        Send a Control Change message to the FCB1010.

        Args:
            controller (int): Controller number (0-127)
            value (int): Controller value (0-127)
            channel (int, optional): MIDI channel (0-15). Defaults to 0.
        """
        if 0 <= controller <= 127 and 0 <= value <= 127 and 0 <= channel <= 15:
            status = 0xB0 | channel  # Control Change status byte
            message = [status, controller, value]
            self.midi_out.send_message(message)
            logger.info(
                f"Sent Control Change: controller={controller}, value={value}, channel={channel}"
            )
        else:
            logger.error(
                f"Invalid controller ({controller}), value ({value}), or channel ({channel})"
            )

    def send_sysex(self, data: List[int]) -> bool:
        """
        Send a SysEx message to the FCB1010.

        Args:
            data: List of bytes to send (without F0/F7, they will be added automatically)

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            # Build complete sysex message
            sysex_msg = [SYSEX_START]
            sysex_msg.extend(FCB1010_MANUFACTURER_ID)
            sysex_msg.append(FCB1010_DEVICE_ID)
            sysex_msg.append(FCB1010_MODEL_ID)
            sysex_msg.extend(data)
            sysex_msg.append(SYSEX_END)

            # Validate all bytes are in valid range (0-127)
            if not all(0 <= byte <= 127 for byte in sysex_msg):
                logger.error("Invalid sysex data: bytes must be in range 0-127")
                return False

            self.midi_out.send_message(sysex_msg)
            logger.debug(f"Sent SysEx: {[hex(b) for b in sysex_msg]}")
            return True
        except Exception as e:
            logger.error(f"Error sending sysex: {e}")
            return False

    def send_sysex_data(self, data: List[int]) -> bool:
        """
        Easy-to-use method to send raw sysex data to FCB1010.
        This is a convenience wrapper around send_sysex().

        Args:
            data: List of data bytes to send (will be wrapped with FCB1010 sysex header)

        Returns:
            bool: True if sent successfully, False otherwise

        Example:
            >>> fcb = FCB1010()
            >>> fcb.send_sysex_data([0x01, 0x02, 0x03])
        """
        return self.send_sysex(data)

    def wait_for_sysex_response(self, timeout: Optional[float] = None) -> Optional[List[int]]:
        """
        Wait for a sysex response from the FCB1010.

        Args:
            timeout: Maximum time to wait in seconds (defaults to self._sysex_timeout)

        Returns:
            List of bytes from the sysex response, or None if timeout
        """
        if timeout is None:
            timeout = self._sysex_timeout

        start_time = time.time()
        initial_response_count = len(self._sysex_responses)

        while time.time() - start_time < timeout:
            if len(self._sysex_responses) > initial_response_count:
                response_data, _ = self._sysex_responses.pop(0)
                # Validate and extract sysex data
                if len(response_data) >= 2:
                    if response_data[0] == SYSEX_START and response_data[-1] == SYSEX_END:
                        # Remove F0 and F7, return data bytes
                        return list(response_data[1:-1])
                    else:
                        logger.warning("Received invalid sysex message format")
            time.sleep(0.01)

        logger.warning(f"No sysex response received within {timeout} seconds")
        return None

    def read_preset_sysex(self, preset_number: int) -> Optional[List[int]]:
        """
        Read a preset from FCB1010 using sysex.

        Args:
            preset_number: Preset number to read (0-99)

        Returns:
            List of bytes from the preset data, or None if failed
        """
        if not 0 <= preset_number <= 99:
            logger.error(f"Invalid preset number: {preset_number} (must be 0-99)")
            return None

        # Clear any pending responses
        self._sysex_responses.clear()

        # Build read preset command (command format may vary - this is a common pattern)
        # Command byte 0x01 typically means "read preset"
        command = [0x01, preset_number]

        if self.send_sysex(command):
            return self.wait_for_sysex_response()
        return None

    def write_preset_sysex(self, preset_number: int, preset_data: List[int]) -> bool:
        """
        Write preset data to FCB1010 using sysex.

        Args:
            preset_number: Preset number to write (0-99)
            preset_data: List of bytes containing preset data

        Returns:
            bool: True if successful, False otherwise
        """
        if not 0 <= preset_number <= 99:
            logger.error(f"Invalid preset number: {preset_number} (must be 0-99)")
            return False

        # Build write preset command
        # Command byte 0x02 typically means "write preset"
        command = [0x02, preset_number]
        command.extend(preset_data)

        return self.send_sysex(command)

    def read_preset(self, preset_number):
        """
        Read preset data from the FCB1010.

        Args:
            preset_number (int): The preset number to read (0-99)

        Returns:
            dict: Preset data or None if read failed
        """
        logger.info(f"Reading preset {preset_number} via sysex")
        sysex_data = self.read_preset_sysex(preset_number)

        if sysex_data is None:
            logger.warning(f"Failed to read preset {preset_number}")
            return None

        # Parse sysex data into preset structure
        # This is a placeholder - actual parsing depends on FCB1010 sysex format
        return {
            "preset_number": preset_number,
            "name": f"Preset {preset_number}",
            "sysex_data": sysex_data,
        }

    def write_preset(self, preset_data):
        """
        Write preset data to the FCB1010.

        Args:
            preset_data (dict): Preset data to write. Must contain 'preset_number'
                                and optionally 'sysex_data' or other preset fields.

        Returns:
            bool: True if successful, False otherwise
        """
        preset_number = preset_data.get("preset_number")
        if preset_number is None:
            logger.error("preset_data must contain 'preset_number'")
            return False

        logger.info(f"Writing preset {preset_number} via sysex")

        # Extract sysex data if provided, otherwise build from preset structure
        if "sysex_data" in preset_data:
            sysex_data = preset_data["sysex_data"]
        else:
            # Build sysex data from preset structure
            # This is a placeholder - actual format depends on FCB1010 specification
            sysex_data = []
            # Add program changes
            for pc in preset_data.get("program_changes", []):
                sysex_data.extend([pc.get("program", 0), pc.get("channel", 0)])
            # Add control changes
            for cc in preset_data.get("control_changes", []):
                sysex_data.extend([
                    cc.get("controller", 0),
                    cc.get("value", 0),
                    cc.get("channel", 0)
                ])

        return self.write_preset_sysex(preset_number, sysex_data)

    def close(self):
        """
        Close MIDI connections.
        """
        if self.midi_in:
            self.midi_in.close_port()
        if self.midi_out:
            self.midi_out.close_port()
        logger.info("Closed MIDI connections")


class Preset:
    """
    Class representing an FCB1010 preset.
    """

    def __init__(self, preset_number, name=""):
        """
        Initialize a new preset.

        Args:
            preset_number (int): Preset number (0-99)
            name (str, optional): Preset name. Defaults to "".
        """
        self.preset_number = preset_number
        self.name = name if name else f"Preset {preset_number}"
        self.program_changes = []
        self.control_changes = []

    def add_program_change(self, program_number, channel=0):
        """
        Add a program change message to this preset.

        Args:
            program_number (int): Program number (0-127)
            channel (int, optional): MIDI channel (0-15). Defaults to 0.
        """
        self.program_changes.append({"program": program_number, "channel": channel})

    def add_control_change(self, controller, value, channel=0):
        """
        Add a control change message to this preset.

        Args:
            controller (int): Controller number (0-127)
            value (int): Controller value (0-127)
            channel (int, optional): MIDI channel (0-15). Defaults to 0.
        """
        self.control_changes.append(
            {"controller": controller, "value": value, "channel": channel}
        )

    def to_dict(self):
        """
        Convert preset to dictionary.

        Returns:
            dict: Preset data as dictionary
        """
        return {
            "preset_number": self.preset_number,
            "name": self.name,
            "program_changes": self.program_changes,
            "control_changes": self.control_changes,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a Preset object from dictionary data.

        Args:
            data (dict): Preset data

        Returns:
            Preset: New Preset object
        """
        preset = cls(data["preset_number"], data.get("name", ""))

        for pc in data.get("program_changes", []):
            preset.add_program_change(pc["program"], pc.get("channel", 0))

        for cc in data.get("control_changes", []):
            preset.add_control_change(
                cc["controller"], cc["value"], cc.get("channel", 0)
            )

        return preset
