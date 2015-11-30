from django.conf.urls import url
import app.views as views

urlpatterns = [
        url(r'^(?P<filename>(sitemap.xml)|(robots.txt)|(humans.txt))$',
            views.RootFilesView.as_view(), name='app.root_files'),
    ]
