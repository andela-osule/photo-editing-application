from .models import Photo
from .forms import PhotoForm
from django.conf import settings
from django.http import JsonResponse
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt


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
        'ERROR':   'Photo failed to upload at this time.',
        'SUCCESS': 'Photo successfully submitted for upload',
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
        pass


class JSONPhotosView(View):
    '''Returns photos belonging to authenticated user as JSON
    '''
    def get(self, request):
        serialized_photos = {'photos': Photo.get_for_user(request.user)}
        return JsonResponse(serialized_photos, safe=False)


class DestroyPhotoView(View):
    '''Deletes photo from the database'''
    MSGS = {
        'ERROR':   'Photo does not exist',
        'SUCCESS': 'Photo was deleted successfully',
    }

    def get(self, request, photo_id):
        mesgs = dict()
        try:
            photo = Photo.objects.get(id=photo_id, user=request.user)
            mesgs['tags'] = 'success'
            mesgs['text'] = DestroyPhotoView.MSGS['SUCCESS']
            photo.delete()
        except Photo.DoesNotExist:
            mesgs['tags'] = 'danger'
            mesgs['text'] = DestroyPhotoView.MSGS['ERROR']
        return JsonResponse({'messages': mesgs})


class UploadPhotoView(View):
    '''Uploads photo to the database'''
    MSGS = {
        'ERROR':   'Photo failed to upload at this time.',
        'SUCCESS': 'Photo successfully submitted for upload',
    }

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(UploadPhotoView, self).dispatch(*args, **kwargs)

    def post(self, request):
        request.POST['user'] = request.user.id
        request.POST['title'] = ''
        mesgs = dict()
        photo_form = PhotoForm(
            request.POST,
            request.FILES,
        )
        if photo_form.is_valid():
            mesgs['tags'] = 'success'
            mesgs['text'] = UploadPhotoView.MSGS['SUCCESS']
            photo_form.save()
            uploaded_photo = Photo.get_for_user(request.user, latest=True)
        else:
            mesgs['tags'] = 'danger'
            mesgs['text'] = UploadPhotoView.MSGS['ERROR']
        response_data = {'messages': mesgs, 'photo': uploaded_photo.pop()}
        return JsonResponse(response_data)
