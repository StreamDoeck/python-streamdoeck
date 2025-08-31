#         Python Stream Doeck Library
#      Released under the GPLv2 licence
#
#  Authors:
#    * Lisias T (https://github.com/lisias)
#
#  Mirabox Stream Dock N3 non-official support

from ..ImageHelpers import ImageTools
from .StreamDeck import StreamDeck, ControlType, DialEventType
from .Mirabox import Mirabox

class MiraboxN3EN(Mirabox):
    """
    Represents a physically attached Mirabox Stream Dock N3 (EN) device.
    """

    OUTPUT_PACKET_LENGHT = 1024

    KEY_COLS = 3
    KEY_ROWS = 2
    KEY_COUNT = KEY_COLS * KEY_ROWS

    TOUCH_KEY_COUNT = 3

    KEY_PIXEL_WIDTH = 64
    KEY_PIXEL_HEIGHT = 64
    KEY_IMAGE_FORMAT = "JPEG"
    KEY_FLIP = (False, False)
    KEY_ROTATION = -90

    SCREEN_PIXEL_WIDTH = 320
    SCREEN_PIXEL_HEIGHT = 240
    SCREEN_IMAGE_FORMAT = "JPEG"
    SCREEN_FLIP = (True, False)
    SCREEN_ROTATION = -90

    DIAL_COUNT = 3

    DECK_TYPE = "Mirabox Stream Dock N3en"
    DECK_VISUAL = True
    DECK_TOUCH = False

    BLANK_KEY_IMAGE = ImageTools.load_asset("black-64x64.jpg")

    KEY_NUM_TO_DEVICE_KEY_ID = [
                                    0x01, 0x02, 0x03
                                ,   0x04, 0x05, 0x06
                                ,   0x25, 0x30, 0x31    # touch keys
                            ]
    KEY_DEVICE_ID_TO_KEY_NUM = {value: index for index, value in enumerate(KEY_NUM_TO_DEVICE_KEY_ID)}

    DIAL_NUM_PUSH_TO_DEVICE_KEY_ID = [0x35, 0x34, 0x33]
    KEY_DEVICE_ID_TO_DIAL_PUSH_NUM = {value: index for index, value in enumerate(DIAL_NUM_PUSH_TO_DEVICE_KEY_ID)}

    DIAL_TURN_LEFT_NUM_TO_DEVICE_KEY_ID = [0x50, 0x60, 0x90]
    KEY_DEVICE_ID_TO_DIAL_TURN_LEFT_NUM = {value: index for index, value in enumerate(DIAL_TURN_LEFT_NUM_TO_DEVICE_KEY_ID)}

    DIAL_TURN_RIGHT_NUM_TO_DEVICE_KEY_ID = [0x51, 0x61, 0x91]
    KEY_DEVICE_ID_TO_DIAL_TURN_RIGHT_NUM = {value: index for index, value in enumerate(DIAL_TURN_RIGHT_NUM_TO_DEVICE_KEY_ID)}

    def __init__(self, device):
        super().__init__(device)

    def _read_control_states(self):
        device_input_data = self.device.read(self.INPUT_PACKET_LENGHT)

        if(device_input_data and device_input_data.startswith(Mirabox.ACK_OK)):
            triggered_raw_key = device_input_data[9]
            triggered_state = device_input_data[10]

            if triggered_raw_key in self.KEY_NUM_TO_DEVICE_KEY_ID:
                states = [False] * (self.KEY_COUNT + self.TOUCH_KEY_COUNT)
                triggered_key = self.KEY_DEVICE_ID_TO_KEY_NUM[triggered_raw_key]
                states[triggered_key] = 1 == triggered_state
                return {
                    ControlType.KEY: states,
                }

            elif triggered_raw_key in self.DIAL_NUM_PUSH_TO_DEVICE_KEY_ID:
                states = [False] * self.DIAL_COUNT
                triggered_key = self.KEY_DEVICE_ID_TO_DIAL_PUSH_NUM[triggered_raw_key]
                states[triggered_key] = 1 == triggered_state
                return {
                    ControlType.DIAL: {
                        DialEventType.PUSH : states
                    }
                }

            elif triggered_raw_key in self.DIAL_TURN_LEFT_NUM_TO_DEVICE_KEY_ID:
                states = [0] * self.DIAL_COUNT
                triggered_key = self.KEY_DEVICE_ID_TO_DIAL_TURN_LEFT_NUM[triggered_raw_key]
                states[triggered_key] = -1
                return {
                    ControlType.DIAL: {
                        DialEventType.TURN : states
                    }
                }

            elif triggered_raw_key in self.DIAL_TURN_RIGHT_NUM_TO_DEVICE_KEY_ID:
                states = [0] * self.DIAL_COUNT
                triggered_key = self.KEY_DEVICE_ID_TO_DIAL_TURN_RIGHT_NUM[triggered_raw_key]
                states[triggered_key] = +1
                return {
                    ControlType.DIAL: {
                        DialEventType.TURN : states
                    }
                }

        # we don't know how to handle the response
        return None

    def reset(self):
        super().reset()
        # flush. Needed for V2 Miraboxes
        payload = self._make_payload_for_report_id(0x00, Mirabox.CMD_PREFIX + Mirabox.CRT_STP)
        self.device.write(payload)

    def set_key_image(self, key, image):
        if min(max(key, 0), self.KEY_COUNT) != key:
            raise IndexError("Invalid key index {}.".format(key))

        key = self.KEY_NUM_TO_DEVICE_KEY_ID[key]
        image = bytes(image or self.BLANK_KEY_IMAGE)
        self._set_raw_key_image(key, image)

    def set_secondary_image(self, key, image):
        pass

    def set_screen_image(self, image):
        pass