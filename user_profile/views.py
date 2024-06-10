from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import UserSerializer
from .customfunctions import password_valid, generateOTP, customSHA256, username_valid
from django.conf import settings
from django.core.mail import send_mail
import datetime
from .custompermissions import IsOtpAllowed, IsVerified
from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.


class UserView(APIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            # Apply IsAuthenticated for DELETE requests
            return [IsAuthenticated()]
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        if self.request.method == 'PATCH':
            return [IsVerified()]
        if self.request.method == 'POST':
            return [AllowAny()]

    def get(self, request):
        user = request.user
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        if (data.get('username')):
            if not username_valid(data.get('username')):
                return Response({'message': 'Username invalid'}, status=status.HTTP_400_BAD_REQUEST)

        if (data.get('password')):
            if not password_valid(data.get('password')):
                return Response({'message': 'Password must contain one lower case, one upper case, one digit and one special character'}, status=status.HTTP_400_BAD_REQUEST)

        user_serializer = UserSerializer(data=data)

        if (user_serializer.is_valid()):
            saved_user = user_serializer.save()
            return Response(UserSerializer(saved_user).data, status=status.HTTP_201_CREATED)

        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # Create a mutable copy else data['user profile'] not allowrd
        # for some reason query dict is not working need to look so converted to python dict
        data = request.data

        if (data.get('username')):
            if not username_valid(data.get('username')):
                return Response({'message': 'Username invalid'}, status=status.HTTP_400_BAD_REQUEST)

        if (data.get('password')):
            if not password_valid(data.get('password')):
                return Response({'message': 'Password must contain one lower case, one upper case, one digit and one special character'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user_serializer = UserSerializer(user, data=data, partial=True)
        if (user_serializer.is_valid()):
            user = user_serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_202_ACCEPTED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            User.objects.get(pk=request.user.id).delete()
            return Response({'message': f'Account deleted'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)


class OtpViewClass(APIView):
    # Need to modify perfmission classes to authenticated but not verified
    permission_classes = [IsOtpAllowed]

    def get(self, request):
        now = datetime.datetime.now(datetime.timezone.utc)
        user = User.objects.get(pk=request.user.id)
        user_profile = user.user_profile
        otp_created_on = user_profile.otp_created_on
        allow_otp = False
        timedelta = 0
        # to check if created on is null or not
        if (not otp_created_on):
            allow_otp = True
        else:
            # convert into minutes
            timedelta = (now-otp_created_on).seconds/60

        # send otp if time is more than 10 minutes
        try:
            if (timedelta > 10 or allow_otp):
                user_profile.otp_created_on = now
                otp = generateOTP()
                user_profile.otp = customSHA256(otp)
                subject = "OTP Verification Code"
                message = "Please verify your account using the code {}.\nThis OTP is only valid for 10 minutes.\nDo not share this with anyone.".format(
                    otp)
                sender = settings.EMAIL_HOST_USER
                reciever = [user.email]
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=sender,
                    recipient_list=reciever,
                    fail_silently=False,
                )
                user_profile.save()
                return Response({'message': 'OTP sent to email'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Otp has already been sent to email'}, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        user_profile = user.user_profile
        data = request.data

        now = datetime.datetime.now(datetime.timezone.utc)
        timedelta = 0

        if (user_profile.otp_created_on):
            otp = data.get('otp')
            timedelta = (now-user_profile.otp_created_on).seconds/60

            # check if otp is provided or not
            if (not otp):
                return Response({'message': f'Otp not provided'}, status=status.HTTP_400_BAD_REQUEST)

            if (len(otp) != 6):
                return Response({'message': f'Otp not valid'}, status=status.HTTP_400_BAD_REQUEST)

            otp_sha = customSHA256(otp)
            saved_otp = user_profile.otp

            if (timedelta > 10):
                return Response({'message': f'Otp is only valid for 10 minutes'}, status=status.HTTP_400_BAD_REQUEST)

            if (otp_sha == saved_otp):
                user_profile.verified = True
                user_profile.save()
                return Response({'message': f'Account verified'}, status=status.HTTP_201_CREATED)

            return Response({'message': f'otp incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'Otp has not been requested'}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsVerified])
@api_view(['GET'])
def specific_user_view(request, u_id):
    if request.method == 'GET':
        try:
            user = User.objects.get(pk=u_id)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"message':'User doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
