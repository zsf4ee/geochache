from django.test import TestCase
from . models import User, Geocache, Find, Comment
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.test import client

# Create your tests here.

# YourTestClass Code from https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing

class YourTestClass(TestCase):
    def setUp(self):
        # Setup run before every test method.
        pass

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_something_that_will_pass(self):
        self.assertFalse(False)

    def test_something_that_will_fail(self):
        self.assertTrue(False)