from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Contact(models.Model):
    listing = models.CharField(max_length=200)
    listing_id = models.IntegerField()
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    contact_date = models.DateTimeField(default=datetime.now, blank=True)
    # Nullable FK so unauthenticated users can still enquire
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='contacts')

    class Meta:
        ordering = ['-contact_date']

    def __str__(self):
        return f'{self.name} — {self.listing}'
