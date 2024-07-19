from django.urls import path
from payment import views as pay


urlpatterns = [
    path('payment/',pay.PaymentSuccesView.as_view(), name="payment_success")
]
