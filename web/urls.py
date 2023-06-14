from django.urls import re_path as url
from . import views


urlpatterns = [
    url(r'^dashboard/$', views.Home, name='home'),
    url(r'^login/$', views.Login, name='login'),
    url(r'^register/$', views.Register, name='register'),
    url(r'^profile/$', views.Profile, name='profile'),
    url(r'^inter-bank/$', views.InterBank, name='inter'),
    url(r'^other-bank/$', views.OtherBank, name='other'),
    url(r'^transactions/$', views.Transactions, name='transactions'),
    url(r'^withdrawal/$', views.Withdrawal, name='withdrawal'),
    url(r'^loan/$', views.Loan, name='loan'),
    url(r'^deposit/$', views.Deposit, name='deposit'),
    url(r'^logout/$', views.Logout, name='logout'),
    url(r'^transfer/$', views.MakeTransfer, name='transfer'),
    url(r'^account-details/$', views.AccountDetail, name='account'),

    # home
    url(r'^$', views.Home, name='index'),
]
