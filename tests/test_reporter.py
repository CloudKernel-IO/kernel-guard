"""Tests unitarios para core/reporter.py"""
import pytest
import os
from unittest.mock import patch, mock_open
from freezegun import freeze_time
from core.reporter import Reporter


class TestReporter:
    """Tests para la clase Reporter"""
    
    @freeze_time("2026-02-16 14:30:00")
    def test_generate_html_creates_file(self, sample_results, tmp_path):
        """Debe crear archivo HTML con nombre correcto"""
        with patch('builtins.open', mock_open()) as mocked_file:
            Reporter.generate_html(sample_results, "azure")
            
            # Verificar que se llamó open con el nombre correcto
            mocked_file.assert_called_once_with(
                "report_azure_20260216.html", "w"
            )
    
    @freeze_time("2026-02-16 14:30:00")
    def test_generate_html_content_structure(self, sample_results):
        """Debe generar HTML con estructura correcta"""
        m = mock_open()
        with patch('builtins.open', m):
            Reporter.generate_html(sample_results, "aws")
            
            # Obtener el contenido escrito
            handle = m()
            written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
            
            # Verificar elementos clave del HTML
            assert "<html>" in written_content
            assert "<head>" in written_content
            assert "<style>" in written_content
            assert "CloudKernel | Audit Report" in written_content
            assert "AWS" in written_content
            assert "2026-02-16 14:30" in written_content
            assert "</html>" in written_content
    
    @freeze_time("2026-02-16 14:30:00")
    def test_generate_html_includes_all_results(self, sample_results):
        """Debe incluir todos los resultados en el HTML"""
        m = mock_open()
        with patch('builtins.open', m):
            Reporter.generate_html(sample_results, "gcp")
            
            handle = m()
            written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
            
            # Verificar que todos los recursos están presentes
            assert "resource-1" in written_content
            assert "resource-2" in written_content
            assert "resource-3" in written_content
            assert "resource-4" in written_content
            
            # Verificar tipos
            assert "Type1" in written_content
            assert "Type2" in written_content
    
    @freeze_time("2026-02-16 14:30:00")
    def test_generate_html_css_classes(self, sample_results):
        """Debe aplicar clases CSS correctas según el estado"""
        m = mock_open()
        with patch('builtins.open', m):
            Reporter.generate_html(sample_results, "azure")
            
            handle = m()
            written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
            
            # Verificar clases CSS
            assert ".OK" in written_content
            assert ".DRIFT" in written_content
            assert "color: #10b981" in written_content  # Verde para OK
            assert "color: #ef4444" in written_content  # Rojo para DRIFT/ERROR
    
    @freeze_time("2026-02-16 14:30:00")
    def test_generate_html_prints_confirmation(self, sample_results, capsys):
        """Debe imprimir mensaje de confirmación"""
        m = mock_open()
        with patch('builtins.open', m):
            Reporter.generate_html(sample_results, "azure")
            
            captured = capsys.readouterr()
            assert "✅ Informe profesional generado" in captured.out
            assert "report_azure_20260216.html" in captured.out
    
    def test_generate_html_different_clouds(self):
        """Debe generar reportes para diferentes clouds"""
        results = [["test", "type", "OK", "INFO"]]
        
        clouds = ["azure", "aws", "gcp"]
        for cloud in clouds:
            m = mock_open()
            with patch('builtins.open', m):
                Reporter.generate_html(results, cloud)
                
                handle = m()
                written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
                assert cloud.upper() in written_content
    
    @freeze_time("2026-02-16 14:30:00")
    def test_generate_html_empty_results(self):
        """Debe manejar lista vacía de resultados"""
        m = mock_open()
        with patch('builtins.open', m):
            Reporter.generate_html([], "azure")
            
            handle = m()
            written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
            
            # Debe generar HTML válido aunque esté vacío
            assert "<html>" in written_content
            assert "CloudKernel" in written_content
            assert "<tbody></tbody>" in written_content
    
    @freeze_time("2026-02-16 14:30:00")
    def test_generate_html_table_structure(self, sample_results):
        """Debe generar tabla HTML con headers correctos"""
        m = mock_open()
        with patch('builtins.open', m):
            Reporter.generate_html(sample_results, "azure")
            
            handle = m()
            written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
            
            # Verificar estructura de tabla
            assert "<table>" in written_content
            assert "<thead>" in written_content
            assert "<tbody>" in written_content
            assert "Recurso" in written_content
            assert "Tipo" in written_content
            assert "Estado" in written_content
            assert "<tr><td>" in written_content
