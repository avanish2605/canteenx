from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, StudentProfile, CanteenAdminProfile
from canteens.models import Canteen


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True)
    enrollment_number = serializers.CharField(write_only=True, required=False)
    canteen_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'mobile', 'role', 'password', 'password2', 'enrollment_number', 'canteen_id']

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email=normalized).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Normalize mobile
        mobile = attrs.get('mobile', '').strip()
        if mobile:
            # Check unique mobile
            if User.objects.filter(mobile=mobile).exists():
                raise serializers.ValidationError({"mobile": "A user with this mobile number already exists."})
            attrs['mobile'] = mobile

        role = attrs.get('role', 'student')
        if role == 'student':
            enrollment = attrs.get('enrollment_number', '').strip().upper()
            if not enrollment:
                raise serializers.ValidationError({"enrollment_number": "Enrollment number is required for students."})
            if StudentProfile.objects.filter(enrollment_number=enrollment).exists():
                raise serializers.ValidationError({"enrollment_number": "This enrollment number is already registered."})
            attrs['enrollment_number'] = enrollment
        elif role == 'canteen_admin':
            canteen_id = attrs.get('canteen_id')
            if not canteen_id:
                raise serializers.ValidationError({"canteen_id": "Canteen selection is required for canteen admin."})
            if not Canteen.objects.filter(id=canteen_id).exists():
                raise serializers.ValidationError({"canteen_id": "Selected canteen does not exist."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        enrollment_number = validated_data.pop('enrollment_number', None)
        canteen_id = validated_data.pop('canteen_id', None)
        password = validated_data.pop('password')
        role = validated_data.get('role', 'student')

        if role == 'student':
            validated_data['is_active'] = False
            validated_data['is_email_verified'] = False
        elif role == 'canteen_admin':
            validated_data['is_staff'] = True
            validated_data['is_active'] = True
            validated_data['is_email_verified'] = True
        else:
            validated_data['is_active'] = True
            validated_data['is_email_verified'] = True

        user = User.objects.create_user(password=password, **validated_data)

        if user.role == 'student' and enrollment_number:
            StudentProfile.objects.create(user=user, enrollment_number=enrollment_number)
        elif user.role == 'canteen_admin' and canteen_id:
            canteen = Canteen.objects.get(id=canteen_id)
            CanteenAdminProfile.objects.create(user=user, canteen=canteen)

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            user_obj = None

        if user_obj and not user_obj.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        if user_obj and not user_obj.is_email_verified:
            from .models import EmailOTP
            from .services import generate_and_send_otp
            latest_otp = EmailOTP.objects.filter(user=user_obj, is_used=False).order_by('-created_at').first()
            if not latest_otp:
                generate_and_send_otp(user_obj)
            raise serializers.ValidationError({
                "detail": "Email address not verified. Please verify your OTP to activate your account.",
                "email_unverified": True,
                "email": user_obj.email,
            })

        if user_obj and not user_obj.is_active:
            raise serializers.ValidationError("Account is inactive.")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserDetailSerializer(user).data,
        }


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['id', 'enrollment_number', 'created_at']


class CanteenAdminProfileSerializer(serializers.ModelSerializer):
    canteen_name = serializers.CharField(source='canteen.name', read_only=True)

    class Meta:
        model = CanteenAdminProfile
        fields = ['id', 'canteen', 'canteen_name', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(read_only=True)
    canteen_admin_profile = CanteenAdminProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'mobile', 'role', 'is_active', 'is_email_verified',
                  'created_at', 'student_profile', 'canteen_admin_profile']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'mobile']
