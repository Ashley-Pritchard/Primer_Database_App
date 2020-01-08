from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('primer/', views.primer, name='primer'),
    path('amplicon/', views.amplicon, name='amplicon'),
    path('order/', views.order, name='order')
]
