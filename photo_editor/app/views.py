from .models import Photo
from .forms import PhotoForm
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect


class RootFilesView(View):
    '''Renders requests for `sitemap.xml`, `robots.txt` and `humans.txt`'''

    def get(self, request, *args, **kwargs):
        '''Returns response for `GET` request to the website root'''
        filename = self.kwargs.get('filename')
        return render(
            request, filename,
            {'page_title': filename}, content_type="text/plain"
        )


class AuthView(View):
    '''Handles User authentication'''

    def get(self, request):
        '''Handles `GET` request to the login route'''

        # Ensure that user has been authenticated before granting access to
        # login

        if request.user.is_authenticated():
            return redirect(reverse('app.index'))

        context = {
            'app_id': settings.FB_APP_ID,
            'allow_perms': ','.join(settings.FB_SCOPE),
        }

        return render(request, 'app/login.html', context)


class DeAuthView(View):

    '''De-authenticates user'''
    def get(self, request):
        '''Handle the de-authentication of a user'''
        request.session.flush()
        request.COOKIES = {
            k: v for k, v in request.COOKIES.iteritems()
            if not k.startswith('fbsr_')
        }
        return redirect(reverse('app.auth.login'))


class AppView(View):
    MSGS = {
        'SUCCESS': 'Photo successfully submitted for upload',
        'ERROR': 'Photo failed to upload at this time.'
    }

    '''Parley all requests that boister app functions'''

    def get(self, request):
        context = {}
        if not request.user.is_authenticated():
            return redirect(reverse('app.auth.login'))
        else:
            context['photos'] = Photo.objects.filter(user=request.user)
        return render(request, 'app/index.html', context)

    def post(self, request):
        '''Upload files to Cloudinary'''
        request.POST['user'] = request.user.id
        request.POST['title'] = ''
        photo_form = PhotoForm(
            request.POST,
            request.FILES,
        )
        if photo_form.is_valid():
            messages.add_message(
                request, messages.SUCCESS, AppView.MSGS['SUCCESS']
            )
            photo_form.save()
        else:
            messages.add_message(
                request, messages.ERROR, AppView.MSGS['ERROR']
            )
        return redirect(reverse('app.index'))


class JSONPhotosView(View):
    def get(self, request):
        serialized_photos = Photo.get_for_user(request.user)
        return JsonResponse(serialized_photos, safe=False)
