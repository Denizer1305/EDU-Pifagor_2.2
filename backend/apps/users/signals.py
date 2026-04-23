from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import (
    ParentProfile,
    Profile,
    StudentProfile,
    TeacherProfile,
    User,
)


@receiver(post_save, sender=User)
def ensure_user_profiles(sender, instance: User, created: bool, **kwargs):
    """
    Создаёт обязательные профили пользователя.

    Логика:
    - у каждого пользователя должен быть базовый Profile;
    - в зависимости от registration_type создаётся role-profile;
    - роли здесь не назначаются, так как это часть service-логики и
      может зависеть от верификации.
    """
    Profile.objects.get_or_create(user=instance)

    if instance.registration_type == User.RegistrationTypeChoices.STUDENT:
        StudentProfile.objects.get_or_create(user=instance)

    elif instance.registration_type == User.RegistrationTypeChoices.PARENT:
        ParentProfile.objects.get_or_create(user=instance)

    elif instance.registration_type == User.RegistrationTypeChoices.TEACHER:
        TeacherProfile.objects.get_or_create(user=instance)
