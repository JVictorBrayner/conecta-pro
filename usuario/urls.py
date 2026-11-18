from django.urls import path
from . import views

urlpatterns = [
    path('', views.fazer_login, name='home'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.fazer_login, name='login'),
    path('logout/', views.fazer_logout, name='logout'),
    path('perfil-prestador/', views.gerenciar_perfil_prestador, name='gerenciar_perfil_prestador'),
    path('vitrine/<int:prestador_id>/', views.vitrine_prestador, name='vitrine_prestador'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
]