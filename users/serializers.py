from django.contrib.auth.models import User
from rest_framework import serializers
from .models import StudentProfile, Parent,Setting
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from masarat.enums import AcademicYear
# Student Profile Serializer
class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = [
            "academic_year",
            "parent",
            "learning_type",
            "first_time_login",
            "phone_number",
            "gender",
            "date_of_birth",
            "profile_picture",
            "major",
        ]
        extra_kwargs = {
            "academic_year": {"required": True},
            "learning_type": {"required": True},
            "first_time_login": {"default": True},
            "phone_number": {"required": False, "allow_null": True},
            "gender": {"required": False, "allow_null": True},
            "date_of_birth": {"required": False, "allow_null": True},
            "profile_picture": {"required": False, "allow_null": True},
            "major": {"required": False, "allow_null": True},
        }
        
    def update(self, instance, validated_data):
        # Update attributes or keep existing values if not provided
        instance.academic_year = validated_data.get("academic_year", instance.academic_year)
        instance.parent = validated_data.get("parent", instance.parent)
        instance.learning_type = validated_data.get("learning_type", instance.learning_type)
        instance.first_time_login = validated_data.get("first_time_login", instance.first_time_login)
        instance.phone_number = validated_data.get("phone_number", instance.phone_number)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.date_of_birth = validated_data.get("date_of_birth", instance.date_of_birth)
        profile_picture = validated_data.get("profile_picture", None)
        if profile_picture:
            instance.profile_picture = profile_picture
        instance.major = validated_data.get("major", instance.major)
        instance.save()
        return instance

    def to_representation(self, instance):
        # Get the default representation from the model fields
        representation = super().to_representation(instance)
        
        # Convert academic_year to Arabic value
        academic_year_value = instance.academic_year
        if academic_year_value in AcademicYear.values:
            # Find the Arabic translation for the academic_year
            arabic_value = dict(AcademicYear.choices).get(academic_year_value)
            representation["academic_year"] = arabic_value  # Replace the academic_year with its Arabic value
        
        return representation

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "first_name", "last_name", "student_profile"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        student_profile_data = validated_data.pop("student_profile")
        user = User.objects.create_user(**validated_data)
        StudentProfile.objects.create(user=user, **student_profile_data)
        return user

    def update(self, instance, validated_data):
        student_profile_data = validated_data.pop("student_profile", None)
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
        instance.save()

        if student_profile_data:
            student_profile = instance.student_profile
            for attr, value in student_profile_data.items():
                setattr(student_profile, attr, value)
            student_profile.save()
        
        return instance
    


# Parent Serializer
class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = ["email", "phone_number", "password"]
        extra_kwargs = {
            "password": {"write_only": True}  # You may want to hash this if needed
        }
        
    def create(self, validated_data):
        # This method will ensure the parent instance is created securely
        return Parent.objects.create(**validated_data)









# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer()
    parent = ParentSerializer()  # Add parent field

    class Meta:
        model = User
        fields = ["username", "password", "email", "first_name", "last_name", "student_profile", "parent"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Extract parent and student profile data
        parent_data = validated_data.pop("parent")
        student_profile_data = validated_data.pop("student_profile")

        # Create user
        user = User.objects.create_user(
            **validated_data  # This includes username, password, first_name, last_name, and email
        )

        # Create parent using ParentSerializer
        parent_serializer = ParentSerializer(data=parent_data)
        parent_serializer.is_valid(raise_exception=True)
        parent = parent_serializer.save()

        # Create student profile and link to the parent
        StudentProfile.objects.create(user=user, parent=parent, **student_profile_data)

        # Create the Setting instance for the new user
        Setting.objects.create(user=user)  # Create default settings for the user

        return user












class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Ensure that a user with this email exists
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Ensure that the new password and confirm password match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        # Ensure that the old password is correct
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data):
        # Ensure that the old password and new password are different
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("New password cannot be the same as the old password.")
        return data
    


# Custom Token Serializer to include first_time_login flag
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Check for the user's first-time login status
        user = self.user
        try:
            student_profile = StudentProfile.objects.get(user=user)
            data['first_time_login'] = student_profile.first_time_login

            # Optionally, reset first_time_login to False after the first login
            if student_profile.first_time_login:
                student_profile.first_time_login = False
                student_profile.save()
        except StudentProfile.DoesNotExist:
            data['first_time_login'] = False
            data['error'] = "StudentProfile does not exist."

        return data
    



class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = [
            "user",
            "camera_on_or_off",
            "theme",
            "sound_level",
        ]
        extra_kwargs = {
            "camera_on_or_off": {"default": False},
            "theme": {"default": "default"},
            "sound_level": {"default": 50, "min_value": 0, "max_value": 100},
        }

    def create(self, validated_data):
        # Create the Setting instance linked to the user
        return Setting.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Update fields or keep the existing values if not provided
        instance.camera_on_or_off = validated_data.get("camera_on_or_off", instance.camera_on_or_off)
        instance.theme = validated_data.get("theme", instance.theme)
        instance.sound_level = validated_data.get("sound_level", instance.sound_level)
        instance.save()
        return instance
    


from .models import SchoolApplication
from rest_framework import serializers

class SchoolApplicationCustomSerializer(serializers.ModelSerializer):
    userType = serializers.CharField(source='role')
    applicantName = serializers.CharField(source='applicant_name')
    position = serializers.CharField(source='applicant_job_title')
    phone = serializers.CharField(source='applicant_phone')
    email = serializers.EmailField(source='applicant_email')
    schoolName = serializers.CharField(source='school_name')
    country = serializers.CharField(source='school_country')
    userEmail = serializers.EmailField(source='school_email')
    userPhone = serializers.CharField(source='school_phone')

    class Meta:
        model = SchoolApplication
        fields = [
            'userType',
            'applicantName',
            'position',
            'phone',
            'email',
            'schoolName',
            'country',
            'userEmail',
            'userPhone'
        ]
