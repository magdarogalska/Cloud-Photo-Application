import io
from urllib.parse import urlparse, urlsplit

import boto3 as boto3
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PhotoUploadForm
from .models import Photo
import boto3
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.conf import settings
from botocore.exceptions import NoCredentialsError
from PIL import Image, ImageOps, ImageFilter
from .image_func import sepia_filter, poster_filter

from django.http import HttpResponse


def photo_uploaded(request, pk):
    photo = Photo.objects.get(pk=pk)

    return render(request, 'photo_uploaded.html', {'photo': photo})

# def photo_filtered(request):
#
#     return render(request, 'filter_result.html', {'photo': photo})


def index(request):
    return render(request, 'index.html')


from io import BytesIO


def apply_filter(request):
    if request.method == 'POST':
        filter_type = request.POST.get('filter')
        image_url = request.POST.get('image_url')
        index = image_url.find(".jpg")

        # Extract the part of the URL up to ".jpg"
        if index != -1:
            image_url = image_url[:index + 4]  # +4 to include ".jpg"
        else:
            # ".jpg" not found in the URL
            path_without_extension = image_url

        s3 = boto3.resource('s3',
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
        key = image_url.replace('https://photoappmr.s3.amazonaws.com/','')
        image = bucket.Object(key)
        img_data = image.get().get('Body').read()
        image = Image.open(io.BytesIO(img_data))
        # s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
        # bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        # object_key = image_url

        # Download the image from S3 to a local file
        # local_file_path = 'static/pics/newpic.jpg'
        # s3.download_file(bucket_name, object_key, local_file_path)

        # Apply the filter to the original image

        if filter_type == 'grayscale':
            filtered_image = ImageOps.grayscale(image)
        elif filter_type == 'sepia':
            filtered_image = sepia_filter(image)
        elif filter_type == 'posterize':
            filtered_image = poster_filter(image)
        else:
            filtered_image = image

        # Create a temporary in-memory buffer to save the filtered image
        filtered_image_io = BytesIO()
        filtered_image.save(filtered_image_io, format='JPEG')

        # Upload the filtered image to S3 with a new object key
        filtered_object_key = f'filtered/newpic.jpg'
        s3.upload_fileobj(filtered_image_io, settings.AWS_STORAGE_BUCKET_NAME, filtered_object_key)




        return render(request, 'filter_result.html')

    return render(request, 'photo_uploaded.html', {'form': PhotoUploadForm()})


def upload_photo(request):
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save()

            if isinstance(photo, TemporaryUploadedFile):
                try:
                    s3 = boto3.client('s3')
                    object_key = f'photos/{photo.image.name}'
                    s3.upload_file(photo.temporary_file_path(), settings.AWS_STORAGE_BUCKET_NAME, object_key)
                except NoCredentialsError:
                    # Handle AWS credentials error
                    # You may want to log the error or display an error message to the user.
                    pass
            # original_image_path = photo.image.path
            # return render(request, 'photo_uploaded.html', {'original_image_path': original_image_path})
            return redirect('photo_uploaded', pk=photo.pk)
    else:
        form = PhotoUploadForm()
    return render(request, 'photo_upload.html', {'form': form})
