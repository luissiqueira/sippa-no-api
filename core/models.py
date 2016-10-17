from __future__ import unicode_literals

from django.db import models
from django.db.models import Q


class Teacher(models.Model):
    name = models.TextField('Nome')
    emails = models.TextField('Emails', blank=True)
    avatar_url = models.URLField('Avatar URL', null=True, blank=True)
    position = models.TextField('Cargo', blank=True)

    @classmethod
    def find_by_name_or_email(cls, name, email):
        return cls.objects.filter(Q(name__icontains=name) | Q(emails__icontains=email)).first()

    @classmethod
    def import_from_json(cls, json_array):
        for item in json_array:
            name = item['name']
            _, _ = cls.objects.get_or_create(name=name, defaults=item)

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'
        ordering = ['name']

    def __unicode__(self):
        return self.name
