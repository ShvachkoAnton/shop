from django.http import request
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import OrderItem,Order
from .forms import OrderCreateForm
from cart.cart import Cart
from django.shortcuts import get_object_or_404

from  .tasks import order_created
# Create your views here.
def order_create(request):
    cart=Cart(request)
    if request.method=='POST':
        form=OrderCreateForm(request.POST)
        if form.is_valid():
            order=form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity'])
        cart.clear()
        #запуск асинхронной задачи
        order_created.delay(order.id)
        return render(request, 'order_created.html',
        {'order':order})
    else:
        form=OrderCreateForm()
    return render(request, 'order_create.html',{'cart':cart,
    'form':form})

    
@staff_member_required
def admin_order_detail(request,order_id):
    order=get_object_or_404(Order, id=order_id)
    return render(request,'admin_order_detail.html',{'order':order})
