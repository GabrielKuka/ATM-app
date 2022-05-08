from django.urls import path
from . import views

urlpatterns = [
    path('withdraw/', views.withdraw),
    path('withdrawals/', views.get_all_withdrawals),
    path('atms/', views.get_atms),
    path('atms/<int:id>', views.get_atm),
    path('atms/poor/', views.get_poor_atms),
    path('atms/add_cash/', views.add_cash),
]