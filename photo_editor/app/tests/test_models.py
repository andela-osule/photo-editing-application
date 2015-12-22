from app.models import Share, SocialUser
from django.test import TestCase
from mock import Mock


class ShareModelTest(TestCase):
    '''Test share model'''
    def setUp(self):
        user = Mock(spec=SocialUser)
        user.save = Mock(return_value=None)
        user.objects.create = Mock(return_value=None)
        user.objects.create(username='John Doe', password='impossible')
        self.user = user

    def test_can_create_share_link(self):
        share = Mock(spec=Share)
        share.save = Mock(return_value=None)
        share.return_value.Share = Mock(return_value=None)
        share.this(src='image.jpg', owner=self.user)
        share.save.assert_has_calls([])
