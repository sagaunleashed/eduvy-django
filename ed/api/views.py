from os import stat
import re
from django.contrib.auth.models import update_last_login
from rest_framework import serializers, status,generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from ed.models import Branch, introBanner, planBanner
from users.models import NewUser
from rest_framework.permissions import AllowAny, DjangoModelPermissions,BasePermission, IsAuthenticated, SAFE_METHODS, IsAdminUser
from .serializers import BranchViewSerializer, LoginSerializers, RegisterUserSerializer
from rest_framework_simplejwt.tokens import RefreshToken, Token
from rest_framework.authtoken.models import Token
from rest_framework import viewsets

# class UserWritePermission(BasePermission):
#     message  ='Editing is restricted to author and admin only.'
    
#     def has_object_permission(self, request, view, obj):
#         if request.method in SAFE_METHODS:
#             return True
#         return obj.user == request.user

class BranchViewList(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Branch.objects.all()
    serializer_class = BranchViewSerializer


class BranchDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAdminUser]
    queryset = Branch.objects.all()
    serializer_class = BranchViewSerializer
    
    

class CustomUserCreate(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        reg_serializer = RegisterUserSerializer(data = request.data)
        if reg_serializer.is_valid():
            newuser = reg_serializer.save()
            if newuser:
                return Response(status=status.HTTP_201_CREATED)
        return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class Branch(viewsets.ViewSet):
#     # permission_classes = [IsAuthenticated]
#     # queryset = Branch.objects.all()
#     # def list(self,requset): 
#     pass
        




# class BlacklistTokenView(APIView):
#     permission_classes = [AllowAny]
    
#     def post(self,request):
#         try:
#             refresh_token = request.data['refresh_token']
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#         except Exception as e:
#             return Response(status = status.HTTP_400_BAD_REQUEST)
            
            
            
# class LoginAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = LoginSerializers(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         update_last_login(None, user)
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({"status": status.HTTP_200_OK, "Token": token.key})
    
    
    
    
    
# @api_view(['GET','POST'])
# def branch(request):
#     queryset = Branch.objects.all().values()
#     data = list(queryset)
#     return Response(data)

# @api_view(['GET','POST'])
# def introbanner(request):
#     queryset = introBanner.objects.all().values()
#     data = list(queryset)
#     return Response(data)

# @api_view(['GET','POST'])
# def planbanner(request):
#     queryset = planBanner.objects.all().values()
#     data = list(queryset)
#     return Response(data)
