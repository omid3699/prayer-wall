from django.urls import path

from .views import (
    AnonymousUserCreate,
    AnonymousUserDelete,
    AnonymousUserDetail,
    AnonymousUserList,
    EmailObtainAuthToken,
    EmailVerificationConfirm,
    EmailVerificationRequest,
    UserDelete,
    UserDetail,
    UserList,
    UserRegister,
    UserUpdate,
)


app_name = "users"

urlpatterns = [
    path("auth/token/", EmailObtainAuthToken.as_view(), name="api-token-auth"),
    path("register/", UserRegister.as_view(), name="register"),
    path("verify/resend/", EmailVerificationRequest.as_view(), name="verify-resend"),
    path("verify/confirm/", EmailVerificationConfirm.as_view(), name="verify-confirm"),
    path("me/", UserDetail.as_view(), name="me"),
    path("update/", UserUpdate.as_view(), name="update"),
    path("delete/", UserDelete.as_view(), name="delete"),
    path("anonymous/", AnonymousUserList.as_view(), name="anonymous-list"),
    path("anonymous/create/", AnonymousUserCreate.as_view(), name="anonymous-create"),
    path(
        "anonymous/<uuid:id>/", AnonymousUserDetail.as_view(), name="anonymous-detail"
    ),
    path(
        "anonymous/<uuid:id>/delete/",
        AnonymousUserDelete.as_view(),
        name="anonymous-delete",
    ),
    path("<uuid:id>/", UserDetail.as_view(), name="detail"),
    path("", UserList.as_view(), name="list"),
    path("<uuid:id>/update/", UserUpdate.as_view(), name="update-by-id"),
    path("<uuid:id>/delete/", UserDelete.as_view(), name="delete-by-id"),
]
