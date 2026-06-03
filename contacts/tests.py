from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from realtors.models import Realtor
from listings.models import Listing
from .models import Contact


def make_realtor():
    return Realtor.objects.create(
        name='Jane Smith', phone='0821234567',
        email='jane@example.com', photo='photos/test.jpg'
    )


def make_listing(realtor):
    return Listing.objects.create(
        realtor=realtor, title='Test Property',
        address='1 Main Rd', city='Sandton', state='GP',
        zipcode='2196', price=1500000, bedrooms=3,
        bathrooms=2.0, sqft=180, lot_size=0.5,
        photo_main='photos/test.jpg', is_published=True
    )


class ContactModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass1234')

    def test_contact_str(self):
        contact = Contact.objects.create(
            listing='Test Property', listing_id=1,
            name='Bob', email='bob@test.com', user=self.user
        )
        self.assertEqual(str(contact), 'Bob — Test Property')


class ContactViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', password='pass1234', email='test@test.com')
        self.realtor = make_realtor()
        self.listing = make_listing(self.realtor)

    def _post_contact(self):
        return self.client.post(reverse('contact'), {
            'listing_id': self.listing.id,
            'listing': self.listing.title,
            'name': 'Bob Jones',
            'email': 'bob@test.com',
            'phone': '0821234567',
            'message': 'Interested!',
            'realtor_email': self.realtor.email,
        })

    def test_unauthenticated_contact_saved(self):
        self._post_contact()
        self.assertEqual(Contact.objects.count(), 1)

    def test_authenticated_contact_saved(self):
        self.client.login(username='testuser', password='pass1234')
        self._post_contact()
        contact = Contact.objects.first()
        self.assertEqual(contact.user, self.user)

    def test_duplicate_enquiry_blocked(self):
        self.client.login(username='testuser', password='pass1234')
        self._post_contact()
        self._post_contact()
        self.assertEqual(Contact.objects.count(), 1)

    def test_contact_redirects_to_listing(self):
        response = self._post_contact()
        self.assertRedirects(response, f'/listings/{self.listing.id}')
