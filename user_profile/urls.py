from django.urls import path
from . import views
from rest_framework.authtoken import views as tokenviews

urlpatterns = [
    path('', views.UserView.as_view()),
    path('api-token-auth/', tokenviews.obtain_auth_token),
    # otpverifyrequest POST otpgenerate GET Token Based
    path('otp/', views.OtpViewClass.as_view()),
    path('<int:u_id>', views.specific_user_view)
]
