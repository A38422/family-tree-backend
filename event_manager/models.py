from django.db import models

from family_tree_manager.models import FamilyTree


class Event(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date = models.DateField()
    description = models.TextField(null=True, blank=True)
    attendees = models.ManyToManyField(FamilyTree, null=True, blank=True, related_name='attendees')

    def __str__(self):
        return self.name
