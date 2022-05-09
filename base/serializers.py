from rest_framework import serializers
from .models import ATM, Withdrawal

from users.serializers import UserSerializer 

class AtmSerializer(serializers.ModelSerializer):
    budget = serializers.ReadOnlyField()
    mesatarja = serializers.ReadOnlyField()
    kart_5000 = serializers.ReadOnlyField()
    kart_2000 = serializers.ReadOnlyField()
    kart_1000 = serializers.ReadOnlyField()
    kart_500 = serializers.ReadOnlyField()

    class Meta:
        model = ATM
        fields = '__all__'

class WithdrawalSerializer(serializers.ModelSerializer):
    client =  UserSerializer()
    class Meta:
        model = Withdrawal 
        fields = '__all__'
