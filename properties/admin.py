# properties/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 
        'title', 
        'location', 
        'price_display',
        'property_type',
        'status_display',
        'created_at_short',
        'is_available'
    ]
    
    list_filter = [
        'property_type',
        'status',
        'location',
        'has_garage',
        'has_pool',
        'is_furnished',
        'created_at',
    ]
    
    search_fields = [
        'title',
        'description',
        'location',
        'reference_number',
    ]
    
    readonly_fields = [
        'reference_number',
        'created_at',
        'updated_at',
        'price_per_sqft_display',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'reference_number')
        }),
        ('Price & Location', {
            'fields': ('price', 'location')
        }),
        ('Property Details', {
            'fields': ('property_type', 'bedrooms', 'bathrooms', 'square_feet')
        }),
        ('Features', {
            'fields': ('has_garage', 'has_pool', 'has_garden', 'is_furnished'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'listed_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'price_per_sqft_display'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        """Display price with dollar sign"""
        return f"${obj.price:,.2f}"
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'
    
    def status_display(self, obj):
        """Color-coded status display"""
        color_map = {
            'available': 'green',
            'sold': 'red',
            'pending': 'orange',
            'rented': 'blue',
        }
        color = color_map.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def created_at_short(self, obj):
        """Display short date format"""
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_short.short_description = 'Created'
    created_at_short.admin_order_field = 'created_at'
    
    def price_per_sqft_display(self, obj):
        """Display price per square foot if available"""
        price_per_sqft = obj.price_per_sqft
        if price_per_sqft:
            return f"${price_per_sqft:,.2f}/sqft"
        return "N/A"
    price_per_sqft_display.short_description = 'Price per SqFt'
