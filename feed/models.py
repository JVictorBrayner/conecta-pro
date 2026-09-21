from django.db import models
from usuario.models import PerfilPrestador

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Publicacao(models.Model):
    prestador = models.ForeignKey(PerfilPrestador, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    texto = models.TextField()

    # para fotos
    imagem = models.ImageField(upload_to='fotos_servicos/', blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Anúncio de {self.prestador.usuario.first_name} - {self.categoria}"

