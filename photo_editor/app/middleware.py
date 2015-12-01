from django.shortcuts import render, redirect, render_to_response
from django.core.urlresolvers import reverse
from facebook import get_user_from_cookie, GraphAPI
from settings.base import FB_APP_ID, FB_SCOPE, FB_APP_SECRET
from .models import SocialUser as User


class SocialBinderMiddleware():
    
    def process_request(self, request):
        if request.session.get('user'):
            request.user = request.session.get('user')
    
    def process_response(self, request, response):
        
        result = get_user_from_cookie(
                cookies=request.COOKIES,
                app_id=FB_APP_ID,
                app_secret=FB_APP_SECRET)

        # If there is no result, we assume the user is not logged in.
        if result:
            # Check to see if this user is already in our database.
            user = User.objects.filter(id = result.get('uid')).first()
    
            if not user:
                # Not an existing user so get info
                graph = GraphAPI(result['access_token'])
                profile = graph.get_object('me')
                # Create the user and insert it into the database
                user = User(id=str(profile.get('id')), name=profile.get('name'),
                            profile_url=profile.get('link'),
                            access_token=result.get('access_token'))
            elif not user.has_valid_access_token(result.get('access_token')):
                # If an existing user, update the access token
                user.access_token = result.get('access_token')
    
            # Add the user to the current session
            response.session['user'] = dict(name=user.name,
                                           profile_url=user.profile_url,
                                           id=user.id,
                                           access_token=user.access_token)

            user.save()
        return response
