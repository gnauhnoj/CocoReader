from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'annotations', views.annotations, name='annotations'),
    url(r'random', views.get_random_image, name='random'),
    ]
