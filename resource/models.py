from django.db import models

# Create your models here.
class SKUDetailFile(models.Model):
    file = models.FileField()
    filename = models.CharField(max_length=500 , unique=True)

class SKUPriceFile(models.Model):
    file = models.FileField()
    filename = models.CharField(max_length=500 , unique=True)

class Uploadfile(models.Model):
    file =models.FileField(upload_to= "selarforcast")