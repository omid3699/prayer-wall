from django.urls import path

from .views import (
    AnonymousUserCreate,
    AnonymousUserDelete,
    AnonymousUserDetail,
    AnonymousUserList,
    UserDelete,
    UserDetail,
    UserList,
    UserRegister,
    UserUpdate,
)


app_name = "users"

urlpatterns = [
    path("register/", UserRegister.as_view(), name="register"),
    path("me/", UserDetail.as_view(), name="me"),
    path("<int:id>/", UserDetail.as_view(), name="detail"),
    path("", UserList.as_view(), name="list"),
    path("update/", UserUpdate.as_view(), name="update"),
    path("<int:id>/update/", UserUpdate.as_view(), name="update-by-id"),
    path("delete/", UserDelete.as_view(), name="delete"),
    path("<int:id>/delete/", UserDelete.as_view(), name="delete-by-id"),
    path("anonymous/", AnonymousUserList.as_view(), name="anonymous-list"),
    path("anonymous/create/", AnonymousUserCreate.as_view(), name="anonymous-create"),
    path("anonymous/<int:id>/", AnonymousUserDetail.as_view(), name="anonymous-detail"),
    path(
        "anonymous/<int:id>/delete/",
        AnonymousUserDelete.as_view(),
        name="anonymous-delete",
    ),
]
