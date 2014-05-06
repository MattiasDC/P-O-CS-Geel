from base64 import b64decode
from base64 import b64encode
import qrcode
import zbar
from PIL import Image
import io
from Crypto.PublicKey import RSA




class QRProcessing(object):
    key = None
    pub_key = None                    # Private key
    _bits = 512                         # Key encryption size

    _error_correction_code = 'L'        # QR error code

    def __init__(self):
        self.key = RSA.generate(1024, e=5)
        self.pub_key = self.key.publickey().exportKey("PEM")

    def decrypt(self, message):
        if message is None:
            return None
        try:
            return self.key.decrypt(b64decode(message))
        except Exception:
            return None

    def _decode_pil(self, pil):
        scanner = zbar.ImageScanner()
        scanner.parse_config('enable')

        pil = pil.convert(self._error_correction_code)
        width, height = pil.size
        # wrap image data
        image = zbar.Image(width, height, 'Y800', pil.tostring())
        # scan the image for barcodes
        result = scanner.scan(image)

        _last_qr = None
        if result == 0:
            print "No QR codes found"
        else:
            for symbol in image:
                # Zbar scans the image from bottom to top -> all qr codes are found if they can be read BUT when
                # multiple QR codes on a picture it is less accurate (doesn't find hard to read QR codes)
                _last_qr = symbol.data
                print _last_qr

        # cleanup
        del image
        return _last_qr.strip()

    def decrypt_pil(self, pil):
        qr_string = self._decode_pil(pil)
        if not qr_string is None:
            return self.decrypt(qr_string)
        return None



