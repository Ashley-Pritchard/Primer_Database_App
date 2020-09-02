from django.urls import path, re_path
from . import views

#urls - each corresponds to both a html page in the templates directory and a function in the views.py file

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r"^loginview/$", views.loginview, name="loginview"),
    re_path(r"^change_password/$", views.change_password, name="change_password"),
    re_path(r'search/(.*)/$', views.search, name='search'),
    re_path(r'amplicon/(.*)/$', views.amplicon, name='amplicon'),
    path('order/', views.order, name='order'),
    re_path(r'order_form/(.*)/$', views.order_form, name='order_form'),
    path('ordered/', views.ordered, name='ordered'),
    re_path(r'reorder_archive_primer/(.*)/(.*)/$', views.reorder_archive_primer, name='reorder_archive_primer'),
    path('order_placed/', views.order_placed, name='order_placed'),
    path('location_updated/', views.location_updated, name='location_updated'),
    re_path('in_testing/(.*)/$', views.in_testing, name='in_testing'),
    path('failed/', views.failed, name='failed'),
    path('remove_failed/', views.remove_failed, name='remove_failed'),
    path('retesting/', views.retesting, name='retesting'),
    path('retested/', views.retested, name='retested')
]
