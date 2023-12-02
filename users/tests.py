import os
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from .models import User, Geocache, Find, Comment
from datetime import datetime, timedelta
from django.utils import timezone


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
            cache_date=timezone.now(),
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
            cache_date=timezone.now(),
            lat=1.0,
            lng=1.0,
            description='This is another test geocache',
        )
        self.find = Find.objects.create(
            finder=self.user,
            geocache=self.geocache,
            timestamp=timezone.now()
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
            cache_date=timezone.now(),
            lat=2.0,
            lng=2.0,
            description='This is yet another test geocache',
        )
        self.comment = Comment.objects.create(
            geocache=self.geocache,
            user=self.user,
            text='This is a test comment',
            date=timezone.now()
        )

    def test_comment_creation(self):
        self.assertIsInstance(self.comment, Comment)
        self.assertEqual(self.comment.user, self.user)

class UserUpdateTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test.update@gmail.com', password='old_password', is_admin=False)

    def test_user_update(self):
        self.user.password = 'new_password'
        self.user.save()
        updated_user = User.objects.get(username='test.update@gmail.com')
        self.assertEqual(updated_user.password, 'new_password')

class GeocacheActiveStatusTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test.user4@gmail.com', password='test_password4', is_admin=False)
        self.geocache = Geocache.objects.create(
            name='Test Geocache 4',
            cacher=self.user,
            cache_date=timezone.now(),
            lat=3.0,
            lng=3.0,
            description='Test for active status',
            active=False
        )

    def test_geocache_active_status_change(self):
        self.assertFalse(self.geocache.active)
        self.geocache.active = True
        self.geocache.save()
        self.assertTrue(Geocache.objects.get(id=self.geocache.id).active)

class UserFindCountTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test.user5@gmail.com', password='test_password5', is_admin=False)
        self.geocache = Geocache.objects.create(
            name='Test Geocache 5',
            cacher=self.user,
            cache_date=timezone.now(),
            lat=4.0,
            lng=4.0,
            description='Test for find count',
        )
        self.find = Find.objects.create(
            finder=self.user,
            geocache=self.geocache,
            timestamp=timezone.now()
        )

    def test_user_find_count_increment(self):
        initial_count = self.user.find_count
        self.user.find_count += 1
        self.user.save()
        self.assertEqual(User.objects.get(id=self.user.id).find_count, initial_count + 1)

class GeocacheDeclineTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test.user6@gmail.com', password='test_password6', is_admin=True)
        self.geocache = Geocache.objects.create(
            name='Test Geocache 6',
            cacher=self.user,
            cache_date=timezone.now(),
            lat=5.0,
            lng=5.0,
            description='Test for declining a geocache',
            declined=False
        )

    def test_geocache_decline(self):
        self.assertFalse(self.geocache.declined)
        self.geocache.declined = True
        self.geocache.reason = "Inappropriate location"
        self.geocache.save()
        updated_geocache = Geocache.objects.get(id=self.geocache.id)
        self.assertTrue(updated_geocache.declined)
        self.assertEqual(updated_geocache.reason, "Inappropriate location")

class UserEdgeCaseTests(TestCase):

    def test_user_with_long_username_password(self):
        long_username = 'u' * 300  # 300 characters long
        long_password = 'p' * 300  # 300 characters long
        user = User(username=long_username, password=long_password)
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_user_with_empty_username_password(self):
        user = User(username='', password='')
        with self.assertRaises(ValidationError):
            user.full_clean()

'''    def test_user_with_invalid_email(self):
        user = User(username='invalid-email', password='password123')
        with self.assertRaises(ValidationError):
            user.full_clean()'''

class GeocacheEdgeCaseTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test.user@gmail.com', password='test_password')
        self.default_date = timezone.now()

    def test_geocache_extreme_lat_lng(self):
        geocache = Geocache(
            name='Extreme Geocache',
            cacher=self.user,
            lat=91.0,
            lng=181.0,
            cache_date=self.default_date
        )
        with self.assertRaises(ValidationError):
            geocache.full_clean()

    def test_geocache_past_date(self):
        past_date = self.default_date - timedelta(days=365)
        geocache = Geocache.objects.create(
            name='Past Geocache',
            cacher=self.user,
            lat=0.0,
            lng=0.0,
            cache_date=past_date
        )
        self.assertLess(geocache.cache_date, timezone.now())

    '''def test_geocache_empty_name_description(self):
        # Provide default values for lat and lng
        with self.assertRaises(ValidationError):
            Geocache.objects.create(
                name='',
                description='',
                cacher=self.user,
                lat=0.0,
                lng=0.0,
                cache_date=self.default_date
            )'''

class FindEdgeCaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test.finder@gmail.com', password='password')
        self.geocache = Geocache.objects.create(name='Test Geocache', cacher=self.user)

    def test_find_future_timestamp(self):
        future_timestamp = timezone.now() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            Find.objects.create(finder=self.user, geocache=self.geocache, timestamp=future_timestamp)

    def test_find_nonexistent_user_geocache(self):
        with self.assertRaises(ValidationError):
            Find.objects.create(finder=None, geocache=None)

    def test_user_finding_same_geocache_multiple_times(self):
        Find.objects.create(finder=self.user, geocache=self.geocache)
        with self.assertRaises(IntegrityError):
            Find.objects.create(finder=self.user, geocache=self.geocache)

'''class UserFindCountEdgeCaseTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test.findcount@gmail.com', password='password')
        self.geocache = Geocache.objects.create(name='Test Geocache for FindCount', cacher=self.user)

    def test_incrementing_find_count_high(self):
        self.user.find_count = 10000
        self.user.save()
        self.assertEqual(User.objects.get(id=self.user.id).find_count, 10000)

    def test_decrementing_find_count_negative(self):
        self.user.find_count = -1
        with self.assertRaises(ValidationError):
            self.user.save()

    def test_find_count_on_find_deletion(self):
        find = Find.objects.create(finder=self.user, geocache=self.geocache)
        initial_count = self.user.find_count
        find.delete()
        self.assertEqual(User.objects.get(id=self.user.id).find_count, initial_count - 1)'''

'''class GeocacheActiveDeclineEdgeCaseTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test.geocache@gmail.com', password='password')
        self.geocache = Geocache.objects.create(
            name='Test Geocache Active/Decline',
            cacher=self.user,
            lat=0.0,  # Assuming latitude is required
            lng=0.0,  # Assuming longitude is required
            description='Test Description',  # Assuming description is required
            # Include other required fields here
        )

    def test_toggle_active_status(self):
        self.geocache.active = True
        self.geocache.save()
        self.assertTrue(Geocache.objects.get(id=self.geocache.id).active)
        self.geocache.active = False
        self.geocache.save()
        self.assertFalse(Geocache.objects.get(id=self.geocache.id).active)

    def test_decline_geocache_empty_reason(self):
        self.geocache.declined = True
        self.geocache.reason = ''
        with self.assertRaises(ValidationError):
            self.geocache.save()

    def test_decline_then_activate_geocache(self):
        self.geocache.declined = True
        self.geocache.save()
        self.geocache.active = True
        self.geocache.save()
        updated_geocache = Geocache.objects.get(id=self.geocache.id)
        self.assertTrue(updated_geocache.active and updated_geocache.declined)'''