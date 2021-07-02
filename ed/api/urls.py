from django.urls import path,include
from ed.api.views import *

# from rest_framework import routers

# router = routers.DefaultRouter()
# router.register('branch',BranchView)

app_name = "eduvy_api"

urlpatterns = [
    # path('branchview/',include(router.urls)),
    path('branchlist/',BranchViewList.as_view(),name="branchlist"),
    path('branchlist/<int:pk>/',BranchDetail.as_view(),name="branchdetail"),
    path('register/',CustomUserCreate.as_view(),name="create_user"),
    # path('branch/',Branch.as_view(),name="create_user"),
    # path('logout/blacklist/',BlacklistTokenView.as_view(),name="create_user"),
    # path('login/',LoginAPIView.as_view(),name="create_user"),
    path('api-auth/',include('rest_framework.urls','rest_framework')),
    # path('branch/',branch),
    # path('planbanner/',planbanner),
    # path('introbanner/',introbanner)
]
