"""avicrypto URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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

from . import views
# from views import ResetPasswordRequestView

urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_fn, name='login'),
    url(r'^signup', views.Registration.as_view(), name='signup'),

    url(r'^check-referal$', views.check_referal, name='check_referal'),
    url(r'^check-placement$', views.check_placement, name='check_placement'),

    url(r'^profile', views.profile, name='profile'),
    url(r'^home', views.home, name='dashboard'),
    url(r'^thanks$', views.thanks, name='thanks'),
    url(r'^error$', views.error, name='Error'),
    url(r'^logout$', views.logout_fn, name='Secure logout'),
    url(r'^network$', views.network, name='network'),
    url(r'^support$', views.support, name='support'),
    url(r'^uploads/simple/$', views.simple_upload, name='simple_upload'),
    url(r'^uploads/form/$', views.model_form_upload, name='model_form_upload'),
    url(r'^add/user/', views.add_user, name='profile'),
    url(r'^reset-password/(?P<token>.+)$', views.reset_password, name='reset_password'),
    # url(r'^add/user/(?P<id>[a-zA-Z0-9]{0,30})/$',views.add_user, name='add_user'),
]


