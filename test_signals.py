# test_signals.py
import os
import sys
import django
import time
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_caching_property_listings.settings')
django.setup()

from properties.models import Property
from properties.utils import get_all_properties
from django.core.cache import cache
from decimal import Decimal

def test_cache_invalidation_signals():
    """
    Test that cache invalidation signals work correctly.
    """
    print("=" * 70)
    print("Testing Cache Invalidation Signals")
    print("=" * 70)
    
    # Clear cache before starting
    print("\n🗑️  Step 1: Clearing initial cache...")
    cache.delete('all_properties')
    print("   ✅ Cache cleared")
    
    # Step 2: Populate cache
    print("\n📝 Step 2: Populating cache...")
    properties = get_all_properties()
    print(f"   ✅ Retrieved {len(properties)} properties")
    print(f"   Cache populated: {cache.get('all_properties') is not None}")
    
    # Step 3: Create a new property (should invalidate cache)
    print("\n➕ Step 3: Creating new property...")
    new_property = Property.objects.create(
        title="Test Property - Signal Test",
        description="Testing cache invalidation signals",
        price=Decimal('250000'),
        location="Test City, TS",
        property_type="house",
        bedrooms=3,
        bathrooms=2.0,
    )
    print(f"   ✅ Created property: {new_property.title}")
    
    # Wait a moment for signals to process
    time.sleep(0.5)
    
    # Check if cache was invalidated
    print("\n🔍 Step 4: Checking cache after creation...")
    cached = cache.get('all_properties') is not None
    print(f"   Cache after creation: {'STILL CACHED' if cached else 'INVALIDATED'}")
    
    if cached:
        print("   ⚠️  Cache should have been invalidated by post_save signal")
    else:
        print("   ✅ Cache successfully invalidated by signal!")
    
    # Step 5: Update property
    print("\n✏️  Step 5: Updating property...")
    new_property.title = "Test Property - Updated"
    new_property.save()
    print(f"   ✅ Updated property title")
    
    time.sleep(0.5)
    
    print("\n🔍 Step 6: Checking cache after update...")
    cached = cache.get('all_properties') is not None
    print(f"   Cache after update: {'STILL CACHED' if cached else 'INVALIDATED'}")
    
    # Step 7: Delete property
    print("\n🗑️  Step 7: Deleting property...")
    property_id = new_property.id
    new_property.delete()
    print(f"   ✅ Deleted property ID: {property_id}")
    
    time.sleep(0.5)
    
    print("\n🔍 Step 8: Checking cache after deletion...")
    cached = cache.get('all_properties') is not None
    print(f"   Cache after deletion: {'STILL CACHED' if cached else 'INVALIDATED'}")
    
    # Step 9: Test cache statistics
    print("\n📊 Step 9: Checking cache invalidation statistics...")
    from properties.signals import get_cache_invalidation_stats
    stats = get_cache_invalidation_stats()
    
    print(f"   Total invalidations: {stats['total_invalidations']}")
    if stats['last_invalidation']:
        print(f"   Last invalidation:")
        print(f"     Property: {stats['last_invalidation']['property_title']}")
        print(f"     Action: {stats['last_invalidation']['action']}")
    
    print("\n" + "=" * 70)
    print("Signal Testing Complete!")
    print("=" * 70)
    
    # Summary
    print("\n📋 Summary:")
    print(f"   Properties in database: {Property.objects.count()}")
    print(f"   Cache populated: {cache.get('all_properties') is not None}")
    print(f"   Total cache invalidations recorded: {stats['total_invalidations']}")

def test_bulk_operations():
    """
    Test cache invalidation with bulk operations.
    """
    print("\n" + "=" * 70)
    print("Testing Bulk Operations with Cache Invalidation")
    print("=" * 70)
    
    # Clear cache
    cache.delete('all_properties')
    
    # Create multiple properties
    print("\n📝 Creating multiple properties...")
    properties_to_create = []
    
    for i in range(3):
        prop = Property(
            title=f"Bulk Test Property {i+1}",
            description=f"Testing bulk creation {i+1}",
            price=Decimal('100000') * (i + 1),
            location=f"Bulk City {i+1}",
            property_type="apartment",
            bedrooms=i + 1,
            bathrooms=float(i + 1),
        )
        properties_to_create.append(prop)
    
    # Use individual saves (each triggers signal)
    print("\n💾 Saving individually (each triggers signal)...")
    for prop in properties_to_create:
        prop.save()
    
    time.sleep(1)
    
    print(f"   Created {len(properties_to_create)} properties individually")
    print(f"   Cache after individual saves: {'INVALIDATED' if cache.get('all_properties') is None else 'CACHED'}")
    
    # Clean up
    print("\n🗑️  Cleaning up test properties...")
    Property.objects.filter(title__startswith="Bulk Test").delete()
    print("   ✅ Cleanup complete")

if __name__ == "__main__":
    test_cache_invalidation_signals()
    test_bulk_operations()
    