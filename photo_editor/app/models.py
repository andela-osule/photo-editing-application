from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.http import request

class SocialUser(AbstractBaseUser):
    name = models.CharField(null=False, max_length=256, default='')
    profile_url = models.TextField(null=True)
    access_token = models.TextField(null=True)
    id = models.BigIntegerField(unique=True, primary_key=True)
    USERNAME_FIELD = 'id'
    
    def has_valid_access_token(self, token):
        """Affirms that the user has a valid access token
        """
        return self.access_token == token

    def is_authenticated(self):
        """Affirms that the user is authenticated"""
        return self.active
