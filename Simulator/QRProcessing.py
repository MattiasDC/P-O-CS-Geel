from base64 import b64decode
from base64 import b64encode
import qrcode
import zbar
import rsa
#import Image
import io


class QRProcessing(object):
    _public = None                  # Public key
    _private = None                     # Private key
    _bits = 512                         # Key encryption size

    _error_correction_code = 'L'        # QR error code

    def __init__(self):
        self._public, self._private = rsa.newkeys(self._bits)

    def get_public_key(self):
        return self._public

    def get_public_key_pem(self):
        return self._public.save_pkcs1(format='PEM')

    def decrypt(self, message):
        if message is None:
            return None
        try:
            return rsa.decrypt(message, self._private)
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
        return _last_qr

    def decrypt_pil(self, pil):
        qr_string = self._decode_pil(pil)
        if not qr_string is None:
            return self.decrypt(b64decode(qr_string))
            print 'decryption failed'
        return None



