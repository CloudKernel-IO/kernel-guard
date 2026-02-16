"""Tests unitarios para main.py"""
import pytest
import sys
from unittest.mock import patch, MagicMock
from main import classify_severity, main


class TestClassifySeverity:
    """Tests para la función classify_severity"""
    
    def test_critical_severity_with_emoji(self):
        """Debe clasificar como HIGH cuando contiene 🚨"""
        result = classify_severity("🚨 CRITICAL: Public Access")
        assert result == "HIGH"
    
    def test_critical_severity_with_text(self):
        """Debe clasificar como HIGH cuando contiene CRITICAL"""
        result = classify_severity("CRITICAL: Security Issue")
        assert result == "HIGH"
    
    def test_medium_severity_with_emoji(self):
        """Debe clasificar como MEDIUM cuando contiene ⚠️"""
        result = classify_severity("⚠️ RISK: Old Keys")
        assert result == "MEDIUM"
    
    def test_medium_severity_with_text(self):
        """Debe clasificar como MEDIUM cuando contiene RISK"""
        result = classify_severity("RISK: Unencrypted Data")
        assert result == "MEDIUM"
    
    def test_low_severity_with_emoji(self):
        """Debe clasificar como LOW cuando contiene 💰"""
        result = classify_severity("💰 ORPHAN: Unused Disk")
        assert result == "LOW"
    
    def test_low_severity_with_text(self):
        """Debe clasificar como LOW cuando contiene ORPHAN"""
        result = classify_severity("ORPHAN: Charging")
        assert result == "LOW"
    
    def test_info_severity_default(self):
        """Debe clasificar como INFO cuando no coincide ningún patrón"""
        result = classify_severity("✅ OK")
        assert result == "INFO"


class TestMain:
    """Tests para la función main"""
    
    @patch('main.AzureProvider')
    @patch('sys.argv', ['main.py', '--cloud', 'azure', '--target', 'rg-test'])
    def test_azure_scan_without_report(self, mock_azure_provider, capsys):
        """Debe ejecutar scan de Azure sin generar reporte"""
        # Setup
        provider_instance = MagicMock()
        provider_instance.scan.return_value = [
            ["vm-01", "VirtualMachine", "✅ OK"],
            ["storage-01", "Storage", "🚨 CRITICAL: Public"]
        ]
        mock_azure_provider.return_value = provider_instance
        
        # Execute
        main()
        
        # Verify
        provider_instance.scan.assert_called_once_with('rg-test')
        captured = capsys.readouterr()
        assert "🚀 Iniciando auditoría Kernel-Guard en AZURE" in captured.out
        assert "vm-01" in captured.out
    
    @patch('main.Reporter.generate_html')
    @patch('main.AWSProvider')
    @patch('sys.argv', ['main.py', '--cloud', 'aws', '--target', 'us-east-1', '--report'])
    def test_aws_scan_with_report(self, mock_aws_provider, mock_reporter):
        """Debe ejecutar scan de AWS y generar reporte HTML"""
        # Setup
        provider_instance = MagicMock()
        provider_instance.scan.return_value = [
            ["bucket-1", "S3", "🚨 CRITICAL: Public Access"]
        ]
        mock_aws_provider.return_value = provider_instance
        
        # Execute
        main()
        
        # Verify
        provider_instance.scan.assert_called_once_with('us-east-1')
        mock_reporter.assert_called_once()
        call_args = mock_reporter.call_args[0]
        assert call_args[1] == 'aws'  # cloud_name
        assert len(call_args[0]) == 1  # results
        assert call_args[0][0][3] == "HIGH"  # severity
    
    @patch('main.GCPProvider')
    @patch('sys.argv', ['main.py', '--cloud', 'gcp', '--target', 'my-project'])
    def test_gcp_scan_success(self, mock_gcp_provider, capsys):
        """Debe ejecutar scan de GCP exitosamente"""
        # Setup
        provider_instance = MagicMock()
        provider_instance.scan.return_value = [
            ["disk-1", "Disk", "💰 ORPHAN: Unused Disk"]
        ]
        mock_gcp_provider.return_value = provider_instance
        
        # Execute
        main()
        
        # Verify
        provider_instance.scan.assert_called_once_with('my-project')
        captured = capsys.readouterr()
        assert "GCP" in captured.out
    
    @patch('main.AzureProvider')
    @patch('sys.argv', ['main.py', '--cloud', 'azure', '--target', 'rg-test'])
    def test_scan_error_handling(self, mock_azure_provider, capsys):
        """Debe manejar errores durante el scan"""
        # Setup
        provider_instance = MagicMock()
        provider_instance.scan.side_effect = Exception("Connection failed")
        mock_azure_provider.return_value = provider_instance
        
        # Execute & Verify
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "❌ Error crítico durante el escaneo" in captured.out
    
    @patch('sys.argv', ['main.py', '--cloud', 'azure'])
    def test_missing_target_argument(self, capsys):
        """Debe fallar si falta el argumento --target"""
        with pytest.raises(SystemExit):
            main()
    
    def test_severity_classification_in_results(self):
        """Debe clasificar correctamente la severidad en todos los resultados"""
        raw_results = [
            ["res1", "Type1", "🚨 CRITICAL: Alert"],
            ["res2", "Type2", "⚠️ RISK: Warning"],
            ["res3", "Type3", "💰 ORPHAN: Cost"],
            ["res4", "Type4", "✅ OK"]
        ]
        
        final_results = []
        for r in raw_results:
            severity = classify_severity(r[2])
            final_results.append([r[0], r[1], r[2], severity])
        
        assert final_results[0][3] == "HIGH"
        assert final_results[1][3] == "MEDIUM"
        assert final_results[2][3] == "LOW"
        assert final_results[3][3] == "INFO"
