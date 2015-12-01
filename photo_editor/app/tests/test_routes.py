from django.test import TestCase, Client

class AppTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()

    def test_can_get_sitemap_in_app_root(self):
        """Test that sitemap.xml can be accessed"""
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)

    def test_can_get_robots_in_app_root(self):
        """Test that robots.txt file can be accessed"""
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)

    def test_can_get_humans_in_app_root(self):
        """Test that humans.txt file can be accessed"""
        response = self.client.get('/humans.txt')
        self.assertEqual(response.status_code, 200)
    
    def test_guest_can_access_login_page(self):
        """Test that guest can access login page"""
        response = self.client.get(reverse('app.auth.login'))
        self.assertEqual(response.status_code, 200)
