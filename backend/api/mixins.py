from __future__ import annotations


class SerializerByActionMixin:
    serializer_action_classes: dict[str, type] = {}

    def get_serializer_class(self):
        action = getattr(self, "action", None)
        if action and action in self.serializer_action_classes:
            return self.serializer_action_classes[action]
        return super().get_serializer_class()


class ActionPermissionMixin:
    permission_action_classes: dict[str, list[type]] = {}

    def get_permissions(self):
        action = getattr(self, "action", None)
        if action and action in self.permission_action_classes:
            permission_classes = self.permission_action_classes[action]
            return [permission() for permission in permission_classes]
        return super().get_permissions()
