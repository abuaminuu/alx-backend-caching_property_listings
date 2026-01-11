# properties/signals.py
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from django.db import transaction
import logging
from .models import Property

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Property)
def invalidate_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalidate cache when a Property is saved (created or updated).
    
    Args:
        sender: The model class (Property)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional arguments
    """
    # Use transaction.on_commit to ensure cache is cleared after successful save
    transaction.on_commit(
        lambda: _clear_property_cache(instance, created)
    )

@receiver(post_delete, sender=Property)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate cache when a Property is deleted.
    
    Args:
        sender: The model class (Property)
        instance: The actual instance being deleted
        **kwargs: Additional arguments
    """
    # Use transaction.on_commit to ensure cache is cleared after successful deletion
    transaction.on_commit(
        lambda: _clear_property_cache(instance, is_delete=True)
    )

@receiver(m2m_changed, sender=Property.amenities.through)
def invalidate_cache_on_m2m_change(sender, instance, action, **kwargs):
    """
    Invalidate cache when ManyToMany relationships change.
    
    Args:
        sender: The intermediate model
        instance: The Property instance
        action: The action being performed (pre_add, post_add, pre_remove, post_remove, pre_clear, post_clear)
        **kwargs: Additional arguments
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        logger.info(f"Property amenities changed for {instance.id}, invalidating cache...")
        transaction.on_commit(
            lambda: _clear_property_cache(instance, is_m2m_change=True)
        )

def _clear_property_cache(instance, created=False, is_delete=False, is_m2m_change=False):
    """
    Clear all property-related cache entries.
    
    Args:
        instance: Property instance
        created: Whether this is a new property
        is_delete: Whether this is a deletion
        is_m2m_change: Whether this is a ManyToMany change
    """
    try:
        # Main cache key to delete
        main_cache_key = 'all_properties'
        
        # Additional cache keys to invalidate
        cache_keys_to_delete = [
            main_cache_key,
            f'{main_cache_key}_meta',
        ]
        
        # Add pattern-based cache keys
        cache_patterns = [
            'properties_location_*',
            'properties_price_*',
            'property_*',  # Individual property cache
        ]
        
        # Delete specific keys
        deleted_keys = []
        for key in cache_keys_to_delete:
            if cache.delete(key):
                deleted_keys.append(key)
                logger.info(f"Deleted cache key: {key}")
        
        # Delete pattern-based keys (Redis-specific)
        try:
            for pattern in cache_patterns:
                keys = cache.keys(pattern)
                if keys:
                    cache.delete_many(keys)
                    deleted_keys.extend(keys)
                    logger.info(f"Deleted {len(keys)} keys matching pattern: {pattern}")
        except AttributeError:
            # Some cache backends don't support pattern deletion
            logger.warning("Pattern-based cache deletion not supported by this backend")
        
        # Log the action
        action_type = "created" if created else "deleted" if is_delete else "updated"
        if is_m2m_change:
            action_type = "M2M relationship changed"
        
        logger.info(f"✅ Cache invalidated for property {instance.id} ({action_type})")
        logger.info(f"   Total cache keys deleted: {len(deleted_keys)}")
        
        # Store cache invalidation event for monitoring
        invalidation_event = {
            'property_id': instance.id,
            'property_title': instance.title,
            'action': action_type,
            'cache_keys_deleted': deleted_keys,
            'timestamp': instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None,
        }
        
        # Store last invalidation event (optional, for debugging)
        cache.set('last_cache_invalidation', invalidation_event, timeout=3600)
        
        # Increment invalidation counter
        invalidation_count = cache.get('cache_invalidation_count', 0)
        cache.set('cache_invalidation_count', invalidation_count + 1, timeout=None)
        
    except Exception as e:
        logger.error(f"❌ Failed to invalidate cache for property {instance.id}: {e}")


# Signal for bulk operations (if using queryset.update() or bulk_create)
@receiver(post_save, sender=Property)
def handle_bulk_operations(sender, **kwargs):
    """
    Handle cache invalidation for bulk operations.
    This is triggered for each instance in bulk operations.
    """
    # For bulk operations, we might want different behavior
    # Currently handled by the main post_save signal
    pass


# Additional utility functions for cache management
def get_cache_invalidation_stats():
    """
    Get statistics about cache invalidations.
    
    Returns:
        dict: Cache invalidation statistics
    """
    stats = {
        'total_invalidations': cache.get('cache_invalidation_count', 0),
        'last_invalidation': cache.get('last_cache_invalidation'),
        'current_cache_state': {
            'all_properties_cached': cache.get('all_properties') is not None,
            'all_properties_ttl': cache.ttl('all_properties') if cache.get('all_properties') else None,
        }
    }
    return stats


def clear_all_property_cache():
    """
    Clear all property-related cache entries.
    Useful for manual cache management.
    """
    logger.info("Manually clearing all property cache...")
    
    keys_to_delete = [
        'all_properties',
        'all_properties_meta',
    ]
    
    patterns_to_delete = [
        'properties_*',
        'property_*',
    ]
    
    deleted_count = 0
    
    # Delete specific keys
    for key in keys_to_delete:
        if cache.delete(key):
            deleted_count += 1
    
    # Delete pattern-based keys
    try:
        for pattern in patterns_to_delete:
            keys = cache.keys(pattern)
            if keys:
                cache.delete_many(keys)
                deleted_count += len(keys)
    except AttributeError:
        logger.warning("Pattern-based deletion not supported")
    
    logger.info(f"Cleared {deleted_count} cache entries")
    return deleted_count
