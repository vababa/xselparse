from django.shortcuts import render, redirect
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect

# Create your views here.
@csrf_protect
def login(request):
    args = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        #print('username: ', username, 'password: ', password)
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            print('User logegd in: ', username)
            return redirect('/parse/')
        else:
            args['login_error'] = 'Пользователь не найден'
            return render(request, 'login.html', args)
    else:
        return render(request, 'login.html', args)

def logout(request):
    auth.logout(request)
    return redirect('/parse/')