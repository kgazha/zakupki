from django.contrib import admin
from core import models


admin.site.register(models.Resource)
admin.site.register(models.File)
admin.site.register(models.PurchaseTypeControl)
admin.site.register(models.Purchase)
