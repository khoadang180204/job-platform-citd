#User không đúng role → đá về trang chủ
#Trong views.py, đã update code candidate → bị redirect /

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def employer_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'employer':
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper

def candidate_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'candidate':
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper
