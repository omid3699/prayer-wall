from django.urls import path

from .views import (
    MyPrayerRequestsList,
    MyPrayersList,
    PrayerCreate,
    PrayerDelete,
    PrayerList,
    PrayerRequestApprove,
    PrayerRequestCreate,
    PrayerRequestDelete,
    PrayerRequestDetail,
    PrayerRequestList,
    PrayerRequestUpdate,
)


app_name = "prayers"

urlpatterns = [
    path("", PrayerRequestList.as_view(), name="list"),
    path("create/", PrayerRequestCreate.as_view(), name="create"),
    path("my/", MyPrayerRequestsList.as_view(), name="my-requests"),
    path("my/prayers/", MyPrayersList.as_view(), name="my-prayers"),
    path("<uuid:id>/", PrayerRequestDetail.as_view(), name="detail"),
    path("<uuid:id>/update/", PrayerRequestUpdate.as_view(), name="update"),
    path("<uuid:id>/delete/", PrayerRequestDelete.as_view(), name="delete"),
    path("<uuid:id>/approve/", PrayerRequestApprove.as_view(), name="approve"),
    path("<uuid:id>/prayers/", PrayerList.as_view(), name="prayer-list"),
    path("<uuid:id>/pray/", PrayerCreate.as_view(), name="pray"),
    path("prayers/<uuid:id>/", PrayerDelete.as_view(), name="prayer-delete"),
]
