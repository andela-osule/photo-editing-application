from django.shortcuts import render, redirect, render_to_response
from django.core.urlresolvers import reverse
from django.views.generic import View
from settings.base import FB_APP_ID, FB_SCOPE, FB_APP_SECRET
from facebook import get_user_from_cookie, GraphAPI

class RootFilesView(View):
    """Renders requests for `sitemap.xml`, `robots.txt` and `humans.txt`"""

    def get(self, request, *args, **kwargs):
        """Returns response for `GET` request to the website root"""
        filename = self.kwargs.get('filename')
        return render(
            request, filename,
            {'page_title': filename}, content_type="text/plain"
        )


class AuthView(View):
    """Handles User authentication"""
    
    def get(self, request):
        """Handles `GET` request to the login route"""
        
        # Ensure that user has been authenticated before granting access to
        # login
        if request.user.is_authenticated():
            return redirect(reverse('app.index'))
        
        context = {
            'app_id': FB_APP_ID,
            'allow_perms': ','.join(FB_SCOPE),
        }

        return render(request, 'app/login.html', context)
    
class AppView(View):
    """Parley all requests that boister app functions
    """

    def get(self, request):
        if not request.user.is_authenticated():
            return redirect(reverse('app.auth.login'))
        
        return render(request, 'app/index.html')
