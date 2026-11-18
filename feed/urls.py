from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('editar/<int:pub_id>/', views.editar_publicacao, name='editar_publicacao'),
    path('excluir/<int:pub_id>/', views.excluir_publicacao, name='excluir_publicacao'),
]
