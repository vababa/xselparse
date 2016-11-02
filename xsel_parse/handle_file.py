from django.conf import settings

def handle_uploaded_file(f):
    filepath = settings.MEDIA_ROOT + 'temp.xls'
    with open(filepath, 'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    destination.close()

    return filepath