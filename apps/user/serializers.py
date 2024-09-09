from rest_framework import serializers
from .models import CustomUser, UserKYC
from django.core.validators import EmailValidator, MinLengthValidator
from django.contrib.auth import authenticate

class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[EmailValidator(message="Invalid Email address")])
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=True)
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=True)

    class Meta:
        model = CustomUser
        fields = ['id','email','first_name', 'last_name', 'password', 'password2', 'roll', 'phone_number', 'bank_account_info', 'tax_id']  # Exclude fields not needed for registration

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError({"Email": "This email already exists"})
        return value
    
    def validate(self, data):
        if data['password'] and len(data['password']) < 8:
            raise serializers.ValidationError({"Password": "The password must be at least 8 characters long"})
        
        if data['password2'] and len(data['password2']) < 8:
            raise serializers.ValidationError({"Password2": "Password2 must be at least 8 characters long"})
        
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"Password": "The password and re-entered password must match"})
        
        
        
        return data
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')  # Remove password2 as it is not needed in the User model

        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user
    
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def validate(self, data):
        if not data['email'] or not  data['password']:
            raise serializers.ValidationError("Email and password is must")
        user = authenticate(email=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid Email or Password")
        data['user'] =user

        return data
    

class UserKYCSerializer(serializers.ModelSerializer):
    
    class Meta:
        models = UserKYC
        fields = '__all__'

    def validate(self, data):
        verification_method = data.get('verification_method')
        aadhard_provided = data.get('aadhar_card_number') and data.get('aadhar_card_image')
        pancard_provided = data.get('pan_card_number') and data.get('pan_card_image')

        if verification_method:
            if not aadhard_provided:
                raise serializers.ValidationError("Adhar details must be provied ")
            if pancard_provided:
                raise serializers.ValidationError("Do not provided Pan card if verification method select adhar card")
            
        if verification_method:
            if not pancard_provided:
                raise serializers.ValidationError("Pac card is must if u select verification method Pan card")
            if aadhard_provided:
                raise serializers.ValidationError("Do not provide adhar card if U select verification method Pan")
        
        if data['aadhar_card_number'] and not data['aadhar_card_number'].isdigit():
            raise serializers.ValidationError('Addhar card number must be in Number')
        
        if data['pan_card_number'] and not data['pan_card_number'].isalnum():
            raise serializers.ValidationError('Pan card must be Combimnation of Alpha and number')
        
        
        return data
    




    

