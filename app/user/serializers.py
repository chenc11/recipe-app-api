"""
Serializers for the user API View.
"""
from django.contrib.auth import (
    get_user_model,
    # function comes with Django that allows you to
    # authenticate with authentication system
    authenticate,
)
from django.utils.translation import gettext as _
# serializer is a way to convert objects to and from python objects
from rest_framework import serializers


# automatically validate and save things to a specific model
# that we define in our serialization
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    # tell the Django Rest Framework the model and the fields and
    # any additional arguments that we
    # want to pass to the serializers and serialziers
    # need to know what model is representing
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        # cannot read password for security issue
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # overwrite the create method to be called after validation
    # and only be called when validation is successful
    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)
        # overwrite the create method and pass
        # only the validated data into serializer

    # overwrite the update method to make sure the password is hashed
    # instance: the model instance that's going to be updated
    # validated_data: the data that's already passed through
    # the serializer validation (email, pwd, name)
    def update(self, instance, validated_data):
        """Update and return user."""
        # retrieve the password from the validated data dictionary
        # and remove it in the dict after being retrieved
        # don't force the user to have pwd so default to none here
        password = validated_data.pop('password', None)
        # still keeping some function of the wheel while change only
        # things we need by calling the update
        # function provided by base serializer
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
