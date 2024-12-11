from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Order
from .forms import OrderForm

@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = OrderForm(data)

            if form.is_valid():
                order = form.save(commit=False)
                order.save()

                return JsonResponse({
                    'id': order.id,
                    'quantity': order.quantity,
                }, status=201)
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
