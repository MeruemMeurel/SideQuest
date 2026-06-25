from datetime import datetime, time

import django_filters
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from .models import Post


class PostFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(field_name="author_id")
    created_after = django_filters.CharFilter(method="filter_created_after")
    created_before = django_filters.CharFilter(method="filter_created_before")

    class Meta:
        model = Post
        fields = (
            "author",
            "created_after",
            "created_before",
        )

    def filter_created_after(self, queryset, name, value):
        parsed_value = self.parse_datetime_or_date(value, time.min)
        if parsed_value is None:
            return queryset.none()

        return queryset.filter(created_at__gte=parsed_value)

    def filter_created_before(self, queryset, name, value):
        parsed_value = self.parse_datetime_or_date(value, time.max)
        if parsed_value is None:
            return queryset.none()

        return queryset.filter(created_at__lte=parsed_value)

    def parse_datetime_or_date(self, value, date_time):
        parsed_datetime = parse_datetime(value)
        if parsed_datetime is not None:
            if timezone.is_naive(parsed_datetime):
                return timezone.make_aware(parsed_datetime)

            return parsed_datetime

        parsed_date = parse_date(value)
        if parsed_date is None:
            return None

        return timezone.make_aware(datetime.combine(parsed_date, date_time))
