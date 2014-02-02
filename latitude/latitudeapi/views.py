from sqlite3 import IntegrityError
from django.shortcuts import render

from rest_framework import generics, mixins, status
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from serializers import LocationSerializer,UserSerializer,FriendSerializer,CurrentLocationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action,link, authentication_classes
from models import Location,CurrentLocation, FriendShip
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
import datetime
# Create your views here.
class LocationService(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin):
    serializer_class = LocationSerializer
    model = Location
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,SessionAuthentication,)

    def pre_save(self,obj):
        obj.owner = self.request.user

    def get_queryset(self):
        return Location.objects.filter(owner = self.request.user).all()

@api_view(['GET'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated, ))
def get_friends_loc(request):
    friends = [_.to_friend for _ in request.user.friend_set.all()]
    locs = CurrentLocation.objects.filter(owner__in=friends)
    serializer = CurrentLocationSerializer(locs, many=True)
    return Response(serializer.data)

class FriendService(viewsets.GenericViewSet,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin):
    model = FriendShip
    serializer_class = FriendSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,SessionAuthentication,)

    def pre_save(self, obj):
        obj.from_friend = self.request.user

    def create(self, request, *args, **kwargs):
        #TODO: hack refer to issue: https://github.com/tomchristie/django-rest-framework/issues/821
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            if FriendShip.isFriend(serializer.object.from_friend, serializer.object.to_friend):
                return Response("%s is already friend with %s" % (serializer.object.from_friend,serializer.object.to_friend),
                    status = status.HTTP_400_BAD_REQUEST)
            elif serializer.object.from_friend == serializer.object.to_friend:
                return Response("cannot add friend to oneself", status = status.HTTP_400_BAD_REQUEST)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return self.request.user.friend_set.all()


class UserService(viewsets.GenericViewSet, mixins.CreateModelMixin):
    model = User
    serializer_class = UserSerializer
    #permission_classes = (IsAuthenticated,)