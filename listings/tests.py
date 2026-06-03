from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from realtors.models import Realtor
from .models import Listing, Favourite


def make_realtor():
    return Realtor.objects.create(
        name='Jane Smith', phone='0821234567',
        email='jane@example.com', photo='photos/test.jpg'
    )


def make_listing(realtor):
    return Listing.objects.create(
        realtor=realtor, title='3 Bed House Sandton',
        address='1 Main Rd', city='Sandton', state='GP',
        zipcode='2196', price=1500000, bedrooms=3,
        bathrooms=2.0, sqft=180, lot_size=0.5,
        photo_main='photos/test.jpg', is_published=True
    )


class ListingModelTest(TestCase):
    def setUp(self):
        self.realtor = make_realtor()
        self.listing = make_listing(self.realtor)

    def test_listing_str(self):
        self.assertEqual(str(self.listing), '3 Bed House Sandton')

    def test_listing_is_published_default(self):
        self.assertTrue(self.listing.is_published)

    def test_listing_price(self):
        self.assertEqual(self.listing.price, 1500000)


class FavouriteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass1234')
        self.realtor = make_realtor()
        self.listing = make_listing(self.realtor)

    def test_create_favourite(self):
        fav = Favourite.objects.create(user=self.user, listing=self.listing)
        self.assertEqual(str(fav), 'testuser → 3 Bed House Sandton')

    def test_unique_together(self):
        Favourite.objects.create(user=self.user, listing=self.listing)
        from django.db import IntegrityError
        with self.assertRaises(Exception):
            Favourite.objects.create(user=self.user, listing=self.listing)


class ListingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.realtor = make_realtor()
        self.listing = make_listing(self.realtor)
        self.user = User.objects.create_user('viewer', password='pass1234')

    def test_listings_index(self):
        response = self.client.get(reverse('listings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '3 Bed House Sandton')

    def test_listing_detail(self):
        response = self.client.get(reverse('listing', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sandton')

    def test_listing_detail_404(self):
        response = self.client.get(reverse('listing', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_search_no_filters(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '3 Bed House Sandton')

    def test_search_by_city(self):
        response = self.client.get(reverse('search') + '?city=Sandton')
        self.assertContains(response, '3 Bed House Sandton')

    def test_search_by_city_no_match(self):
        response = self.client.get(reverse('search') + '?city=Durban')
        self.assertNotContains(response, '3 Bed House Sandton')

    def test_search_by_price(self):
        response = self.client.get(reverse('search') + '?price=2000000')
        self.assertContains(response, '3 Bed House Sandton')

    def test_search_price_too_low(self):
        response = self.client.get(reverse('search') + '?price=500000')
        self.assertNotContains(response, '3 Bed House Sandton')

    def test_toggle_favourite_requires_login(self):
        response = self.client.post(reverse('toggle_favourite', args=[self.listing.id]))
        self.assertRedirects(response, f'/accounts/login?next=/listings/{self.listing.id}/favourite')

    def test_toggle_favourite_authenticated(self):
        self.client.login(username='viewer', password='pass1234')
        self.client.post(reverse('toggle_favourite', args=[self.listing.id]))
        self.assertTrue(Favourite.objects.filter(user=self.user, listing=self.listing).exists())

    def test_toggle_favourite_removes_on_second_click(self):
        self.client.login(username='viewer', password='pass1234')
        self.client.post(reverse('toggle_favourite', args=[self.listing.id]))
        self.client.post(reverse('toggle_favourite', args=[self.listing.id]))
        self.assertFalse(Favourite.objects.filter(user=self.user, listing=self.listing).exists())

    def test_unpublished_listing_hidden_from_index(self):
        self.listing.is_published = False
        self.listing.save()
        response = self.client.get(reverse('listings'))
        self.assertNotContains(response, '3 Bed House Sandton')
