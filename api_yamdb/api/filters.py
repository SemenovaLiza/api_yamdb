import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name')
    genre = django_filters.CharFilter(field_name='genre')
    category = django_filters.CharFilter(field_name='category')
    year = django_filters.NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = '__all__'
