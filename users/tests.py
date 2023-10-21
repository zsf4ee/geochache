import os
from django.test import TestCase
from .models import User, Geocache, Find, Comment
from datetime import datetime

# Ensure Django settings are configured
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

class UserTestCase(TestCase):

    def setUp(self):
        self.common_user = User.objects.create(username='cs3240.student@gmail.com', password='some_password', is_admin=False)
        self.admin_user = User.objects.create(username='cs3240.super@gmail.com', password='some_password', is_admin=True)

    def test_common_user_creation(self):
        self.assertIsInstance(self.common_user, User)
        self.assertFalse(self.common_user.is_admin)

    def test_admin_user_creation(self):
        self.assertIsInstance(self.admin_user, User)
        self.assertTrue(self.admin_user.is_admin)

class GeocacheTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test.user@gmail.com', password='test_password', is_admin=False)
        self.geocache = Geocache.objects.create(
            name='Test Geocache',
            cacher=self.user,
            cache_date=datetime.now(),
            lat=0.0,
            lng=0.0,
            description='This is a test geocache',
        )

    def test_geocache_creation(self):
        self.assertIsInstance(self.geocache, Geocache)
        self.assertEqual(self.geocache.cacher, self.user)
        self.assertFalse(self.geocache.active)

class FindTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test.user2@gmail.com', password='test_password2', is_admin=False)
        self.geocache = Geocache.objects.create(
            name='Test Geocache 2',
            cacher=self.user,
            cache_date=datetime.now(),
            lat=1.0,
            lng=1.0,
            description='This is another test geocache',
        )
        self.find = Find.objects.create(
            finder=self.user,
            geocache=self.geocache,
            timestamp=datetime.now()
        )

    def test_find_creation(self):
        self.assertIsInstance(self.find, Find)
        self.assertEqual(self.find.finder, self.user)

class CommentTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test.user3@gmail.com', password='test_password3', is_admin=False)
        self.geocache = Geocache.objects.create(
            name='Test Geocache 3',
            cacher=self.user,
            cache_date=datetime.now(),
            lat=2.0,
            lng=2.0,
            description='This is yet another test geocache',
        )
        self.comment = Comment.objects.create(
            geocache=self.geocache,
            user=self.user,
            text='This is a test comment',
            date=datetime.now()
        )

    def test_comment_creation(self):
        self.assertIsInstance(self.comment, Comment)
        self.assertEqual(self.comment.user, self.user)
