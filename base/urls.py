from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_atms),
    path('add_atm', views.add_atm),
    path('<int:id>/', views.get_atm),
    path('<int:id>/withdraw/', views.withdraw),
    path('<int:id>/add_cash/', views.add_cash),
    path('<int:id>/refills/', views.get_refills),
    path('poor/', views.get_poor_atms),
    path('withdrawals/', views.get_all_withdrawals),
]