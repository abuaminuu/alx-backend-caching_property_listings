from django.apps import AppConfig

class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'
    
    def ready(self):
        """
        Override ready() method to import signals when app is ready.
        This ensures signals are connected when Django starts.
        """
        # Import signals module
        import properties.signals
        
        # You can also connect custom signals here if needed
        self._setup_custom_signals()
        
        # Log that signals are loaded
        import logging
        logger = logging.getLogger(__name__)
        logger.info("✅ Properties app signals loaded successfully")
    
    def _setup_custom_signals(self):
        """
        Setup any custom signals for the properties app.
        This is optional but can be useful for custom signal handling.
        """
        pass
