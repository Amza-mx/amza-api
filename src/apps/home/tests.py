from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class HomeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.url = reverse('home:index')

    def test_redirect_to_login_when_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_view_loads_with_authentication(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/index.html')

    def test_context_contains_stats(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertIn('stats', response.context)
        stats = response.context['stats']

        # Verify all expected stat keys are present
        expected_keys = [
            'total_analyses',
            'recent_analyses',
            'feasible_products',
            'total_brands',
            'allowed_brands',
            'blocked_brands',
            'usa_products',
            'mx_products',
        ]
        for key in expected_keys:
            self.assertIn(key, stats)
            self.assertIsInstance(stats[key], int)

    def test_template_renders_navigation_cards(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        content = response.content.decode('utf-8')

        # Check for key navigation links
        self.assertIn('/pricing-analysis/panorama/', content)
        self.assertIn('/pricing-analysis/batch/', content)
        self.assertIn('/pricing-analysis/brands/', content)
        self.assertIn('/admin/', content)
        self.assertIn('/api/v1/', content)
