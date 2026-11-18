from django.db import models
from django.contrib.auth.models import User

class PerfilPrestador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_prestador')
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    telefone = models.CharField(max_length=20)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    categoria = models.ForeignKey('feed.Categoria', on_delete=models.SET_NULL, null=True)
    descricao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perfil de: {self.usuario.first_name}"

class Avaliacao(models.Model):
    prestador = models.ForeignKey(PerfilPrestador, on_delete=models.CASCADE, related_name='avaliacoes')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    nota = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comentario = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('prestador', 'autor')

    def __str__(self):
        return f"Avaliação de {self.autor.first_name} para {self.prestador.usuario.first_name} ({self.nota}★)"
    