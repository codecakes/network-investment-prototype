"""avicrypto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^', include('addons.accounts.urls', namespace="accounts")),
    url(r'^package/', include('addons.packages.urls', namespace="package")),
    url(r'^transaction/', include('addons.transactions.urls', namespace="transaction")),
    url(r'^wallet/', include('addons.wallet.urls', namespace="wallet")),
    url(r'^admin/', admin.site.urls),
    url(r'^django-rq/', include('django_rq.urls'))
]

# if not settings.DEBUG:
#     urlpatterns += url('',
#         (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
#             'document_root': settings.STATIC_ROOT
#         }),
#     )

urlpatterns += static(settings.STATIC_ROOT, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
