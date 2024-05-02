from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Img(models.Model):
    lat = models.FloatField(verbose_name=_('latitude'), help_text=_('latitude'))  #緯度
    lng = models.FloatField(verbose_name=_('longitude'), help_text=_('longitude'))  #經度
    imgtime = models.DateTimeField(default=timezone.now)
    filename = models.CharField(max_length=100, verbose_name=_('filename'), help_text=_('filename'))
    dirname = models.CharField(max_length=100, verbose_name=_('dirname'), help_text=_('dirname'))
    path = models.CharField(max_length=200, verbose_name=_('path'), help_text=_('path'), default='')
    def __str__(self):
        return self.filename