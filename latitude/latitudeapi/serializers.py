__author__ = 'hqdvista'

from rest_framework import serializers
from rest_framework.serializers import RelatedField
from latitudeapi.models import Location,FriendShip, CurrentLocation
from django.contrib.auth.models import User

class LocationSerializer(serializers.ModelSerializer):
    #ts = serializers.Field(source = 'convert_to_epoc')
    ts = serializers.DateTimeField(required=False, source='ts')
    class Meta:
        model = Location
        fields = ('ts', 'lat', 'lon', 'prec')

class CurrentLocationSerializer(serializers.ModelSerializer):
    owner = serializers.Field(source='owner.username')
    loc = LocationSerializer()
    class Meta:
        model = CurrentLocation
        fields = ('owner','loc')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'password', 'username','email']

    def restore_object(self, attrs, instance=None):
        user = super(UserSerializer,self).restore_object(attrs,instance)
        user.set_password(attrs['password'])
        return user

    def to_native(self, obj):
        ret = super(UserSerializer,self).to_native(obj)
        del ret['password']
        return ret


class FriendSerializer(serializers.ModelSerializer):
    #to_friend = UserSerializer()
    friend_name = serializers.SerializerMethodField('get_friend_name')
    class Meta:
        model = FriendShip
        fields = ('to_friend','friend_name')

    def get_friend_name(self,obj):
        if obj is not None:
            return obj.to_friend.username
