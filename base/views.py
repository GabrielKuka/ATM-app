from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import AtmSerializer, WithdrawalSerializer
from .models import ATM, Withdrawal


@api_view(['POST'])
def withdraw(request):
    try:

        valid_input = str(request.data['amount']).isdigit() and int(request.data['amount'])>=500
        
        if not valid_input: 
            raise ValueError("Invalid amount value.")

        initial_amount = amount = int(request.data['amount']) 

        if amount % 500 != 0:
            raise ValueError("Amount needs to be multiple of 500.") 

        atm_id = int(request.data['atm_id'])
        atm = ATM.objects.get(id=atm_id)

        bank_notes = {
            '5000': atm.sasi_5000,
            '2000': atm.sasi_2000,
            '1000': atm.sasi_1000,
            '500': atm.sasi_500
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
            amount=initial_amount, atm=ATM(id=atm_id), 
            note_5000=result.get('5000', 0),
            note_2000=result.get('2000', 0),
            note_1000=result.get('1000', 0),
            note_500=result.get('500', 0),
            )

        w.save()

        serializer = WithdrawalSerializer(instance=w, many=False)

        return Response(serializer.data)
    except ValueError as e:
        return Response(f"Error: {e}")
    except ObjectDoesNotExist as e:
        return Response(f"Error: This atm does not exist.")

@api_view(['PUT'])
def add_cash(request):
    try:
        data=request.data

        atm = ATM.objects.get(id=data["atm_id"]) 

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

    except ObjectDoesNotExist:
        return Response("Error: This ATM does not exist.")
    except ValueError as e:
        return Response(f"Error: {e}")
    except Exception as err:
        return Response(f"Error: {err}")

@api_view(['GET'])
def get_atms(request):
    try:
        atms = ATM.objects.all()
        serializer = AtmSerializer(atms, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(f"Error: {e}")

@api_view(['GET'])
def get_atm(request, id):
    try:
        atm = ATM.objects.get(id=id)
        serializer = AtmSerializer(atm, many=False)
        return Response(serializer.data)

    except ObjectDoesNotExist:
        return Response('Error: Atm not found')
    except Exception as e:
        return Response(f"Error: {e}")

@api_view(['GET'])
def get_all_withdrawals(request):
    try:
        ws = Withdrawal.objects.all()
        serializer = WithdrawalSerializer(ws, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(f'Error: {e}')

@api_view(['GET'])
def get_poor_atms(request):

    try:
        atms = [atm for atm in ATM.objects.all() if atm.budget <=5000] 
        serializer = AtmSerializer(atms, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(f"Error: {e}")

@api_view(['GET'])
def test(request):
    from django.db.models import Avg, Sum
    from datetime import datetime, timedelta
    last_month = datetime.today() - timedelta(days=30)

    avg = Withdrawal.objects.filter(date__gte=last_month).order_by('-date__day') \
        .values('date__day').annotate(total_sum=Sum('note_5000')).aggregate(avg=Avg('total_sum'))

    return Response(avg)
