from django.db.models import fields
from django.http.request import validate_host
from rest_framework import serializers
from ed.models import *
from users.models import *
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

class BranchViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch        
        fields = ('id','BranchCode','BranchName','Image')
        
        
class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id','BranchName',]
        
class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewUser
        fields = ('email','password')
        extra_kwargs = {'password':{'write_only':True}}
        
    def create(self,validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    
class LoginSerializers(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        max_length=128,
        write_only=True
    )

    def validate(self, data):
        username = data.get('email')
        password = data.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data