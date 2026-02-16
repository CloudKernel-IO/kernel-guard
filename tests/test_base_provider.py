"""Tests para la clase base CloudProvider"""
import pytest
from core.base_provider import CloudProvider


class TestCloudProvider:
    """Tests para la clase base CloudProvider"""
    
    def test_is_abstract_class(self):
        """CloudProvider debe ser una clase base abstracta"""
        # Intentar instanciar directamente debe estar permitido pero scan debe ser implementado
        provider = CloudProvider()
        assert isinstance(provider, CloudProvider)
    
    def test_scan_method_exists(self):
        """Debe tener el método scan definido"""
        provider = CloudProvider()
        assert hasattr(provider, 'scan')
    
    def test_scan_raises_not_implemented(self):
        """El método scan debe lanzar NotImplementedError si no se implementa"""
        provider = CloudProvider()
        
        with pytest.raises(NotImplementedError):
            provider.scan("test-target")
    
    def test_subclass_must_implement_scan(self):
        """Las subclases deben implementar el método scan"""
        
        class IncompleteProvider(CloudProvider):
            pass
        
        provider = IncompleteProvider()
        
        with pytest.raises(NotImplementedError):
            provider.scan("test")
    
    def test_subclass_with_scan_implementation(self):
        """Las subclases que implementan scan deben funcionar correctamente"""
        
        class CompleteProvider(CloudProvider):
            def scan(self, target: str):
                return [["resource-1", "type-1", "status-1"]]
        
        provider = CompleteProvider()
        results = provider.scan("test-target")
        
        assert len(results) == 1
        assert results[0][0] == "resource-1"
    
    def test_scan_signature_accepts_string(self):
        """El método scan debe aceptar un string como target"""
        
        class TestProvider(CloudProvider):
            def scan(self, target: str):
                assert isinstance(target, str)
                return []
        
        provider = TestProvider()
        provider.scan("my-target")
