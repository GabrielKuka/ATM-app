from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def overview(request):
    info = {
        "Title": "API overview",
        "Show ATMS": "/base/atms/",
        "Show 1 ATM": "/base/atms/<id>/",
        "Add Cash to ATM": "/base/atms/add_cash/",
        "Withdraw cash": "/base/withdraw/",
        "Show withdrawals": "/base/withdrawals/"
    }
    
    return Response(info)
        