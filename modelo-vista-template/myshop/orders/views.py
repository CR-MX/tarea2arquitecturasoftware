#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------------------------
# Archivo: views.py
#
# Descripción:
#   En este archivo se definen las vistas para la app de órdenes.
#
#   A continuación se describen los métodos que se implementaron en este archivo:
#
#                                               Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Verifica la infor- |
#           |                        |  - request: datos de     |    mación y crea la   |
#           |    order_create()      |    la solicitud.         |    orden de compra a  |
#           |                        |                          |    partir de los datos|
#           |                        |                          |    del cliente y del  |
#           |                        |                          |    carrito.           |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Crea y envía el    |
#           |        send()          |  - order_id: id del      |    correo electrónico |
#           |                        |    la orden creada.      |    para notificar la  |
#           |                        |                          |    compra.            |
#           +------------------------+--------------------------+-----------------------+
#
# --------------------------------------------------------------------------------------------------

from django.shortcuts import render, redirect
from .models import OrderItem, Order, Product
from django.views.generic import ListView
from .forms import OrderCreateForm, OrderItemForm
from django.core.mail import send_mail
from cart.cart import Cart

from django.utils import timezone
from django.http import HttpResponse
from django.forms import inlineformset_factory


def order_create(request):

    # Se crea el objeto Cart con la información recibida.
    cart = Cart(request)

    # Si la llamada es por método POST, es una creación de órden.
    if request.method == 'POST':

        # Se obtiene la información del formulario de la orden,
        # si la información es válida, se procede a crear la orden.
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])

            # Se limpia el carrito con ayuda del método clear()
            cart.clear()

            # Llamada al método para enviar el email.
            send(order.id, cart)
            return render(request, 'orders/order/created.html', {'cart': cart, 'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart,
                                                        'form': form})


def send(order_id, cart):
    # Se obtiene la información de la orden.
    order = Order.objects.get(id=order_id)

    # Se crea el subject del correo.
    subject = 'Order nr. {}'.format(order.id)

    # Se define el mensaje a enviar.
    message = 'Dear {},\n\nYou have successfully placed an order. Your order id is {}.\n\n\n'.format(
        order.first_name, order.id)
    message_part2 = 'Your order: \n\n'
    mesagges = []

    for item in cart:
        msg = str(item['quantity']) + 'x ' + str(item['product']
                                                 ) + '  $' + str(item['total_price']) + '\n'
        mesagges.append(msg)

    message_part3 = ' '.join(mesagges)
    message_part4 = '\n\n\n Total: $' + str(cart.get_total_price())
    body = message + message_part2 + message_part3 + message_part4

    # Se envía el correo.
    send_mail(subject, body, 'rxshark117@gmail.com',
              [order.email], fail_silently=False)


# Listado de todas las ordenes
def listOrders(request):  # listado
    order = Order.objects.all()
    return render(request, 'orders/order_list.html', {'order': order})
   
#Listado de los articulos de cada orden
def listOrder(request, pk): #Detalles # Por si falla
    order=Order.objects.get(id=pk)
    orderi = OrderItem.objects.filter(order=pk)
    context = {'order':order,'orderi':orderi}

    #como saber quien hizo el post
    if request.method == "POST":
        orderi.delete()
        return redirect('/')
    return render (request, 'orders/orderitem_list.html',context)



# correo Cancelación completa
def send_all_cancel(orderi, order, pk):
    orderi = OrderItem.objects.filter(order=pk)
    subject = 'Order nr. {}'.format(order.id) 
    message_part1 = 'Dear {},\n\n Your entire order was successfully cancelled. Your number order is {}.\n\n\n'.format(order.first_name,order.id)
    message_part2 = 'Your order: \n\n'
    message_dinamic=''
    total=0
    total_general=0
    for i in orderi:
        message_dinamic += 'Product: '
        message_dinamic += str(i.product)
        message_dinamic += ', Quantity: '
        message_dinamic += str(i.quantity)
        message_dinamic += ', Unit price: $'
        message_dinamic += str(i.price)
        message_dinamic += ', Total: $'
        total=int(i.price)*int(i.quantity)
        message_dinamic += str(total)
        total_general += total
        message_dinamic += '\n'
    message_dinamic +='\n\nTotal: $'
    message_dinamic +=str(total_general)

    body = message_part1 + message_part2 + message_dinamic
    send_mail(subject, body, 'rxshark117@gmail.com', [order.email], fail_silently=False)

# Elimina una orden completa
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    orderi = OrderItem.objects.filter(order=pk)
    if request.method == "POST":
        send_all_cancel(orderi, order, pk)
        order.delete()
        return redirect('/')
    context = {'order': order, 'orderi': orderi}
    return render(request, 'orders/delete.html', context)

#Correo Cancelacion parcial
def send_cancel_item(orderi,order, pk):
    subject = 'Order nr. {}'.format(order.id) 
    message_part1 = 'Dear {},\n\n This item was canceled. Your number order is {}.\n\n\n'.format(order.first_name,order.id)
    message_part2 = 'Your order: \n\n'
    message_dinamic=''
    total=0
    total_general=0
    for i in orderi:
        message_dinamic += 'Product: '
        message_dinamic += str(i.product)
        message_dinamic += ', Quantity: '
        message_dinamic += str(i.quantity)
        message_dinamic += ', Unit price: $'
        message_dinamic += str(i.price)
        message_dinamic += ', Total: $'
        total=int(i.price)*int(i.quantity)
        message_dinamic += str(total)
        total_general += total
        message_dinamic += '\n'
    message_dinamic +='\n\nTotal: $'
    message_dinamic +=str(total_general)
    body = message_part1 + message_part2 + message_dinamic
    send_mail(subject, body, 'rxshark117@gmail.com', [order.email], fail_silently=False)

#Eliminación parcial
def deleteProduct(request, pk): 
    orderi = OrderItem.objects.filter(id=pk)
    order = Order.objects.get(id=orderi.first().order_id)
    if request.method == "POST":
        # ya no hay mas items
        if OrderItem.objects.filter(order_id=orderi.first().order_id).count() == 1:
            print(order.email)
            order.delete()
            orderi.delete()
            send_cancel_item(orderi, order, pk)
        send_cancel_item(orderi, order, pk)  
        orderi.delete()
        return redirect('/')

    context = {'orderi': orderi, 'order_id': orderi.first().order_id}
    return render(request, 'orders/confirm_cancel_product.html', context)










