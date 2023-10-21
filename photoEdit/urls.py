from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('upload/', views.upload_photo, name='upload_photo'),
    path('photos/<int:pk>/', views.photo_uploaded, name='photo_uploaded')
]
