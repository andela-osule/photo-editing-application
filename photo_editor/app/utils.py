import os
from PIL import Image
from facebook import GraphAPI
from django.conf import settings
from django.utils.text import slugify
from PIL import ImageFilter as PIL_ImageFilter
from proxy import ImageFilterProxy, defaults


ImageFilter = ImageFilterProxy(PIL_ImageFilter, defaults)


class Fx(object):
    def __init__(self, image_url, fx):
        '''Creates an object effect applyable'''
        self.im = Image.open(os.path.join(settings.BASE_DIR, image_url))
        self.FILTER = fx

    def apply(self):
        '''Applies an image effect'''
        filename = self.im.filename
        if self.FILTER in settings.PHOTO_FX_BASIC:
            self.im = do(self.FILTER, on=self.im, type="basic")
        if self.FILTER in settings.PHOTO_FX_ADVANCED:
            self.im = do(self.FILTER, on=self.im, type="advanced")
        self.filename = filename
        return self


class Storage(object):
    '''Manages image pertaining to the user'''
    UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'static', 'uploads')

    @staticmethod
    def upload(request):
        '''Uploads user image
        returns: image upload path
        '''
        if not os.path.exists(Storage.UPLOAD_DIR):
            os.makedirs(Storage.UPLOAD_DIR)
        user_upload_dir = os.path.join(
            Storage.UPLOAD_DIR, str(request.user.id)
        )
        if not os.path.exists(user_upload_dir):
            os.makedirs(user_upload_dir)
        im = request.FILES.get('image')
        im_path = os.path.join(user_upload_dir, im.name)
        im.file.seek(0)
        try:
            open(im_path, 'wb').write(im.file.read())
        except:
            raise IOError
        return os.path.relpath(im_path, settings.BASE_DIR)

    @staticmethod
    def delete(request):
        """deletes user image
        returns: boolean
        """
        pass

    @staticmethod
    def save(request, fx):
        '''Saves an effect applied on an image
        return: effected_im_source
        '''
        filename, ext = os.path.splitext(fx.filename)
        effected_im_src = "{0}.{1}{2}".format(
            filename, fx.FILTER, ext
        )
        fx.im.save(effected_im_src)
        return os.path.relpath(effected_im_src, settings.BASE_DIR)


def do(filter, on, type):
    filter = slugify(filter).upper().replace('-', '_')
    if type == 'basic':
        return on.filter(getattr(ImageFilter, filter))
    if type == 'advanced':
        print "yay"
        if on.mode != "L":
            on = on.convert("L")
        on.putpalette(getattr(ImageFilter, filter))
        on = on.convert("RGB")
        return on


def publish(user, share_uri):
    '''public url to facebook'''
    ga = GraphAPI(user.access_token)
    import pdb; pdb.set_trace()
