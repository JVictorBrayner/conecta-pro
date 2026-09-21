from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Publicacao 

@login_required(login_url='/login/')
def feed(request):
    publicacoes = Publicacao.objects.all().order_by('-data_criacao')
    return render(request, 'feed.html', {'publicacoes': publicacoes})
