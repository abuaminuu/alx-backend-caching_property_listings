# properties/models.py
from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class Property(models.Model):
    PROPERTY_TYPES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('condo', 'Condominium'),
        ('townhouse', 'Townhouse'),
        ('villa', 'Villa'),
        ('cottage', 'Cottage'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('pending', 'Pending'),
        ('rented', 'Rented'),
    ]
    
    # Core fields
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Price in USD"
    )
    location = models.CharField(max_length=100)
    
    # Additional useful fields
    property_type = models.CharField(
        max_length=20, 
        choices=PROPERTY_TYPES, 
        default='house'
    )
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=1.0
    )
    square_feet = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Total square footage"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available'
    )
    
    # Boolean features
    has_garage = models.BooleanField(default=False)
    has_pool = models.BooleanField(default=False)
    has_garden = models.BooleanField(default=False)
    is_furnished = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    listed_date = models.DateTimeField(default=timezone.now)
    
    # For image handling (you'll need Pillow installed)
    # main_image = models.ImageField(upload_to='properties/', null=True, blank=True)
    
    # Unique identifier
    reference_number = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False
    )
    
    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['location']),
            models.Index(fields=['status']),
            models.Index(fields=['property_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.location} (${self.price})"
    
    def save(self, *args, **kwargs):
        # Generate reference number if not set
        if not self.reference_number:
            self.reference_number = self._generate_reference_number()
        
        # Ensure price is positive
        if self.price < Decimal('0'):
            self.price = Decimal('0')
        
        super().save(*args, **kwargs)
    
    def _generate_reference_number(self):
        """Generate a unique reference number"""
        import uuid
        prefix = "PROP"
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"{prefix}-{unique_id}"
    
    @property
    def price_per_sqft(self):
        """Calculate price per square foot if square footage is available"""
        if self.square_feet and self.square_feet > 0:
            return self.price / self.square_feet
        return None
    
    @property
    def is_available(self):
        """Check if property is available"""
        return self.status == 'available'
    
    @property
    def short_description(self):
        """Return truncated description"""
        if len(self.description) > 100:
            return self.description[:100] + "..."
        return self.description
    def save(self, *args, **kwargs):
        """
        Override save method to add custom logic.
        Note: Signals will still fire automatically.
        """
        is_new = self.pk is None
        
        # Add any pre-save logic here
        if is_new:
            logger.info(f"Creating new property: {self.title}")
        else:
            logger.info(f"Updating property {self.id}: {self.title}")
        
        # Call parent save
        super().save(*args, **kwargs)
        
        # Post-save logic (optional)
        # Signals will handle cache invalidation
        
    def delete(self, *args, **kwargs):
        """
        Override delete method to add custom logic.
        Note: Signals will still fire automatically.
        """
        logger.info(f"Deleting property {self.id}: {self.title}")
        
        # Call parent delete
        super().delete(*args, **kwargs)
    
    @classmethod
    def bulk_create_with_cache_invalidation(cls, objects, batch_size=None):
        """
        Custom bulk_create method that handles cache invalidation.
        
        Args:
            objects: List of Property instances
            batch_size: Batch size for creation
            
        Returns:
            List of created instances
        """
        logger.info(f"Bulk creating {len(objects)} properties")
        
        # Clear cache before bulk operation
        cache.delete('all_properties')
        
        # Perform bulk create
        created = super().bulk_create(objects, batch_size=batch_size)
        
        logger.info(f"Bulk created {len(created)} properties, cache invalidated")
        return created
        
