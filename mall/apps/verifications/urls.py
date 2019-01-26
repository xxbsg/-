from django.conf.urls import url

from . import views

urlpatterns=[
    url(r'^imagecodes/(?P<image_code_id>.+)/$',views.RegisterImageAPIView.as_view(),name='imagecode'),
    url(r'^smscodes/(?P<mobile>1[345789]\d{9})/$',views.RegisterSmscodeAPIView.as_view()),
    ############################################################
    url(r'^(?P<username>\w+)/sms/token/$',views.UserForgetPasswordAPIView.as_view()),
    # GET / sms_codes /?access_token = '+ this.access_token
    url(r'^sms_codes/$',views.SendSmsCodeAPIView.as_view()),
    url(r'^password/token/$',views.ValidateSmsCodeAPIView.as_view())
]