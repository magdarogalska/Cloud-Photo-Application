import io
from urllib.parse import urlparse, urlsplit
import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PhotoUploadForm
from .models import Photo
import boto3
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.conf import settings
from botocore.exceptions import NoCredentialsError
from PIL import Image, ImageOps, ImageFilter



def photo_uploaded(request, pk):
    photo = Photo.objects.get(pk=pk)
    if request.method == 'POST':
        filter_type = request.POST.get('filter')
        url = photo.image.url
        new_img = applyfilter(url, filter_type, pk)


        return render(request, 'filter_result.html', {'img_url':new_img})

    return render(request, 'photo_uploaded.html', {'photo':photo})
def download_photo(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        s3 = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        photo_key = url.replace('https://photoappmr.s3.amazonaws.com/', '')

        try:


            response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=photo_key)
            content_type = response['ContentType']
            content = response['Body'].read()

            response = HttpResponse(content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{photo_key}"'
            return response

        except Exception as e:
            return HttpResponse("File not found", status=404)






def index(request):
    return render(request, 'index.html')


from io import BytesIO


def applyfilter(url, preset, pk):


    f = url.replace('https://photoappmr.s3.amazonaws.com/photos/','')
    index = str(f).find('.jpg')
    f = str(f)[:index]

    outputfilename = f + '-out.jpg'




    try:
        # Send an HTTP GET request to the S3 URL to download the image.
        response = requests.get(url)

        # Check if the request was successful (HTTP status code 200).
        if response.status_code == 200:
            # Open the image using Pillow (PIL).
            image = Image.open(BytesIO(response.content))
            # image.show()
        else:
            print(f"Failed to download the image. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")



    if preset == 'grayscale':
        image = ImageOps.grayscale(image)


    if preset == 'edge':
        image = ImageOps.grayscale(image)
        image = image.filter(ImageFilter.FIND_EDGES)

    if preset == 'posterize':
        image = ImageOps.posterize(image, 3)

    if preset == 'solar':
        image = ImageOps.solarize(image, threshold=80)

    image_stream = BytesIO()
    image.save(image_stream, format='JPEG')
    image_stream.seek(0)

    s3 = boto3.client(
        's3',
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    s3_bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    s3_key = 'filtered/' + 'photo'+str(pk)+'.jpg'
    s3.upload_fileobj(image_stream, s3_bucket_name, s3_key)

    # Generate the S3 URL of the uploaded image
    s3_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{s3_key}"


    return s3_url




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

                    pass

            return redirect('photo_uploaded', pk= photo.pk)
    else:
        form = PhotoUploadForm()
    return render(request, 'photo_upload.html', {'form': form})

def handle_uploaded_file(f,filter):
    uploadfilename='photos/' + f.name
    with open(uploadfilename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    outputfilename=applyfilter(f.name, filter)
    return outputfilename

