from datetime import datetime
import io

import Image

import PiCamera
from values import *


_core = None
_flag_initialised = False
_last_picture = None                    # Last taken picture (PIL object)
_camera = PiCamera.PiCamera()

def initialise(core):
    global _core, _flag_initialised

    _core = core
    _flag_initialised = True


def take_picture():
    """
    Takes a picture with a resolution in function of the height
    """
    global _core, _flag_initialised, _last_picture, _camera

    _last_picture = None
    if _flag_initialised:

        #height = _core.get_height()
        #image_height = min(max_height, int(base_height + (max_height - base_height) * (height / maximum_height)))
        #image_width = min(max_width, int(base_width + (max_width - base_width) * (height / maximum_height)))
        _camera.resolution = (cam_resolution, cam_resolution)
        stream = io.BytesIO()
        _camera.capture(stream, format='jpeg')
        stream.seek(0)
        _last_picture = Image.open(stream)

        _core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Took a picture")

    return _last_picture

# ------------------------------------------------- GETTERS

def get_last_picture():
    global _last_picture

    return _last_picture
