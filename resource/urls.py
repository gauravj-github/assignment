from django.urls import path
from resource.views import upload_files


urlpatterns = [
    path("", upload_files, name="upload-file")
]
