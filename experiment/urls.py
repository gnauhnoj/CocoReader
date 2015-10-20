from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'annotations', views.annotations, name='annotations'),
    url(r'random', views.get_random_image, name='random'),
    url(r'^surveyq/(?P<img_id>\w{0,50})/$', views.get_survey_options, name='surveyq'),
    url(r'^surveyc/(?P<cap_id>\w{0,50})/$', views.get_survey_image, name='surveyc'),
]
