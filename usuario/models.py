from django.db import models
from django.contrib.auth.models import User

class PerfilPrestador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20)
    descricao = models.TextField()

    def __str__(self):
        return f"Perfil de: {self.usuario.first_name}"
    