from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractBaseUser


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
    image = CloudinaryField('image')
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
                'src': photo.image.url,
                'edited_at': photo.edited_at.isoformat(),
                'id': photo.id,
            } for photo in user_photos
        ]

    @staticmethod
    def set_thumbnail(photos):
        '''Generates thumbnail images from an uploaded image.
        '''
        for photo in photos:
            if photo.thumbnail.find('80') == -1:
                photo.thumbnail = photo.image.build_url(
                    width=80, height=80, crop='fill'
                )
                photo.save()
