from django.conf import settings
from facebook import get_user_from_cookie, GraphAPI
from .models import SocialUser as User


class SocialBinderMiddleware():

    def process_request(self, request):
        user = request.session.get('user', None)
        # Bind user to request if user is in session
        if user:
            request.user = User.objects.get(id=user['id'])
        return

    def process_response(self, request, response):
        result = None
        # Hoo! Active cookies, verify that user cookie isn't stale
        if request.COOKIES:
            try:
                result = get_user_from_cookie(
                    cookies=request.COOKIES,
                    app_id=settings.FB_APP_ID,
                    app_secret=settings.FB_APP_SECRET
                )
            except:
                pass

        # If there is no result, we assume the user is not logged in.
        if result:
            # Check to see if this user is already in our database.
            graph = GraphAPI(result['access_token'])
            profile = dict()
            user = User.objects.filter(id=result.get('uid')).first()
            if not user:
                # User doesn't exist in datastore so get info
                profile = graph.get_object('/me')
                # Create the user and insert it into the database
                user = User(
                    id=str(profile.get('id')),
                    name=profile.get('name'),
                    profile_url=profile.get('link'),
                    access_token=result.get('access_token')
                )
            elif not user.has_valid_access_token(result.get('access_token')):
                # If an existing user, update the access token
                user.access_token = result.get('access_token')

            graph_query_result = graph.get_object('/me/picture')
            profile['link'] = graph_query_result['url']
            if user.profile_url is not profile['link']:
                user.profile_url = profile['link']

            user.active = True

            # Add the user to the current session
            request.session['user'] = dict(
                name=user.name,
                profile_url=user.profile_url,
                id=user.id,
                access_token=user.access_token,
                is_authenticated=user.is_authenticated()
            )

            user.save()
        return response
