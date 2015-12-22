from app.models import Share, SocialUser, Photo
from django.test import TestCase
from mock import Mock
from types import GeneratorType


class ShareModelTest(TestCase):
    '''Test share model'''
    def setUp(self):
        user = Mock(spec=SocialUser)
        user.save = Mock(return_value=None)
        user.objects.create = Mock(return_value=None)
        user.name = 'John Doe'
        user.username = 'johndoe'
        user.password = 'impossible'
        user._state = Mock()
        self.user = user

    def test_can_create_share_link(self):
        '''Test that the user can share a link'''
        share = Mock(spec=Share)
        share.save = Mock(return_value=None)
        share.return_value.Share = Mock(return_value=None)
        share.this(src='image.jpg', owner=self.user)
        share.save.assert_has_calls([])

    def test_can_generate_random_word(self):
        '''Test that the user can generate a random word'''
        share = Share.random_word()
        self.assertIsNotNone(share)
        self.assertIsInstance(share, GeneratorType)

    def test_can_get_photo(self):
        '''Test that the user can get a photo'''
        uri = 'randomword'
        share = Mock(spec=Share)
        share.get_photo = Mock(return_value=Share())
        photo = share.get_photo(uri=uri)
        self.assertIsInstance(photo, Share)


class PhotoModelTest(TestCase):
    '''Test photo model'''
    def setUp(self):
        user = Mock(spec=SocialUser)
        user.save = Mock(return_value=None)
        user.objects.create = Mock(return_value=None)
        user.objects.create(username='John Doe', password='impossible')
        self.user = user

    def test_can_create_photo(self):
        '''Test that the user can create a photo'''
        mock_file = Mock(spec=file)
        mock_photo = Mock(spec=Photo)
        photo = mock_photo(image=mock_file, user=self.user)
        photo.save = Mock(return_value=None)
        photo.save()
        self.assertIsNotNone(photo.id)
