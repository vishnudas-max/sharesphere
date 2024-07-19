import json
import razorpay
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.conf import settings




class PaymentSuccesView(APIView):
        permission_classes = [IsAuthenticated]
        authentication_classes = [JWTAuthentication]

        def post(self, request):
             amount = request.data.get('amount', 0)  # Amount in paise
             plan = request.data.get('plan')
             currency = 'INR'
             receipt = 'receipt#1'
             client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))
             
             order_data = {
                 'amount': amount,
                 'currency': currency,
                 'receipt': receipt,
             }
             print('wokrking')
             try:
                 order = client.order.create(order_data)
                 return Response({
                     'order_id': order.get('id'),
                     'amount': order_data['amount'],
                     'currency': order_data['currency'],
                     'plan':plan
                 }, status=status.HTTP_200_OK)
             except Exception as e:
                 return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
        def patch(self, request):
            amount = request.data.get('amount')
            plan = request.data.get('plan')
            user = request.user
    
            try:
                verification_instance = user.verificationData
                verification_instance.is_subscribed = True
                verification_instance.amount_paid = amount
                verification_instance.plan_choosed = plan
                verification_instance.subscribed_date = timezone.now()
                verification_instance.save()
                user.is_verified = True
                user.save()
                return Response({'message': 'Subscription details updated successfully'}, status=status.HTTP_200_OK)
            # except Verification.DoesNotExist:
            #     return Response({'error': 'Verification instance not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)