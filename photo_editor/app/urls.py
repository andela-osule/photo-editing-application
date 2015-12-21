from django.conf.urls import url
import app.views as views

urlpatterns = [
    url(r'^$', views.AppView.as_view(), name='app.index'),

    url(r'^login/$', views.AuthView.as_view(), name='app.auth.login'),

    url(r'^photos/$', views.JSONPhotosView.as_view(), name='app.photos'),

    url(r'^privacy/$', views.PrivacyView.as_view(), name='app.privacy'),

    url(r'^logout/$', views.DeAuthView.as_view(), name='app.auth.logout'),

    url(r'^photo/share/$', views.ShareView.as_view(), name='app.photo.share'),

    url(r'^photo/(?P<photo_id>[0-9]+)/delete/$', views.DestroyPhotoView
        .as_view(), name='app.photo.destroy'),

    url(r'^photo/(?P<photo_id>[0-9]+)/update/$', views.UpdatePhotoTitleView
        .as_view(), name='app.photo.update'),

    url(r'^photo/(?P<photo_id>[0-9]+)/fx/(?P<fx>[a-zA-Z0-9\s]+)/$', views
        .JSONFxApplyView.as_view(), name='app.fx.apply'),

    url(r'^upload/$', views.UploadPhotoView.as_view(),
        name='app.photo.upload'),

    url(r'^settings/effects/$', views.JSONFxListView
        .as_view(), name='app.availablefx'),

    url(r'^(?P<filename>(sitemap.xml)|(robots.txt)|(humans.txt))$',
        views.RootFilesView.as_view(), name='app.root_files'),
]
