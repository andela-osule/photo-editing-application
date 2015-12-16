import os
from django.conf import settings
from PIL import Image, ImageFilter
from django.utils.text import slugify


class Fx(object):
    def __init__(self, image_url, fx):
        '''Creates an object effect applyable'''
        self.FILTER = slugify(fx).upper().replace('-', '_')
        self.im = Image.open(os.path.join(settings.BASE_DIR, image_url))

    def apply(self):
        '''Applies an image effect'''
        filename = self.im.filename
        print self.FILTER
        self.im = self.im.filter(getattr(ImageFilter, self.FILTER))
        self.im.filename = filename
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
        # import pdb; pdb.set_trace()
        filename, ext = os.path.splitext(fx.im.filename)
        effected_im_src = "{0}.{1}{2}".format(
                filename, fx.FILTER, ext
        )
        fx.im.save(effected_im_src)
        return os.path.relpath(effected_im_src, settings.BASE_DIR)
