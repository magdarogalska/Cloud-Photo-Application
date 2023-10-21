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


def index(request):
    return render(request, 'index.html')





from io import BytesIO



# def apply_filter(request):
#     if request.method == 'POST':
#         filter_type = request.POST.get('filter')
#         original_image_path = original_image_path
#         original_image = Image.open(original_image_path)
#
#         if filter_type == 'grayscale':
#             filtered_image = ImageOps.grayscale(original_image)
#         elif filter_type == 'sepia':
#             # Apply sepia filter
#             filtered_image = sepia_filter(original_image)
#         elif filter_type == 'posterize':
#             # Apply posterize filter
#             filtered_image = poster_filter(original_image)
#         else:
#             filtered_image = original_image
#
#         # Create a temporary in-memory file to save the filtered image
#         filtered_image_io = BytesIO()
#         filtered_image.save(filtered_image_io, format='JPEG')
#         filtered_image_io.seek(0)
#
#             # Save the filtered image to your S3 bucket
#         filtered_image_name = f'filtered/{photo.image.name}'  # Choose a suitable name
#         s3 = boto3.client('s3')
#         s3.upload_fileobj(filtered_image_io, settings.AWS_STORAGE_BUCKET_NAME, filtered_image_name)
#
#             # Generate the URL to the filtered image in S3
#         filtered_image_url = f'https://{AWS_S3_CUSTOM_DOMAIN}/{filtered_image_name}'
#
#
#
#         return render(request, 'filter_result.html', {'image_url': filtered_image_path})
#
#     return render(request, 'filter_form.html', {'image_url': 'path/to/your/image.jpg'})





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





