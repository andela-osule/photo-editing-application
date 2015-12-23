import os
from PIL import Image
from django.conf import settings
from django.utils.text import slugify
from PIL import ImageFilter as PIL_ImageFilter
from proxy import ImageFilterProxy, defaults


ImageFilter = ImageFilterProxy(PIL_ImageFilter, defaults)


class Fx(object):
    def __init__(self, photo, fx):
        '''Creates an object effect applyable'''
        self.photo = Image.open(photo.image)
        self.filename = photo.image.path
        self.FILTER = fx

    def apply(self):
        '''Applies an image effect'''
        if self.FILTER in settings.PHOTO_FX_BASIC:
            self.photo = do(self, "basic")
        if self.FILTER in settings.PHOTO_FX_ADVANCED:
            self.photo = do(self, "advanced")
        return self


class Storage(object):
    '''Manages image pertaining to the user'''
    UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'static', 'uploads')

    @staticmethod
    def delete(request):
        """deletes user image
        returns: boolean
        """
        pass

    @staticmethod
    def save(request, on):
        '''Saves an effect applied on an image
        return: effected_im_source
        '''
        filename, ext = os.path.splitext(on.filename)
        filtered_photo_path = "{0}.{1}{2}".format(
            filename, on.FILTER, ext
        )
        on.photo.save(filtered_photo_path)
        return os.path.relpath(filtered_photo_path, settings.BASE_DIR)


def do(on, type):
    filter = slugify(on.FILTER).upper().replace('-', '_')
    if type == 'basic':
        return on.photo.filter(getattr(ImageFilter, filter))
    if type == 'advanced':
        if on.photo.mode != "L":
            on = on.photo.convert("L")
        on.putpalette(getattr(ImageFilter, filter))
        on = on.convert("RGB")
        return on
