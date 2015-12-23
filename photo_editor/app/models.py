import os
import random
from PIL import Image
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.contrib.auth.models import AbstractBaseUser
THUMBNAIL_SIZE = 80, 80


class SocialUserManager(models.Manager):
    '''Manage custom user model'''
    def __init__(self, *args):
        super(SocialUserManager, self).__init__()

    def create_user(self, *args, **kwargs):
        '''Create a new user'''
        return SocialUser(**kwargs)


class SocialUser(AbstractBaseUser):
    '''This model extends the AbstractBaseUser class, serving
    as a data store for authenticated users.
    '''
    objects = SocialUserManager()
    name = models.CharField(null=False, max_length=255, default='',)
    profile_url = models.TextField(null=True)
    access_token = models.TextField(null=True)
    id = models.BigIntegerField(unique=True, primary_key=True)
    USERNAME_FIELD = 'id'
    active = models.BooleanField(default=False)

    def has_valid_access_token(self, token):
        '''Affirms that the user has a valid access token
        '''
        return self.access_token == token

    def is_authenticated(self):
        '''Affirms that the user is authenticated'''
        return self.active

    def __unicode__(self):
        return unicode(self.name)


def upload_to(instance, filename):
    '''set file uploaded to'''
    return 'static/uploads/{0}/{1}'.format(
        instance.user.id,
        filename
    )


class Photo(models.Model):
    '''This model represents a Photo record
    belonging to a user. The user can have
    many records.
    '''
    image = models.ImageField(upload_to=upload_to)
    thumbnail = models.ImageField(upload_to=upload_to, null=True)
    title = models.CharField(max_length=255, default='', blank=True)
    user = models.ForeignKey('SocialUser')
    created_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        try:
            public_id = self.url.public_id
        except AttributeError:
            public_id = ''
        return "Photo <%s:%s>" % (self.title, public_id)

    @staticmethod
    def get_for_user(user, latest=None):
        '''Returns list of photos belonging to the authenticated user.
        '''
        user_photos = Photo.objects.filter(user=user).order_by('-edited_at')
        if latest:
            user_photos = [user_photos.latest('created_at')]
        Photo.set_thumbnail(user_photos)
        return [
            {
                'title': photo.title,
                'thumbnail': photo.thumbnail.url,
                'image': photo.image.url,
                'edited_at': photo.edited_at.isoformat(),
                'id': photo.id,
            } for photo in user_photos
        ]

    @staticmethod
    def set_thumbnail(photos):
        '''Generates thumbnail images from an uploaded image.
        '''
        for photo in photos:
            filename, ext = os.path.splitext(photo.image.url)
            if not photo.thumbnail:
                im = Image.open(photo.image)
                im.thumbnail(THUMBNAIL_SIZE)
                thumbnail_path = photo.image.path[:-3] + 'thumbnail' + ext
                im.save(thumbnail_path)
                photo.thumbnail = os.path.relpath(
                    thumbnail_path, settings.BASE_DIR)
                photo.save()

    def update(self, form_data):
        '''Updates a photo record'''
        self.title = form_data.get('title')
        self.save()
        return self.edited_at


class Share(models.Model):
    '''Store public URLs.'''
    uri = models.CharField(max_length=255)
    src = models.CharField(max_length=255)
    shared_at = models.DateTimeField(auto_now=True)
    downloads = models.IntegerField(default=0)
    user = models.ForeignKey('SocialUser')

    @classmethod
    def this(cls, owner, image_src):
        '''Share a photo resource.'''
        share = cls()
        if cls.objects.filter(src=image_src).count():
            return cls.objects.get(src=image_src)
        generate = cls.random_word()
        share.src = image_src
        share.uri = generate.next()
        share.downloads = 0
        while cls.objects.filter(uri=share.uri).count():
            share.uri = cls.random_word().next()
        share.user = owner
        share.save()
        return share

    @classmethod
    def get_photo(cls, uri):
        '''Get a photo by URI'''
        share = cls.objects.get(uri=uri)
        return share

    @staticmethod
    def random_word():
        '''Generate a random word'''
        word = ''
        for i in range(8):
            word += random.choice(
                '{0}{1}{2}'.format(
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                    'abcdefghijklmnopqrstuvwxyz',
                    '0123456789')
            )
        yield word


@receiver(post_delete, sender=Photo)
def delete_from_file_system(sender, instance, **kwargs):
    '''delete from file system'''
    image_path = instance.image.path

    # split the image path into path and extension
    filepath, ext = os.path.splitext(image_path)
    # create possible file paths
    possible_filepaths = [image_path, instance.thumbnail.path]
    possible_filepaths.extend(
        map(lambda effect: '{0}.{1}{2}'.format(filepath, effect, ext),
            settings.PHOTO_FX_BASIC)
    )
    possible_filepaths.extend(
        map(lambda effect: '{0}.{1}{2}'.format(filepath, effect, ext),
            settings.PHOTO_FX_ADVANCED)
    )
    # delete files from directory
    for path in possible_filepaths:
        if os.path.exists(path):
            print path
            # delete file
            os.remove(path)
