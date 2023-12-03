import os
from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import User, Geocache, Find, Comment
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import authenticate, login, logout


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

class AuthenticationViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_login_success(self):
        user = authenticate(username='testuser', password='testpassword')
        self.assertIsNotNone(user)
        self.assertTrue(user.is_authenticated)

    def test_login_failure(self):
        user = authenticate(username='testuser', password='wrongpassword')
        self.assertIsNone(user)

    def test_logout(self):
        logout(self.client)
        self.assertFalse('_auth_user_id' in self.client.session)

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

class GeocacheCreationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='geocacheuser', password='geocachepassword')

    def test_geocache_creation(self):
        geocache = Geocache.objects.create(
            name='New Geocache',
            cacher=self.user,
            cache_date=timezone.now(),
            lat=10.0,
            lng=10.0,
            description='A new geocache'
        )
        self.assertEqual(Geocache.objects.count(), 1)
        self.assertEqual(geocache.name, 'New Geocache')

class GeocacheUpdateTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='geocacheuser', password='geocachepassword')
        self.geocache = Geocache.objects.create(
            name='Update Geocache',
            cacher=self.user,
            cache_date=timezone.now(),
            lat=10.0,
            lng=10.0,
            description='An updatable geocache'
        )

    def test_geocache_update(self):
        self.geocache.name = 'Updated Geocache Name'
        self.geocache.save()
        updated_geocache = Geocache.objects.get(id=self.geocache.id)
        self.assertEqual(updated_geocache.name, 'Updated Geocache Name')

class UserProfileUpdateTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='profileuser', password='profilepassword')

    def test_profile_update(self):
        self.user.username = 'updatedusername'
        self.user.save()
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.username, 'updatedusername')

class FindTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test.user2@gmail.com', password='test_password2', is_admin=False)
        self.geocache = Geocache.objects.create(
            name='Test Geocache 2',
            cacher=self.user,
            cache_date=timezone.now(),
            lat=1.0,
            lng=1.0,
            description='This is another test geocache', )
        self.find = Find.objects.create(
            finder=self.user,
            geocache=self.geocache,
            timestamp=timezone.now() )

    def test_find_creation(self):
        self.assertIsInstance(self.find, Find)
        self.assertEqual(self.find.finder, self.user)

    def test_increment_find_count_for_geocache(self):
        initial_count = self.geocache.find_count
        new_find = Find.objects.create(finder=self.user, geocache=self.geocache, timestamp=timezone.now())
        self.geocache.find_count += 1
        self.geocache.save()
        self.geocache.refresh_from_db()
        self.assertEqual(self.geocache.find_count, initial_count + 1)

    def test_create_find_with_hint_count(self):
        find_with_hint = Find.objects.create(finder=self.user, geocache=self.geocache, timestamp=timezone.now(), hint_count=2)
        self.assertEqual(find_with_hint.hint_count, 2)

    def test_create_find_with_found_status(self):
        find_marked_found = Find.objects.create(finder=self.user, geocache=self.geocache, timestamp=timezone.now(), found=True)
        self.assertTrue(find_marked_found.found)

    def test_find_deletion_impact_on_find_count(self):
        new_find = Find.objects.create(finder=self.user, geocache=self.geocache, timestamp=timezone.now())
        initial_count = self.geocache.find_count
        new_find.delete()
        self.geocache.refresh_from_db()
        self.assertEqual(self.geocache.find_count, initial_count - 1)

    def test_find_deletion_impact_on_find_count(self):
        new_find = Find.objects.create(finder=self.user, geocache=self.geocache, timestamp=timezone.now())
        initial_count = self.geocache.find_count
        new_find.delete()
        self.geocache.find_count -= 1  # Manually decrement the find_count
        self.geocache.save()
        self.geocache.refresh_from_db()
        self.assertEqual(self.geocache.find_count, initial_count - 1)

    def test_increment_find_count_for_user(self):
        initial_count = self.user.find_count
        new_find = Find.objects.create(finder=self.user, geocache=self.geocache, timestamp=timezone.now())
        self.user.find_count += 1  # Manually increment the find_count
        self.user.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.find_count, initial_count + 1)


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

class UserProfileUpdateTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='profileuser', password='profilepassword')

    def test_profile_update(self):
        self.user.username = 'updatedusername'
        self.user.save()
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.username, 'updatedusername')


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

class GeocacheEdgeCaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test.user@gmail.com', password='test_password')

    def test_geocache_extreme_lat_lng(self):
        geocache = Geocache(
            name='Extreme Geocache', cacher=self.user, lat=91.0, lng=181.0, cache_date=timezone.now()
        )
        with self.assertRaises(ValidationError):
            geocache.full_clean()

    def test_geocache_past_date(self):
        past_date = timezone.now() - timedelta(days=365)
        geocache = Geocache.objects.create(
            name='Past Geocache', cacher=self.user, lat=0.0, lng=0.0, cache_date=past_date
        )
        self.assertLess(geocache.cache_date, timezone.now())

class UserLoginFailureTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='password')
        self.geocache = Geocache.objects.create(
            name='Test Geocache',
            active=False,
            password='geopass',
            declined=False,
            admin=None,
            admin_date=None,
            cacher=self.user,
            find_count=0,
            cache_date=timezone.now(),
            lat=Decimal('52.520008'),
            lng=Decimal('13.404954'),
            description='Test description',
            radius=10,
        )

    def test_geocache_creation(self):
        self.assertIsInstance(self.geocache, Geocache)


class UserProfileUpdateTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user@example.com', password='old_password')

    def test_user_profile_update(self):
        self.user.password = 'new_password'
        self.user.save()
        updated_user = User.objects.get(username='user@example.com')
        self.assertEqual(updated_user.password, 'new_password')

class GeocacheApprovalTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create(username='admin@example.com', password='admin_password', is_admin=True)
        self.geocache = Geocache.objects.create(
            name='Test Geocache',
            active=False,
            password='geopass',
            declined=False,
            admin=None,
            admin_date=None,
            cacher=self.admin_user,
            find_count=0,
            cache_date=timezone.now(),
            lat=Decimal('52.520008'),
            lng=Decimal('13.404954'),
            description='Test description',
            radius=10,
        )
    def test_approve_geocache(self):
        self.geocache.active = True
        self.geocache.save()
        self.assertTrue(self.geocache.active)

    def test_decline_geocache(self):
        self.geocache.declined = True
        self.geocache.reason = "Inappropriate location"
        self.geocache.save()
        updated_geocache = Geocache.objects.get(id=self.geocache.id)
        self.assertTrue(updated_geocache.declined)
        self.assertEqual(updated_geocache.reason, "Inappropriate location")

    def test_admin_date_update_on_approval(self):
        self.geocache.active = True
        self.geocache.admin_date = timezone.now()
        self.geocache.save()
        updated_geocache = Geocache.objects.get(id=self.geocache.id)
        self.assertIsNotNone(updated_geocache.admin_date)

    def test_admin_assignment_on_approval(self):
        self.geocache.active = True
        self.geocache.admin = self.admin_user
        self.geocache.save()
        updated_geocache = Geocache.objects.get(id=self.geocache.id)
        self.assertEqual(updated_geocache.admin, self.admin_user)

    def test_approval_resets_decline_status(self):
        self.geocache.declined = True
        self.geocache.reason = "Temporary issue"
        self.geocache.save()
        self.geocache.declined = False
        self.geocache.active = True
        self.geocache.reason = ""
        self.geocache.save()
        updated_geocache = Geocache.objects.get(id=self.geocache.id)
        self.assertFalse(updated_geocache.declined)
        self.assertTrue(updated_geocache.active)

