from django.db import models
from django.db.models import Avg, Sum
from datetime import datetime, timedelta

class ATM(models.Model):
    sasi_500 = models.IntegerField(default=0)
    sasi_1000 = models.IntegerField(default=0)
    sasi_2000 = models.IntegerField(default=0)
    sasi_5000 = models.IntegerField(default=0)

    # The following are composite attributes...
    @property
    def budget(self):
        return (self.sasi_500*500) + (self.sasi_1000)*1000 \
            + (self.sasi_2000)*2000 + (self.sasi_5000)*5000

    @property
    def kart_5000(self):
        return self.__get_avg("note_5000")

    @property
    def kart_2000(self):
        return self.__get_avg("note_2000")

    @property
    def kart_1000(self):
        return self.__get_avg("note_1000")

    @property
    def kart_500(self):
        return self.__get_avg("note_500")

    @property
    def mesatarja(self):
        return self.__get_avg("amount")

    def __get_avg(self, type):
    
        last_month = datetime.today() - timedelta(days=30)

        # Get the data from the last 30 days, group by day, sum the data, get the avg of the sums 
        avg = Withdrawal.objects.filter(date__gte=last_month, atm=self.id) \
                .order_by('-date__day').values('date__day')\
                .annotate(total_sum=Sum(type)).aggregate(avg=Avg('total_sum'))

        return avg['avg'] if avg['avg'] != None else 0.0

    def __str__(self):
        return f"Budget: {self.budget}\nAvg: {self.mesatarja}\n \
                sasi_5000: {self.sasi_5000}\nsasi_2000: {self.sasi_2000}\n \
                sasi_1000: {self.sasi_1000}\nsasi_500: {self.sasi_500}"

class Client(models.Model):
    name = models.CharField(unique=True, max_length=2500)
    pin = models.PositiveIntegerField(default=0000)
    max_val = models.PositiveIntegerField(default=150000)

    def __str__(self):
        return f"Name: {self.name}\nPin: {self.pin}"

class Refill(models.Model):
    sasi_500 = models.IntegerField(default=0)
    sasi_1000 = models.IntegerField(default=0)
    sasi_2000 = models.IntegerField(default=0)
    sasi_5000 = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    atm = models.ForeignKey(ATM, on_delete=models.CASCADE)

    @property
    def amount(self):
        return (self.sasi_500*500)+(self.sasi_1000*1000)+(self.sasi_2000*2000)+(self.sasi_5000*5000)

class Withdrawal(models.Model):
    approved = models.BooleanField(default=False)
    amount = models.IntegerField(default=500)
    note_5000 = models.IntegerField(default=0)
    note_2000 = models.IntegerField(default=0)
    note_1000 = models.IntegerField(default=0)
    note_500 = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    atm = models.ForeignKey(ATM, related_name='atm', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, related_name='client', on_delete=models.CASCADE)

    def __str__(self):
        return f"Date: {self.date}\nApproved: {self.approved}\nAmount: {self.amount}\nAtm: {self.atm.id}\n \
                Note_5000: {self.note_5000}\nNote_2000: {self.note_2000}\n \
                Note_1000: {self.note_1000}\nNote_500: {self.note_500}\n \
                User: {self.client}" 
