from django.shortcuts import render
from .decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def index(request):
    return render(request, 'redirect.html')