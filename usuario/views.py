from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


def cadastro(request):
    # usuário acessando a página sem inputar dados
    if request.method == 'GET':
        status = request.GET.get('status')
        return render(request, 'cadastro.html', {'status': status})

    # se usuario infornmou os dados e clicou no botão para cadastro
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

    # se o usuario deixou algum campo em branco
    if not nome or not email or not senha:
        return redirect('cadastro/?status=2')

    # se o email informado já existe no banco
    if User.objects.filter(username=email).exists():
        return redirect('/cadastro/?status=2')

    # cria e salva usuario no banco
    usuario = User.objects.create_user(
        username=email,
        email=email,
        password=senha,
        first_name=nome
    )

    return redirect('/cadastro/?status=1')    

def fazer_login(request):
    if request.method == 'GET':
        status = request.GET.get('status')
        return render(request, 'login.html', {'status': status})

    elif request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        # O authenticate verifica no banco de dados se a senha está correta.
        usuario = authenticate(request, username=email, password=senha)

        if usuario is not None:
            # se a senha estiver correta, loga no sistema
            login(request, usuario)
            return HttpResponse('Login feito com sucesso!')
        else:
            # se errou a senha ou email:
            return redirect('/login/?status=erro')
