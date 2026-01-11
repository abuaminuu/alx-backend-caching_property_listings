# properties/views.py
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Property

class PropertyListView(ListView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 10
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        cache_key = 'properties_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        queryset = Property.objects.filter(status='available').order_by('-created_at')
        cache.set(cache_key, queryset, 60 * 5)  # Cache for 5 minutes
        return queryset

class PropertyDetailView(DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_object(self, queryset=None):
        property_id = self.kwargs.get('pk')
        cache_key = f'property_{property_id}'
        cached_property = cache.get(cache_key)
        
        if cached_property is not None:
            return cached_property
        
        property_obj = super().get_object(queryset)
        cache.set(cache_key, property_obj, 60 * 15)  # Cache for 15 minutes
        return property_obj
    