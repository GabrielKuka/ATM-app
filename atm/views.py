from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def overview(request):
    info = {
        "Title": "API overview",
        "Show ATMS": "/atms/",
        "Show 1 ATM": "/atms/<id>/",
        "Add Cash to ATM": "/atms/<id>/add_cash/",
        "Withdraw cash": "/atms/<id>/withdraw/",
        "Show withdrawals": "/atms/withdrawals/",
        "Get ATMS with <= 5000": "/atms/poor/"
    }
    
    return Response(info)
        