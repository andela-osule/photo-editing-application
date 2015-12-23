import mock
from app.models import SocialUser, Photo, Share
from app.forms import PhotoForm
from app.views import AppView, DownloadView, UploadPhotoView, JSONFxListView, \
    UpdatePhotoTitleView, DestroyPhotoView, ShareView
from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import TestCase, Client, RequestFactory

user = SocialUser.objects.create_user(
            name='John Doe',
            profile_url='http://someplace_on_the_www',
            id=2,
        )

mock_file = mock.MagicMock(spec=File, name="mockphoto.jpg")


class AppTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = user
        cls.reqfactory = RequestFactory()
        cls.mock_file = mock_file
        cls.mock_file.name = "mockphoto.jpg"
        cls.user.save()
        super(AppTestCase, cls).setUpClass()

    def setUp(self):
        self.client = Client()

    def test_can_get_sitemap_in_app_root(self):
        '''Test that sitemap.xml can be accessed'''
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)

    def test_can_get_robots_in_app_root(self):
        '''Test that robots.txt file can be accessed'''
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)

    def test_can_get_humans_in_app_root(self):
        '''Test that humans.txt file can be accessed'''
        response = self.client.get('/humans.txt')
        self.assertEqual(response.status_code, 200)

    def test_guest_can_access_login_page(self):
        '''Test that guest can access login page'''
        response = self.client.get(reverse('app.auth.login'))
        self.assertEqual(response.status_code, 200)

    def test_auth_user_can_logout(self):
        '''Test that authenticated user can logout'''
        response = self.client.get(reverse('app.auth.logout'))
        self.assertRedirects(
            response,
            reverse('app.auth.login'),
            status_code=302
        )

    def test_guest_cannot_access_index_page(self):
        '''Test that guest can not have unauthorised access to app root
        '''
        response = self.client.get(reverse('app.index'))
        self.assertEqual(response.status_code, 302)

    def test_users_can_view_privacy_policy(self):
        '''Test that users can view privacy policy'''
        response = self.client.get(reverse('app.privacy'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_view_photos(self):
        '''Test that user can view photos'''
        req = self.reqfactory.get(reverse('app.index'))
        req.user = self.user
        AppView.as_view()(req)

    @mock.patch('app.models.Share.save')
    @mock.patch('app.views.open', return_value=mock_file)
    @mock.patch('mimetypes.guess_type')
    @mock.patch('app.models.Share.objects.get_queryset')
    def test_user_can_download_photo(self, mock_save, mock_open, mock_guess_type, mock_get):
        '''Test that user can download photo'''
        share = Share.objects.create(
            uri='-_-', src=':0:.png', 
            user=self.user, downloads=0,
        )
        share.save()
        req = self.reqfactory.get(reverse('app.fileserve')+"?uri=-_-")
        req.user = self.user
        response = DownloadView.as_view()(req)
        self.assertEqual(response.status_code, 200)
    
    @mock.patch('app.models.Photo.objects.get')
    def test_user_can_delete_photo(self, mock_get):
        '''Test that user can delete photo'''
        req = self.reqfactory.get(reverse('app.photo.destroy', kwargs={'photo_id':1}))
        req.user = self.user
        response = DestroyPhotoView.as_view()(req, 1)
        self.assertTrue(Photo.objects.get.called)
    
    @mock.patch('app.models.Share.get_photo')
    def test_user_can_share_photo(self, mock_get_photo):
        '''Test that user can share photo'''
        req = self.reqfactory.get(reverse('app.photo.share'))
        req.user = self.user
        ShareView.as_view()(req)
        self.assertTrue(Share.get_photo.called)

    @mock.patch('app.models.Photo.objects.get', return_value={})
    @mock.patch('app.models.Photo.update')
    @mock.patch('app.models.Photo.get_for_user', return_value=[{'photo':'hfdfskfd.jpg'}])
    def test_user_can_update_photo_title(self, mock_get, mock_update, mock_get_for_user):
        '''Test that user can update photo title'''
        req = self.reqfactory.post(
            reverse('app.photo.update', kwargs={'photo_id': 1}),
            data='{"title":"new title"}', content_type='application/json')
        req.user = self.user
        response = UpdatePhotoTitleView.as_view()(req, 1)
        self.assertIn('success', response.content)

    @mock.patch('app.models.Photo', return_value={'title':'o_o', 'image':'o>o'})
    @mock.patch('app.forms.PhotoForm.save')
    @mock.patch('PIL.Image')
    @mock.patch('app.models.Photo.get_for_user', return_value=[{'image':'hfdfskfd.jpg'}])
    def test_user_can_upload_photo(self, mock_photo, mock_form, mock_pil, mock_get_for_user):
        '''Test that user can upload photo'''
        req = self.reqfactory.post(
            reverse('app.photo.upload'),
            data = {
                'image': self.mock_file,
                'title': 'mock_file'
            }
        )
        req.user = self.user
        UploadPhotoView.as_view()(req)
        self.assertTrue(PhotoForm.save.called)

    def test_can_get_all_effects(self):
        '''Test that user can get all effects'''
        req = self.reqfactory.get(reverse('app.availablefx'))
        req.user = self.user
        resp = JSONFxListView.as_view()(req)
        self.assertIn('Content-Type: application/json', resp.serialize())

    @classmethod
    def tearDownClass(cls):
        super(AppTestCase, cls).tearDownClass()
