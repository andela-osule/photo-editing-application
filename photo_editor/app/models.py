import os
from PIL import Image
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
THUMBNAIL_SIZE = 80, 80


class SocialUser(AbstractBaseUser):
    '''This model extends the AbstractBaseUser class, serving
    as a data store for authenticated users.
    '''
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


class Photo(models.Model):
    '''This model represents a Photo record
    belonging to a user. The user can have
    many records.
    '''
    image = models.CharField(max_length=512)
    thumbnail = models.CharField(max_length=255, default='', blank=True)
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
                'thumbnailSrc': photo.thumbnail,
                'src': photo.image,
                'edited_at': photo.edited_at.isoformat(),
                'id': photo.id,
            } for photo in user_photos
        ]

    @staticmethod
    def set_thumbnail(photos):
        '''Generates thumbnail images from an uploaded image.
        '''
        for photo in photos:
            filename, ext = os.path.splitext(photo.image)
            im = Image.open(os.path.join(settings.BASE_DIR, photo.image))
            im.thumbnail(THUMBNAIL_SIZE)
            thumbnail_src = "{0}.thumbnail{1}".format(
                os.path.join(settings.BASE_DIR, filename), ext
            )
            photo.thumbnail = os.path.relpath(thumbnail_src, settings.BASE_DIR)
            im.save(thumbnail_src)

    def update(self, form_data):
        '''Updates a photo record'''
        self.title = form_data.get('title')
        self.save()
        return self.edited_at
