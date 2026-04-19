import django_filters

from apps.users.models import Profile, TeacherProfile, User


class UserFilter(django_filters.FilterSet):
    """
    Фильтрация для модели User
    """

    email = django_filters.CharFilter(
        field_name="email",
        lookup_expr="icontains"
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active"
    )
    is_email_verified = django_filters.BooleanFilter(
        field_name="is_email_verified"
    )
    created_at = django_filters.DateFromToRangeFilter(
        field_name="created_at"
    )

    class Meta:
        model = User
        fields = (
            'email', 'is_active',
            'is_email_verified', 'created_at',
        )


class ProfileFilter(django_filters.FilterSet):
    """Фильтр для profile."""
    first_name = django_filters.CharFilter(
        field_name="first_name",
        lookup_expr="icontains"
    )
    last_name = django_filters.CharFilter(
        field_name="last_name",
        lookup_expr="icontains"
    )
    city = django_filters.CharFilter(
        field_name="city",
        lookup_expr="icontains"
    )

    class Meta:
        model = Profile
        fields = (
            'first_name', 'last_name',
            'city',
        )


class TeacherProfileFilter(django_filters.FilterSet):
    """Фильтр для teacher profile."""
    is_public = django_filters.BooleanFilter(
        field_name="is_public",
    )
    show_on_teacher_page = django_filters.BooleanFilter(
        field_name="show_on_teacher_page",
    )
    experience_year = django_filters.RangeFilter(
        field_name="experience_year",
    )

    class Meta:
        model = TeacherProfile
        fields = (
            'is_public', 'show_on_teacher_page',
            'experience_year',
        )
