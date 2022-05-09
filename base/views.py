from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .serializers import AtmSerializer, WithdrawalSerializer, ClientSerializer
from .models import ATM, Withdrawal, Client

import sys

MAX_INT = sys.maxsize

@api_view(['GET', 'POST'])
def add_atm(request):

    if request.method == 'GET':
        example = {'5000': 25}
        return Response({'Example': example}) 
    
    try:
        data = request.data
        atm = ATM.objects.create()

        valid_notes = ('5000', '2000', '1000', '500')
        for x in data.items():
            not_valid = x[0] not in valid_notes or not str(x[1]).isdigit() or int(x[1]) <= 0
            if not_valid:
                raise ValueError("'{0}': {1} => Invalid input.".format(x[0], x[1]))

        # Add cash
        input = {
            "sasi_5000": atm.sasi_5000 + data.get('5000', 0), 
            "sasi_2000": atm.sasi_2000 + data.get('2000', 0), 
            "sasi_1000": atm.sasi_1000 + data.get('1000', 0), 
            "sasi_500": atm.sasi_500 + data.get('500', 0), 
        }

        serializer = AtmSerializer(instance=atm, data=input)

        if not serializer.is_valid():
            raise ValueError("Invalid data entered.")
        
        serializer.save()
        return Response(serializer.data)

    except ValueError as e:
        return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(f"Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST', 'GET'])
def withdraw(request, id):

    if request.method == 'GET':
        example = {'amount': 28500, 'name': 'Gabriel', 'pin': 1998}
        return Response(example)

    try:
        valid_input = 'amount' in request.data and \
                'name' in request.data and \
                'pin' in request.data and \
                str(request.data['amount']).isdigit() and \
                int(request.data['amount'])>=500
        
        if not valid_input: 
            raise ValueError("Invalid input.")

        data = request.data

        try:
            client = Client.objects.get(name=data['name'], pin=data['pin'])
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist("Auth data incorrrect.")

        initial_amount = amount = int(data['amount']) 

        if amount % 500 != 0:
            raise ValueError("Amount needs to be multiple of 500.") 
        if amount > client.max_val:
            raise ValueError(f"You can't withdraw more than {client.max_val}")

        atm = ATM.objects.get(id=id)

        bank_notes = {
            '5000': atm.sasi_5000 if atm.budget >= amount else MAX_INT,
            '2000': atm.sasi_2000 if atm.budget >= amount else MAX_INT,
            '1000': atm.sasi_1000 if atm.budget >= amount else MAX_INT,
            '500': atm.sasi_500 if atm.budget >= amount else MAX_INT,
        }    

        result = {}
             
        for el in bank_notes.items():
            note = int(el[0]) 
            note_freq = int(el[1])
        
            if amount >= note and note_freq > 0:
                notes_needed = amount // note

                if notes_needed <= note_freq:
                    result[str(note)] = notes_needed
                    bank_notes[str(note)] -= notes_needed
                else:
                    result[str(note)] = note_freq
                    bank_notes[str(note)]= 0

                amount -= result[str(note)] * note

        valid_withdrawal = atm.budget >= initial_amount and sum(result.values())<=20  

        # Update atm resources if withdrawal is valid    
        if valid_withdrawal:
            atm.sasi_5000 -= result.get('5000', 0)
            atm.sasi_2000 -= result.get('2000', 0)
            atm.sasi_1000 -= result.get('1000', 0)
            atm.sasi_500 -= result.get('500', 0)
            atm.save()

        # Create withdrawal
        w = Withdrawal.objects.create(approved=True if valid_withdrawal else False, 
            amount=initial_amount, atm=ATM(id=id), 
            note_5000=result.get('5000', 0),
            note_2000=result.get('2000', 0),
            note_1000=result.get('1000', 0),
            note_500=result.get('500', 0),
            client=client
            )

        w.save()

        serializer = WithdrawalSerializer(instance=w, many=False)

        return Response(serializer.data)
    except ValueError as e:
        return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist as e:
        return Response(f"Error: {e}", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(f"Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'GET'])
def add_cash(request, id):

    if request.method == 'GET':
        example = { "amount": 28500 }
        return Response({'Example': example})

    try:

        data=request.data

        valid_input = 'amount' in data and str(data['amount']).isdigit() 
        if not valid_input:
            raise ValueError("Invalid Input.")

        amount = data['amount']

        if amount % 500 != 0:
            raise ValueError("Amount needs to be multiple of 500.")

        atm = ATM.objects.get(id=id) 


        bank_notes = (5000, 2000, 1000, 500)

        result = {}
             
        for note in bank_notes:
        
            if amount >= note :
                notes_needed = amount // note

                result[str(note)] = notes_needed

                amount -= result[str(note)] * note

        # Add cash
        input = {
            "sasi_5000": atm.sasi_5000 + result.get('5000', 0), 
            "sasi_2000": atm.sasi_2000 + result.get('2000', 0), 
            "sasi_1000": atm.sasi_1000 + result.get('1000', 0), 
            "sasi_500": atm.sasi_500 + result.get('500', 0), 
        }

        serializer = AtmSerializer(instance=atm, data=input)

        if not serializer.is_valid():
            raise ValueError("Invalid data entered.")
        
        serializer.save()
        return Response(serializer.data)

    except ValueError as e:
        return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response("Error: This ATM does not exist.", status=status.HTTP_404_NOT_FOUND)
    except Exception as err:
        return Response(f"Error: {err}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_atms(request):
    try:
        atms = ATM.objects.all()
        serializer = AtmSerializer(atms, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(f"Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_atm(request, id):
    try:
        atm = ATM.objects.get(id=id)
        serializer = AtmSerializer(atm, many=False)
        return Response(serializer.data)

    except ObjectDoesNotExist:
        return Response('Error: Atm not found', status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(f"Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_all_withdrawals(request):
    try:
        ws = Withdrawal.objects.all()
        serializer = WithdrawalSerializer(ws, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(f'Error: {e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_poor_atms(request):
    try:
        atms = [atm for atm in ATM.objects.all() if atm.budget <=5000] 
        serializer = AtmSerializer(atms, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(f"Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)