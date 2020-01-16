from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('primer/', views.primer, name='primer'),
    path('amplicon/', views.amplicon, name='amplicon'),
    path('order/', views.order, name='order'),
    path('submitted/', views.submitted, name='submitted'),
    path('ordered/', views.ordered, name='ordered'),
    path('order_to_amplicon/', views.order_to_amplicon, name='order_to_amplicon'),
    path('submitted_to_amplicon/', views.submitted_to_amplicon, name='submitted_to_amplicon'),
    path('reorder_primer/', views.reorder_primer, name='reorder_primer'),
    path('archive_primer/', views.archive_primer, name='archive_primer')
]
