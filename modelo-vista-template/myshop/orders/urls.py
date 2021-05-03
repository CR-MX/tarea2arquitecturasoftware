#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: urls.py
#
# Descripción:
#   En este archivo se definen las urls de la app de las órdenes.
#
#   Cada url debe tener la siguiente estructura:
#
#   path( url, vista, nombre_url )
#
#-------------------------------------------------------------------------

from django.urls import path, include
from . import views


urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    #path('listOrders/', views.ListOrders.as_view(), name='listOrders'),
    path('ordenes/', views.listOrders, name='ordenes'),# lista de ordenes
    path('info/<str:pk>/', views.listOrder, name='info'),
    path('delete_order/<str:pk>/', views.deleteOrder, name='delete_order'),
    path('delete_product/<str:pk>/', views.deleteProduct, name='delete_product'),

]
