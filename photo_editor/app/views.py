import os
import mimetypes
from json import loads
from .models import Photo, Share
from .utils import Storage, Fx
from .forms import PhotoForm
from django.conf import settings
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound


class RootFilesView(View):
    '''A view class that responds to requests for `sitemap.xml`,
     `robots.txt` and `humans.txt`'''

    def get(self, request, *args, **kwargs):
        '''Returns response for `GET` request to the website root'''
        filename = self.kwargs.get('filename')
        return render(
            request, filename,
            {'page_title': filename}, content_type="text/plain"
        )


class AuthView(View):
    '''A view class that handles user authentication'''

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
    '''A view class that de-authenticates a user'''
    
    def get(self, request):
        '''Handles the de-authentication of a user'''
        request.session.flush()
        request.COOKIES = {
            k: v for k, v in request.COOKIES.iteritems()
            if not k.startswith('fbsr_')
        }
        return redirect(reverse('app.auth.login'))


class AppView(View):
    '''A view class that generates the user dashboard'''
    MSGS = {
        'ERROR': 'Photo failed to upload at this time.',
        'SUCCESS': 'Photo successfully submitted for upload',
    }

    def get(self, request):
        '''Parley all requests that boister app functions'''
        context = {}
        if not request.user.is_authenticated():
            return redirect(reverse('app.auth.login'))
        else:
            context['photos'] = Photo.objects.filter(user=request.user)
        return render(request, 'app/index.html', context)


class JSONPhotosView(View):
    '''A view class that photos belonging to authenticated user as JSON
    '''
    def get(self, request):
        '''Returns photos belonging to authenticated user as JSON'''
        serialized_photos = {'photos': Photo.get_for_user(request.user)}
        return JsonResponse(serialized_photos, safe=False)


class DestroyPhotoView(View):
    '''A view class that deletes photo from the database'''
    MSGS = {
        'ERROR': 'Photo does not exist',
        'SUCCESS': 'Photo was deleted successfully',
    }

    def get(self, request, photo_id):
        '''Handles the deletion of user photo'''
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
    '''A view class that uploads photo to the database'''
    MSGS = {
        'ERROR': 'Photo failed to upload at this time.',
        'SUCCESS': 'Photo successfully submitted for upload',
    }

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        '''Exempt class methods from csrf verification'''
        return super(UploadPhotoView, self).dispatch(*args, **kwargs)

    def post(self, request):
        '''Upload the user's photo '''
        mesgs = dict()
        photo_form = PhotoForm(
            request.POST, request.FILES
        )
        if photo_form.files['image'].size < settings.MAX_UPLOAD_SIZE:
            if photo_form.is_valid():
                photo_form = photo_form.save(commit=False)
                mesgs['tags'] = 'success'
                mesgs['text'] = UploadPhotoView.MSGS['SUCCESS']
                photo_form.title = request.POST.get('title', '')
                photo_form.user = request.user
                photo_form.save()
            uploaded_photo = Photo.get_for_user(request.user, latest=True)
        else:
            mesgs['tags'] = 'danger'
            mesgs['text'] = UploadPhotoView.MSGS['ERROR']
        response_data = {'messages': mesgs, 'photo': uploaded_photo.pop()}
        return JsonResponse(response_data)


class UpdatePhotoTitleView(View):
    '''Updates the photo title'''
    MSGS = {
        'ERROR': 'Photo title couldn\'t be updated',
        'SUCCESS': 'Photo title has been updated successfully',
    }

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        '''Exempts class methods from csrf verification'''
        return super(UpdatePhotoTitleView, self).dispatch(*args, **kwargs)

    def post(self, request, photo_id):
        '''Updates photo title'''
        mesgs = dict()
        request.POST = loads(request.body)
        request.POST['user'] = request.user.id
        request.POST['title'] = request.POST.get('title', 'Set title')
        try:
            edited_at = Photo.objects.get(id=photo_id).update(request.POST)
            mesgs['tags'] = 'success'
            mesgs['text'] = UpdatePhotoTitleView.MSGS['SUCCESS']
        except:
            mesgs['tags'] = 'danger'
            mesgs['text'] = UpdatePhotoTitleView.MSGS['ERROR']
        response_data = {'messages': mesgs, 'edited_at': edited_at}
        return JsonResponse(response_data)


class JSONFxListView(View):
    '''A view class that returns JSON of available effects'''

    def get(self, request):
        '''Get available list of filters'''
        filters = settings.PHOTO_FX_BASIC + settings.PHOTO_FX_ADVANCED
        response_data = {
            'fxCollection': [
                {'name': fx} for fx in filters
            ]
        }
        return JsonResponse(response_data)


class JSONFxApplyView(View):
    '''A view class that applies an effect to a photo'''

    def get(self, request, photo_id, fx):
        '''Applies a photo effect'''
        photo = Photo.objects.get(id=photo_id)
        effected_im = Fx(photo, fx).apply()
        effected_im_src = Storage.save(request, effected_im)
        response_data = {'filteredPhotoURI': effected_im_src}
        return JsonResponse(response_data)


class ShareView(View):
    '''Shares a photo URI'''

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        '''Exempts class methods from csrf verification'''
        return super(ShareView, self).dispatch(*args, **kwargs)

    def get(self, request):
        '''Renders photo sharing page'''
        uri = request.GET.get('uri')
        photo = Share.get_photo(uri)
        return render(request, 'app/photo.html', {'photo': photo})

    def post(self, request):
        '''Generates share url'''
        body = loads(request.body)
        share = Share.this(request.user, body.get('src'))
        response_data = {
            'status': 'done', 'uri': share.uri,
            'photo': share.src,
            'APP_ID': settings.FB_APP_ID
        }
        return JsonResponse(response_data)


class PrivacyView(View):
    '''A view class for the privacy policy page'''

    def get(self, request):
        '''Renders privacy policy'''
        return render(request, 'app/privacy.html')


class DownloadView(View):
    '''A view class for photo download'''
    def get(self, request):
        '''Returns the file for download'''
        uri = request.GET.get('file')
        photo = get_object_or_404(Share, uri=uri)
        try:
            mimetypes.init()
            file_path = os.path.join(
                settings.BASE_DIR, photo.src[1:]
            )
            file_name = os.path.basename(file_path)
            mtype = mimetypes.guess_type(file_name)
            fsock = open(file_path, "rb")
            photo.downloads += 1
            photo.save()
            response = HttpResponse(fsock, content_type=mtype[0])
            response['Content-Disposition'] = 'attachment;filename='\
                + file_name
        except:
            return HttpResponseNotFound('Photo not found')
        return response
