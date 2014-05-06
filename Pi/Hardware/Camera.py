from datetime import datetime
import io

import numpy as np
import Image
import cv2
import PiCamera


_core = None
_flag_initialised = False
_last_picture = None                    # Last taken picture (PIL object)
_last_picture_pil = None
_camera = PiCamera.PiCamera()
_cam_height = 500
_cam_width = 666


def initialise(core):
    global _core, _flag_initialised

    _core = core
    _flag_initialised = True
    _camera.resolution = (_cam_width, _cam_height)


def take_picture():
    """
    Takes a picture with a resolution in function of the height
    """
    global _core, _flag_initialised, _last_picture, _camera, _cam_width, _cam_height

    _last_picture = None
    if _flag_initialised:
        try:
            #height = _core.get_height()
            #image_height = min(max_height, int(base_height + (max_height - base_height) * (height / maximum_height)))
            #image_width = min(max_width, int(base_width + (max_width - base_width) * (height / maximum_height)))
            stream = io.BytesIO()
            print 'hey'
            _camera.capture(stream, format='jpeg')
            data = np.fromstring(stream.getvalue(), dtype=np.uint8)
            _last_picture = cv2.imdecode(data, 1)
            print 'heya'
            _core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Took a picture")
        except Exception as e:
            print e
            return _last_picture
    return _last_picture


def take_picture_pil():
    """
    Takes a picture with a resolution in function of the height
    """
    global _core, _flag_initialised, _last_picture_pil, _camera

    cv2_im = cv2.cvtColor(_last_picture, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv2_im)
    return pil_im

# ------------------------------------------------- GETTERS
def get_last_picture():
    global _last_picture

    return _last_picture
