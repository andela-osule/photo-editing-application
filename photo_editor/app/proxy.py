from PIL import ImageFilter


class ALIEN(ImageFilter.MedianFilter):
    name = "Alien"

    def __init__(self):
        self.size = 5
        self.rank = 0


class BLURMORE(ImageFilter.GaussianBlur):
    name = "Blur more"

    def __init__(self):
        self.radius = 4


class BRIGHTEN(ImageFilter.BuiltinFilter):
    name = "Brighten"
    filterargs = (3, 3), 16, 0, (
        -2, -24, -2,
        -2, 64, -2,
        -2, 16, -2
    )


class SHARPENMORE(ImageFilter.BuiltinFilter):
    name = "Sharpen more"
    filterargs = (3, 3), 11, 0, (
        -2, -2, -2,
        -2, 32, -2,
        -2, -2, -2,
    )


def make_linear_ramp(white):
    # putpalette expects [r,g,b,r,g,b,...]
    ramp = []
    r, g, b = white
    for i in xrange(255):
        ramp.extend((r * i / 255, g * i / 255, b * i / 255))
    return ramp


def make_grayscale(color):
    ramp = []
    r, g, b = color
    for i in xrange(255):
        ramp.extend(((0.2989 * r), (0.5870 * g), (0.1140 * b)))
    return ramp


SEPIA = make_linear_ramp((255, 240, 192))

WHOOPS = make_linear_ramp((250, 100, 23))

GRAYSCALE = make_grayscale((100, 100, 100))

CLASS_MAP = {
    'ALIEN': ALIEN,
    'BLUR_MORE': BLURMORE,
    'BRIGHTEN': BRIGHTEN,
    'SHARPEN_MORE': SHARPENMORE,
    'SEPIA': SEPIA,
    'WHOOPS': WHOOPS,
    'GRAYSCALE': GRAYSCALE,
}


class ImageFilterProxy(object):
    '''Overlays the default property in Image module of Pillow with
    custom definition
    '''
    def __init__(self, image_filter, defaults):
        self.image_filter = image_filter
        self.defaults = defaults

    def __getattr__(self, attr):
        try:
            return getattr(self.image_filter, attr)
        except AttributeError:
            try:
                return getattr(self.defaults, attr)
            except AttributeError:
                raise AttributeError(
                    u'settings object has no attribute "%s"' % attr
                )

defaults = type('defaults', (object, ), CLASS_MAP)
