from django.shortcuts import render
from rest_framework import generics, authentication, permissions
from api_user import serializers
from core.models import Profile, FriendRequest
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from core import custompermissions

class CreateUserView(generics.CreateAPIView):
    serializer_class = serializers.UserSerializer

class FriendRequestViewSet(viewsets.ModelViewSet):
    # querysetはdbから帰ってきた結果が格納される、今回はallだから全て持ってきてる
    queryset = FriendRequest.objects.all()
    serializer_class = serializers.FriendRequestSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # getによる取得
    def get_queryset(self):
        return self.queryset.filter(Q(askTo=self.request.user) | Q(askFrom=self.request.user))

    # 新規作成
    def perform_create(self, serializer):
        try:
            # serializerがログイン中のユーザーをとってきて、askFromに割り当ててからdbに送ってくれるようになる
            serializer.save(askFrom=self.request.user)
        except:
            # unique_together = (('askFrom', 'askTo'),)をキャッチする
            raise ValidationError("User can have only unique request")

    # delete,updateはオーバーライドして無効にする
    def destroy(self, request, *args, **kwargs):
        response = {'message': 'Delete is not allowed !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    def partial_update(self, request, *args, **kwargs):
        response = {'message': 'Patch is not allowed !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, custompermissions.ProfilePermission)

    # userProにユーザを割り当ててからprofileをつくるようにする、こうすることでフロントで割り当てる必要がなくなる
    def perform_create(self, serializer):
        serializer.save(userPro=self.request.user)

class MyProfileListView(generics.ListAPIView):

    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(userPro=self.request.user)