from warn_relaction_interface import view
from django.conf.urls import url
from django.views import static
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    url(r'^$', view.start),
    url(r'warn_realtion', view.warn_realtion),
    url(r'get_resu_process', view.get_resu_process),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
