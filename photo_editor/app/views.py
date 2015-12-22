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
        'ERROR': 'Photo failed to upload at this time.',
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
        'ERROR': 'Photo does not exist',
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
        'ERROR': 'Photo failed to upload at this time.',
        'SUCCESS': 'Photo successfully submitted for upload',
    }

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(UploadPhotoView, self).dispatch(*args, **kwargs)

    def post(self, request):
        user_id = request.user.id
        title = request.POST.get('title', '')
        image = Storage.upload(request)
        mesgs = dict()
        photo_form = PhotoForm(
            {'image': image, 'title': title, 'user': user_id}
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


class UpdatePhotoTitleView(View):
    '''Updates the photo title'''
    MSGS = {
        'ERROR': 'Photo title couldn\'t be updated',
        'SUCCESS': 'Photo title has been updated successfully',
    }

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(UpdatePhotoTitleView, self).dispatch(*args, **kwargs)

    def post(self, request, photo_id):
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
    '''Returns JSON of available effects'''
    def get(self, request):
        filters = settings.PHOTO_FX_BASIC + settings.PHOTO_FX_ADVANCED
        response_data = {
            'fxCollection': [
                {'name': fx} for fx in filters
            ]
        }
        return JsonResponse(response_data)


class JSONFxApplyView(View):
    '''Applies an effect and returns a base 64 data uri in JSON response'''
    def get(self, request, photo_id, fx):
        photo = Photo.objects.get(id=photo_id)
        effected_im = Fx(photo.image, fx).apply()
        effected_im_src = Storage.save(request, effected_im)
        response_data = {'fxSrc': effected_im_src}
        return JsonResponse(response_data)


class ShareView(View):
    '''Shares a photo URI'''

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ShareView, self).dispatch(*args, **kwargs)

    def get(self, request):
        uri = request.GET.get('uri')
        photo = Share.get_photo(uri)
        return render(request, 'app/photo.html', {'photo': photo})

    def post(self, request):
        body = loads(request.body)
        share = Share.this(request.user, body.get('src'))
        response_data = {
            'status': 'done', 'uri': share.uri,
            'photo': share.src,
            'APP_ID': settings.FB_APP_ID
        }
        return JsonResponse(response_data)


class PrivacyView(View):
    def get(self, request):
        return render(request, 'app/privacy.html')


class DownloadView(View):
    def get(self, request):
        uri = request.GET.get('file')
        photo = get_object_or_404(Share, uri=uri)
        try:
            mimetypes.init()
            file_path = os.path.join(settings.BASE_DIR, photo.src)
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
