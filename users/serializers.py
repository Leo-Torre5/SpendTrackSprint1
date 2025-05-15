from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, Profile
from expenses.models import Category, Budget
from expenses.serializers import CategorySerializer
from rest_framework import serializers
from .models import CustomUser, Profile

class UpdateUserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    phone_number = serializers.CharField(required=False)
    street_address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)  # Added the city field
    zip_code = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'phone_number',
                  'street_address', 'city', 'zip_code', 'state', 'profile_picture']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        # Mise à jour des champs de l'utilisateur
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Mise à jour des champs du profil
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number', 'street_address', 'city', 'zip_code', 'state', 'profile_picture']
        extra_kwargs = {
            'profile_picture': {'required': False}
        }

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        # Update user fields
        instance = super().update(instance, validated_data)

        # Update profile fields
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    street_address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    zip_code = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'user_type', 'first_name', 'last_name',
                  'phone_number', 'street_address', 'city', 'state', 'zip_code', 'profile_picture')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user_type = validated_data.pop('user_type', 1)
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        phone_number = validated_data.pop('phone_number', '')
        street_address = validated_data.pop('street_address', '')
        city = validated_data.pop('city', '')
        state = validated_data.pop('state', '')
        zip_code = validated_data.pop('zip_code', '')
        profile_picture = validated_data.pop('profile_picture', None)

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            user_type=user_type,
            first_name=first_name,
            last_name=last_name,
        )

        # Get the default image path from the Profile model
        default_image = Profile.profile_picture.field.default

        Profile.objects.create(
            user=user,
            phone_number=phone_number,
            street_address=street_address,
            city=city,
            state=state,
            zip_code=zip_code,
            profile_picture=profile_picture if profile_picture else default_image, # Use provided image or default
        )

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_type'] = user.user_type
        return token


# Admin serializers

class AdminUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password',
            'first_name', 'last_name', 'user_type',
            'is_active', 'profile'
        ]

    def create(self, validated_data):
        # Extract profile data and password
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password', None)

        # Create user with proper password handling
        user = CustomUser.objects.create_user(
            **validated_data,
            password=password
        )

        # Update associated profile
        profile = user.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return user

    def update(self, instance, validated_data):
        # Profile data handling
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        # Password update handling
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile fields
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance


class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_default', 'created_by']
        read_only_fields = ['created_by']

    def create(self, validated_data):
        # Automatically set the created_by user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AdminBudgetSerializer(serializers.ModelSerializer):
    # For displaying data
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    # For writing data
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='user',
        write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Budget
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'category': {'read_only': True}
        }