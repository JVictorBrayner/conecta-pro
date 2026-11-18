import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import PerfilPrestador, Avaliacao
from django.db.models import Avg
from feed.models import Categoria, Publicacao

def cadastro(request):
    if request.method == 'GET':
        status = request.GET.get('status')
        return render(request, 'cadastro.html', {'status': status})

    elif request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha')

        # Status 0: campos vazios (alinhado com cadastro.html)
        if not nome or not email or not senha:
            return redirect('/cadastro/?status=0')

        # Status 2: email já existe
        if User.objects.filter(username=email).exists():
            return redirect('/cadastro/?status=2')

        User.objects.create_user(
            username=email,
            email=email,
            password=senha,
            first_name=nome
        )

        # Status 1: sucesso
        return redirect('/cadastro/?status=1')

def fazer_login(request):
    if request.method == 'GET':
        # Se o usuário já estiver logado, vai direto para o feed
        if request.user.is_authenticated:
            return redirect('feed')
        status = request.GET.get('status')
        return render(request, 'login.html', {'status': status})

    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha')

        usuario = authenticate(request, username=email, password=senha)

        if usuario is not None:
            login(request, usuario)
            return redirect('feed')
        else:
            return redirect('/login/?status=erro')

def fazer_logout(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/login/')
def gerenciar_perfil_prestador(request):
    perfil = PerfilPrestador.objects.filter(usuario=request.user).first()
    categorias_disponiveis = Categoria.objects.all().order_by('nome')

    if request.method == 'GET':
        status = request.GET.get('status')
        return render(request, 'perfil_prestador.html', {
            'perfil': perfil,
            'categorias': categorias_disponiveis,
            'status': status
        })

    elif request.method == 'POST':
        telefone_bruto = request.POST.get('telefone', '').strip()
        telefone = re.sub(r'\D', '', telefone_bruto)
        cidade = request.POST.get('cidade', '').strip()
        estado = request.POST.get('estado', '').strip().upper()
        descricao = request.POST.get('descricao', '').strip()
        categoria_id = request.POST.get('categoria')
        foto = request.FILES.get('foto_perfil')

        if not telefone or not cidade or not estado or not descricao or not categoria_id:
            return redirect('/perfil-prestador/?status=erro')

        if perfil is None:
            PerfilPrestador.objects.create(
                usuario=request.user,
                telefone=telefone,
                cidade=cidade,
                estado=estado,
                categoria_id=categoria_id,
                descricao=descricao,
                foto_perfil=foto
            )
        else:
            perfil.telefone = telefone
            perfil.cidade = cidade
            perfil.estado = estado
            perfil.categoria_id = categoria_id
            perfil.descricao = descricao
            if foto:
                perfil.foto_perfil = foto
            perfil.save()

        return redirect('/perfil-prestador/?status=sucesso')

@login_required(login_url='/login/')
def vitrine_prestador(request, prestador_id):
    prestador = get_object_or_404(PerfilPrestador, id=prestador_id)

    if request.method == 'POST':
        # Impede que o prestador avalie o próprio perfil
        if request.user == prestador.usuario:
            return redirect('vitrine_prestador', prestador_id=prestador.id)

        nota = request.POST.get('nota')
        comentario = request.POST.get('comentario', '').strip()

        if nota and nota.isdigit() and 1 <= int(nota) <= 5 and comentario:
            Avaliacao.objects.update_or_create(
                prestador=prestador,
                autor=request.user,
                defaults={
                    'nota': int(nota),
                    'comentario': comentario
                }
            )
            return redirect(f'/vitrine/{prestador.id}/?status=avaliado')
        else:
            return redirect(f'/vitrine/{prestador.id}/?status=erro_avaliacao')

    publicacoes = Publicacao.objects.filter(prestador=prestador).order_by('-data_criacao')
    avaliacoes = prestador.avaliacoes.select_related('autor').all().order_by('-data_criacao')
    media_notas = avaliacoes.aggregate(Avg('nota'))['nota__avg']
    minha_avaliacao = avaliacoes.filter(autor=request.user).first()
    status = request.GET.get('status')

    return render(request, 'vitrine_prestador.html', {
        'prestador': prestador,
        'publicacoes': publicacoes,
        'avaliacoes': avaliacoes,
        'media_notas': media_notas,
        'minha_avaliacao': minha_avaliacao,
        'status': status
    })

@login_required(login_url='/login/')
def configuracoes(request):
    if request.method == 'POST':
        acao = request.POST.get('acao')

        # 1. Atualizar Nome e Email
        if acao == 'dados':
            nome = request.POST.get('nome', '').strip()
            email = request.POST.get('email', '').strip()

            if not nome or not email:
                return redirect('/configuracoes/?status=erro_dados')

            # Verifica se outro usuário já usa este e-mail
            if User.objects.filter(username=email).exclude(id=request.user.id).exists():
                return redirect('/configuracoes/?status=email_em_uso')

            request.user.first_name = nome
            request.user.email = email
            request.user.username = email
            request.user.save()
            return redirect('/configuracoes/?status=dados_salvos')

        # 2. Alterar Senha
        elif acao == 'senha':
            senha_atual = request.POST.get('senha_atual')
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')

            if not request.user.check_password(senha_atual):
                return redirect('/configuracoes/?status=senha_incorreta')

            if not nova_senha or nova_senha != confirmar_senha:
                return redirect('/configuracoes/?status=senhas_diferentes')

            request.user.set_password(nova_senha)
            request.user.save()
            # Mantém o usuário logado após a troca de senha
            update_session_auth_hash(request, request.user)
            return redirect('/configuracoes/?status=senha_alterada')

        # 3. Excluir Conta Definitivamente
        elif acao == 'excluir':
            senha_confirmacao = request.POST.get('senha_confirmacao')

            if not request.user.check_password(senha_confirmacao):
                return redirect('/configuracoes/?status=senha_exclusao_incorreta')

            # Remove foto de perfil e imagens das publicações antes de deletar o usuário
            perfil = PerfilPrestador.objects.filter(usuario=request.user).first()
            if perfil:
                for pub in perfil.publicacao_set.all():
                    if pub.imagem:
                        pub.imagem.delete(save=False)
                if perfil.foto_perfil:
                    perfil.foto_perfil.delete(save=False)

            usuario = request.user
            logout(request)
            usuario.delete()
            return redirect('login')

    status = request.GET.get('status')
    return render(request, 'configuracoes.html', {'status': status})