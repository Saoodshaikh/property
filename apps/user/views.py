from django.shortcuts import render
from rest_framework import viewsets
from .serializers import UserRegisterSerializer, LoginSerializer, UserKYCSerializer
from .models import CustomUser, UserKYC
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .task import send_otp_task, verify_aadhar_otp_task

class CustomUserViewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = (UserRegisterSerializer, UserKYCSerializer)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=False, methods=['post'])
    def login(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh':str(refresh),
                    'access':str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserKYCViewset(viewsets.ModelViewSet):
    queryset = UserKYC.objects.all()
    serializer_class = UserKYCSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Ensure only User can read their records"""
        return UserKYC.objects.filter(user= self.request.user)
    
    def create(self, request, *args, **kwargs):
        if UserKYC.objects.filter(user=self.request.user).exists():
            return Response({"error": "kYC already verified "})

    # Custom Action to generate the OTP
    @action(detail=True, methods=['post'])
    def generate_otp(self, request, pk=None):
        user_kyc = self.get_object()

        if user_kyc.verification_method == 'aadhar_card':
            aadhar_number = user_kyc.aadhar_card_number

            # Use Celery to Send OTP Asynchronoulsy
            send_otp_task.delay(user_kyc.id, aadhar_number)
            return Response({"message": "OTP task creaton is "})
        else:
            return Response({"error": "OTP can only be generate for Aadhar card only"})
    
    @action(detail=True, methods=['post'])
    def verify_otp(self, request, pk=None):
        user_kyc = self.get_object()
        entered_otp = request.data.get('otp')

        if not entered_otp:
            return Response({"error": "Please provide otp"}, status=status.HTTP_400_BAD_REQUEST)
        
        if user_kyc.verification_method == 'aadhar_card':
            aadhar_number = user_kyc.aadhar_card_number

            otp_verified, message = verify_aadhar_otp_task.delay(aadhar_number, entered_otp)
            if otp_verified:
                user_kyc.is_verified = True
                user_kyc.status = 'verified'
                user_kyc.save()
                return Response({"Message": "OTP verified succesfully"}, status=status.HTTP_200_OK)
            
            else:
                return Response({"Error": message}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"error": "OTP verification is only application for Aadhar number"}, status=status.HTTP_400_BAD_REQUEST)










        

        
        



   
    
    
    


