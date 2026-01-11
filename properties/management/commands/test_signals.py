# properties/management/commands/test_signals.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from properties.models import Property
from properties.utils import get_all_properties
from decimal import Decimal
import time

class Command(BaseCommand):
    help = 'Test cache invalidation signals'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['test', 'stats', 'clear'],
            default='test',
            help='Action to perform'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'test':
            self._run_signal_tests()
        elif action == 'stats':
            self._show_stats()
        elif action == 'clear':
            self._clear_all()
    
    def _run_signal_tests(self):
        """Run signal tests"""
        self.stdout.write("=" * 60)
        self.stdout.write("Testing Cache Invalidation Signals")
        self.stdout.write("=" * 60)
        
        # Clear cache
        cache.delete('all_properties')
        
        # Test 1: Cache population
        self.stdout.write("\n1. Populating cache...")
        properties = get_all_properties()
        self.stdout.write(f"   Retrieved {len(properties)} properties")
        
        # Test 2: Create property
        self.stdout.write("\n2. Creating test property...")
        test_prop = Property.objects.create(
            title="Signal Test Property",
            description="Testing cache invalidation",
            price=Decimal('350000'),
            location="Testville",
            property_type="house",
        )
        self.stdout.write(f"   Created: {test_prop.title}")
        
        time.sleep(0.5)
        
        # Check cache
        cached = cache.get('all_properties')
        self.stdout.write(f"   Cache after create: {'INVALIDATED' if cached is None else 'STILL CACHED'}")
        
        if cached is None:
            self.stdout.write(self.style.SUCCESS("   ✅ Signal worked - cache invalidated"))
        else:
            self.stdout.write(self.style.WARNING("   ⚠️  Signal may not have worked"))
        
        # Test 3: Update property
        self.stdout.write("\n3. Updating property...")
        test_prop.title = "Signal Test Property - UPDATED"
        test_prop.save()
        
        time.sleep(0.5)
        
        cached = cache.get('all_properties')
        self.stdout.write(f"   Cache after update: {'INVALIDATED' if cached is None else 'STILL CACHED'}")
        
        # Test 4: Delete property
        self.stdout.write("\n4. Deleting property...")
        test_prop.delete()
        
        time.sleep(0.5)
        
        cached = cache.get('all_properties')
        self.stdout.write(f"   Cache after delete: {'INVALIDATED' if cached is None else 'STILL CACHED'}")
        
        # Cleanup
        Property.objects.filter(title__contains="Signal Test").delete()
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("Signal tests completed!"))
    
    def _show_stats(self):
        """Show cache invalidation statistics"""
        from properties.signals import get_cache_invalidation_stats
        
        stats = get_cache_invalidation_stats()
        
        self.stdout.write("Cache Invalidation Statistics:")
        self.stdout.write("=" * 60)
        
        self.stdout.write(f"Total Invalidations: {stats['total_invalidations']}")
        
        if stats['last_invalidation']:
            self.stdout.write("\nLast Invalidation:")
            for key, value in stats['last_invalidation'].items():
                self.stdout.write(f"  {key}: {value}")
        
        self.stdout.write(f"\nCurrent Cache State:")
        self.stdout.write(f"  all_properties cached: {stats['current_cache_state']['all_properties_cached']}")
        self.stdout.write(f"  TTL remaining: {stats['current_cache_state']['all_properties_ttl'] or 'N/A'} seconds")
    
    def _clear_all(self):
        """Clear all test data"""
        # Delete test properties
        deleted, _ = Property.objects.filter(title__contains="Test").delete()
        self.stdout.write(f"Deleted {deleted} test properties")
        
        # Clear cache
        cache.delete('all_properties')
        self.stdout.write("Cleared cache")
        