from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from xsel_parse.forms import TextToFileForm, UploadForm2
from xsel_parse import xl_parse, handle_file
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth

@csrf_protect
def upload_file(request):
    if request.method == 'POST':
        form = UploadForm2(request.POST, request.FILES)
        if form.is_valid():
            filepath = handle_file.handle_uploaded_file(request.FILES['file_field'])
            (errors, sostav, score, schet) = xl_parse.excel_parse(filepath)
            print(errors)
            for index in range(len(errors)):
                if errors[index].find('КРИТИЧНО') == 0:
                    print('critical in, index = ', index)
                    errors[index] = '<font color="red">' + errors[index][0:9] + '</font>' + errors[index][9:]
                if '\n' in errors[index]:
                    errors[index] = '<br>'.join(errors[index].split('\n'))
                if 'rating.chgk.info' in errors[index]:
                    errors[index] = '<font color="red">' + errors[index] + '</font>'

            return render(request, 'success.html', {'sostav': sostav, 'score': score, 'errors': errors, 'schet': schet,
                                                    'username': auth.get_user(request).username})
    else:
        form = UploadForm2()
    return render(request, 'upload.html', {'form': form, 'username': auth.get_user(request).username})


def success(request):
    form = TextToFileForm(request.POST)
    if form.is_valid():
        response = HttpResponse(form.cleaned_data['text_field'], content_type='application/csv', charset='cp1251')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % form.cleaned_data['file_name']
    return response
'''
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None
        login(request, user)
    else:
        HttpResponseRedirect('/login/', {error})
'''