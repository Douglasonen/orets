from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Transaction, PaymentMethod
from .gateways import MpesaGateway, StripeGateway
from .exceptions import PaymentError
from .models import Order
from django.shortcuts import render, redirect
from .models import PaymentMethod
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import PaymentMethod
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PaymentMethodForm
from orders.models import Order
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PaymentMethod
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import PaymentMethod

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import PaymentMethod, Transaction

@login_required
def delete_payment_method(request, payment_method_id):
    payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, user=request.user)
    
    if request.method == 'POST':
        payment_method.delete()
        messages.success(request, 'Payment method deleted successfully.')
        return redirect('payment_methods')
    
    # If GET request, show confirmation page
    return render(request, 'payments/confirm_delete_payment_method.html', {
        'payment_method': payment_method
    })
@login_required
class PaymentMethodListView(LoginRequiredMixin, ListView):
    model = PaymentMethod
    template_name = 'payments/methods.html'
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(business=self.request.user)\
        .defer('config')
@login_required
def payment_methods(request):
    methods = PaymentMethod.objects.filter(business=request.user)
    return render(request, 'payments/dashboard.html', {
        'payment_methods': methods,
        'successful_transactions': 0,  # Temporary placeholder
        'total_revenue': 0,  # Temporary placeholder
        'recent_transactions': []
    })

class PaymentMethodListView(LoginRequiredMixin, ListView):
    model = PaymentMethod
    template_name = 'payments/methods.html'
    context_object_name = 'methods'

    def get_queryset(self):
        return self.request.user.payment_methods.all()
    
####### up is new

@login_required
def add_payment_method(request):
    # Implement your payment method form here
    return render(request, 'payments/add_method.html')

@login_required
def transactions(request):
    transactions = Transaction.objects.filter(order__business=request.user)
    return render(request, 'payments/transactions.html', {
        'transactions': transactions
    })
### addes are above


@login_required
def add_payment_method(request):
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, business=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment method added successfully')
            return redirect('payment_methods')
    else:
        form = PaymentMethodForm(business=request.user)
    
    return render(request, 'payments/add_payment_method.html', {
        'form': form
    })

@login_required
def edit_payment_method(request, pk):
    method = get_object_or_404(PaymentMethod, pk=pk, business=request.user)
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=method, business=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment method updated successfully')
            return redirect('payment_methods')
    else:
        form = PaymentMethodForm(instance=method, business=request.user)
    
    return render(request, 'payments/edit_payment_method.html', {
        'form': form,
        'method': method
    })

@login_required
def toggle_payment_method(request, pk):
    method = get_object_or_404(PaymentMethod, pk=pk, business=request.user)
    method.is_active = not method.is_active
    method.save()
    messages.success(request, f'Payment method {"activated" if method.is_active else "deactivated"}')
    return redirect('payment_methods')

@login_required
def payment_checkout(request, order_id):
    order = get_object_or_404(Order, pk=order_id, business=request.user)
    payment_methods = PaymentMethod.objects.filter(business=request.user, is_active=True)
    
    if request.method == 'POST':
        # Handle payment processing here
        pass
    
    return render(request, 'payments/payment_checkout.html', {
        'order': order,
        'payment_methods': payment_methods,
        'currency': request.user.currency
    })
'''@login_required
def payment_methods(request):
    """List available payment methods for a business"""
    methods = PaymentMethod.objects.filter(
        business=request.user,
        is_active=True
    ).values('id', 'payment_type')
    return JsonResponse({'methods': list(methods)})


@login_required
def payment_methods(request):
    methods = PaymentMethod.objects.filter(business=request.user)
    return render(request, 'payments/payment_methods.html', {
        'payment_methods': methods
    })'''
@login_required
def initiate_payment(request):
    """Initiate a payment for an order"""
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order_id')
            payment_type = request.POST.get('payment_type')
            
            order = Order.objects.get(id=order_id, business=request.user)
            
            if payment_type == 'mpesa':
                gateway = MpesaGateway(request.user)
                result = gateway.initiate_payment(
                    phone=request.POST.get('phone'),
                    amount=order.total_amount,
                    reference=f"OR{order.id}"
                )
                transaction = Transaction.objects.create(
                    order=order,
                    payment_method=gateway.method,
                    amount=order.total_amount,
                    transaction_id=result['checkout_request_id'],
                    status='pending'
                )
                return JsonResponse({
                    'status': 'pending',
                    'transaction_id': transaction.id
                })
                
            elif payment_type == 'stripe':
                gateway = StripeGateway(request.user)
                result = gateway.create_payment_intent(
                    amount=order.total_amount,
                    currency=request.user.currency,
                    metadata={'order_id': order.id}
                )
                transaction = Transaction.objects.create(
                    order=order,
                    payment_method=gateway.method,
                    amount=order.total_amount,
                    transaction_id=result['id'],
                    status='pending'
                )
                return JsonResponse({
                    'status': 'requires_action',
                    'client_secret': result['client_secret'],
                    'transaction_id': transaction.id
                })
                
        except PaymentError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def payment_webhook(request, gateway):
    """Handle payment gateway webhooks"""
    if request.method == 'POST':
        # Implement webhook handling for each gateway
        return JsonResponse({'status': 'received'})
    return JsonResponse({'error': 'Invalid method'}, status=405)
# payments/views.py


