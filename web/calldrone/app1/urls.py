from django.urls import path

from . import views

urlpatterns = [
    path('page1', views.page1, name='page1'),

    path('page2', views.page2, name='page2'),

    path('page3', views.page3, name='page3'),

    path('page4', views.page4, name='page4'),

    path('page5', views.page5, name='page5')
]