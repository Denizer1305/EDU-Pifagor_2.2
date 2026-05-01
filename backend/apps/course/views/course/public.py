from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.filters import CourseFilter
from apps.course.permissions import IsPublishedCourseVisible
from apps.course.selectors import (
    get_public_courses_queryset,
)
from apps.course.serializers import (
    CoursePublicDetailSerializer,
    CoursePublicListSerializer,
)
from apps.course.views.course.common import (
    apply_filterset,
    get_course_or_404,
)


class CoursePublicListAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        queryset = get_public_courses_queryset(
            search=request.query_params.get("q", ""),
            organization_id=request.query_params.get("organization_id"),
        )
        queryset = apply_filterset(CourseFilter, request, queryset)

        serializer = CoursePublicListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CoursePublicDetailAPIView(APIView):
    permission_classes = (AllowAny, IsPublishedCourseVisible)

    def get(self, request, pk: int, *args, **kwargs):
        course = get_course_or_404(course_id=pk)
        self.check_object_permissions(request, course)

        serializer = CoursePublicDetailSerializer(
            course,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
