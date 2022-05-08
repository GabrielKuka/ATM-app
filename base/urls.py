from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_atms),
    path('<int:id>/', views.get_atm),
    path('<int:id>/withdraw/', views.withdraw),
    path('<int:id>/add_cash/', views.add_cash),
    path('poor/', views.get_poor_atms),
    path('withdrawals/', views.get_all_withdrawals),
]