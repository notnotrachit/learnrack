from django.shortcuts import render, redirect
from .decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return render(request, 'redirect.html')