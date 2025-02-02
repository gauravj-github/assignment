from django.contrib import admin
from resource.models import SKUDetailFile , SKUPriceFile
# Register your models here.
admin.site.register(SKUPriceFile)
admin.site.register(SKUDetailFile)