from django.urls import path

from apps.users.views import (
    ChangePasswordView,
    CurrentUserView,
    LoginView,
    LogoutView,
    MyChildrenListView,
    MyParentProfileView,
    MyProfileView,
    MyStudentProfileView,
    MyTeacherProfileView,
    ProfileDetailView,
    RegisterView,
    TeacherProfileDetailView,
    TeacherPublicListView,
    UserDetailView,
    UserListView,
)

app_name = "users"

urlpatterns = [
    # auth
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", CurrentUserView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),

    # users
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),

    # profiles
    path("profile/me/", MyProfileView.as_view(), name="my-profile"),
    path("profiles/<int:pk>/", ProfileDetailView.as_view(), name="profile-detail"),

    # teachers
    path("teachers/", TeacherPublicListView.as_view(), name="teacher-public-list"),
    path("teachers/<int:pk>/", TeacherProfileDetailView.as_view(), name="teacher-detail"),
    path("teachers/me/", MyTeacherProfileView.as_view(), name="my-teacher-profile"),

    # students
    path("students/me/", MyStudentProfileView.as_view(), name="my-student-profile"),

    # parents
    path("parents/me/", MyParentProfileView.as_view(), name="my-parent-profile"),
    path("parents/me/children/", MyChildrenListView.as_view(), name="my-children"),
]
