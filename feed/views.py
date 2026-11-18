from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Publicacao, Categoria
from django.db.models import Q
from usuario.models import PerfilPrestador

@login_required(login_url='/login/')
def feed(request):
    perfil_prestador = PerfilPrestador.objects.filter(usuario=request.user).first()

    if request.method == 'POST':
        if not perfil_prestador:
            return redirect('gerenciar_perfil_prestador')

        texto = request.POST.get('texto', '').strip()
        imagem = request.FILES.get('imagem')

        if not texto:
            return redirect('/feed/?status=erro')

        Publicacao.objects.create(
            prestador=perfil_prestador,
            categoria=perfil_prestador.categoria,
            texto=texto,
            imagem=imagem
        )

        return redirect('/feed/?status=sucesso')

    # Listagem e filtros (GET)
    publicacoes = Publicacao.objects.select_related('prestador__usuario', 'categoria').all().order_by('-data_criacao')
    categorias = Categoria.objects.all().order_by('nome')

    busca = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()

    if busca:
        publicacoes = publicacoes.filter(
            Q(texto__icontains=busca) |
            Q(prestador__usuario__first_name__icontains=busca) |
            Q(prestador__cidade__icontains=busca) |
            Q(categoria__nome__icontains=busca)
        )

    if categoria_id:
        publicacoes = publicacoes.filter(categoria_id=categoria_id)

    status = request.GET.get('status')

    return render(request, 'feed.html', {
        'publicacoes': publicacoes,
        'categorias': categorias,
        'perfil_prestador': perfil_prestador,
        'busca': busca,
        'categoria_selecionada': categoria_id,
        'status': status
    })

@login_required(login_url='/login/')
def excluir_publicacao(request, pub_id):
    publicacao = get_object_or_404(Publicacao, id=pub_id)

    # Trava de segurança: só o autor da publicação pode excluir
    if publicacao.prestador.usuario != request.user:
        return redirect('feed')

    if request.method == 'POST':
        # Remove o arquivo físico da imagem, se existir
        if publicacao.imagem:
            publicacao.imagem.delete(save=False)
        publicacao.delete()

    # Volta para a página de onde o usuário clicou (feed ou vitrine)
    proxima_pagina = request.POST.get('next', 'feed')
    return redirect(proxima_pagina)


@login_required(login_url='/login/')
def editar_publicacao(request, pub_id):
    publicacao = get_object_or_404(Publicacao, id=pub_id)

    # Trava de segurança: só o autor pode editar
    if publicacao.prestador.usuario != request.user:
        return redirect('feed')

    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        nova_imagem = request.FILES.get('imagem')

        if not texto:
            return render(request, 'editar_publicacao.html', {
                'publicacao': publicacao,
                'erro': 'O texto da publicação não pode ficar vazio.'
            })

        publicacao.texto = texto
        if nova_imagem:
            # Apaga a imagem antiga antes de salvar a nova
            if publicacao.imagem:
                publicacao.imagem.delete(save=False)
            publicacao.imagem = nova_imagem

        publicacao.save()
        return redirect('feed')

    return render(request, 'editar_publicacao.html', {'publicacao': publicacao})
