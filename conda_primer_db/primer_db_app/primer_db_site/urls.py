from django.urls import path
from . import views

#urls - each corresponds to both a html page and a function in the views.py file 

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('primer/', views.primer, name='primer'),
    path('amplicon/', views.amplicon, name='amplicon'),
    path('order/', views.order, name='order'),
    path('order_form/', views.order_form, name='order_form'),
    path('submitted/', views.submitted, name='submitted'),
    path('ordered/', views.ordered, name='ordered'),
    path('order_to_amplicon/', views.order_to_amplicon, name='order_to_amplicon'),
    path('submitted_to_amplicon/', views.submitted_to_amplicon, name='submitted_to_amplicon'),
    path('reorder_primer/', views.reorder_primer, name='reorder_primer'),
    path('archive_primer/', views.archive_primer, name='archive_primer'),
    path('submit_order/', views.submit_order, name='submit_order'),
    path('order_placed/', views.order_placed, name='order_placed'),
    path('order_recieved/', views.order_recieved, name='order_recieved'),
    path('in_testing/', views.in_testing, name='in_testing'),
    path('tested/', views.tested, name='tested'),
    path('failed/', views.failed, name='failed')
]
