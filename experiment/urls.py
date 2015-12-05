from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^annotations/$', views.annotations, name='annotations'),
    url(r'^random/$', views.get_random_image, name='random'),
    url(r'^randomocr/$', views.get_random_ocr, name='randomocr'),
    url(r'^surveyq/(?P<img_id>\w{0,50})/$', views.get_survey_options, name='surveyq'),
    url(r'^surveyc/(?P<img_id>\w{0,50})/$', views.get_survey_image, name='surveyc'),
    url(r'^getscore/(?P<username>\w{0,50})/$', views.get_user_score, name='getscore'),
    url(r'^updatescore/(?P<username>\w{0,50})$', views.update_score, name='updatescore'),
    url(r'^leaderboard/$', views.get_leaderboard, name='leaderboard'),
    url(r'^recordoutcome$', views.record_outcome, name='recordoutcome'),
    url(r'^getnextuser/$', views.get_next_user_num, name='getnextuser'),
]
