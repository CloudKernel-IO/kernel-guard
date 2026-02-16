"""Tests de integración end-to-end"""
import pytest
from unittest.mock import patch, MagicMock, Mock
import sys
from io import StringIO
from main import main


class TestIntegrationAzure:
    """Tests de integración completos para Azure"""
    
    @patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'})
    @patch('main.Reporter.generate_html')
    @patch('providers.azure_provider.DefaultAzureCredential')
    @patch('providers.azure_provider.ComputeManagementClient')
    @patch('providers.azure_provider.SqlManagementClient')
    @patch('providers.azure_provider.StorageManagementClient')
    @patch('providers.azure_provider.NetworkManagementClient')
    @patch('sys.argv', ['main.py', '--cloud', 'azure', '--target', 'rg-production', '--report'])
    def test_full_azure_scan_with_report(
        self, mock_net, mock_storage, mock_sql, mock_compute, 
        mock_cred, mock_reporter, capsys
    ):
        """Test de integración completo: scan Azure + generación de reporte"""
        # Setup - Simular entorno Azure completo
        
        # Disco huérfano
        orphan_disk = Mock()
        orphan_disk.name = "disk-orphan-001"
        orphan_disk.managed_by = None
        
        # SQL sin TDE
        sql_server = Mock()
        sql_server.name = "sql-prod-server"
        tde = Mock()
        tde.status = "Disabled"
        
        # Storage público
        storage_account = Mock()
        storage_account.name = "prodstorageacct"
        storage_account.allow_blob_public_access = True
        
        # NSG con puerto abierto
        nsg = Mock()
        nsg.name = "nsg-prod"
        rule = Mock()
        rule.access = "Allow"
        rule.source_address_prefix = "*"
        rule.destination_port_range = "3389"
        nsg.security_rules = [rule]
        
        # Configurar mocks
        mock_compute.return_value.disks.list_by_resource_group.return_value = [orphan_disk]
        mock_sql.return_value.servers.list_by_resource_group.return_value = [sql_server]
        mock_sql.return_value.transparent_data_encryptions.get.return_value = tde
        mock_storage.return_value.storage_accounts.list_by_resource_group.return_value = [storage_account]
        mock_net.return_value.network_security_groups.list.return_value = [nsg]
        
        # Execute
        main()
        
        # Verify
        captured = capsys.readouterr()
        
        # Verificar output
        assert "🚀 Iniciando auditoría Kernel-Guard en AZURE" in captured.out
        assert "disk-orphan-001" in captured.out
        assert "sql-prod-server" in captured.out
        assert "prodstorageacct" in captured.out
        assert "nsg-prod" in captured.out
        
        # Verificar que se generó el reporte
        mock_reporter.assert_called_once()
        results_arg = mock_reporter.call_args[0][0]
        assert len(results_arg) == 4  # 4 problemas detectados
        
        # Verificar severidades
        severities = [r[3] for r in results_arg]
        assert "HIGH" in severities  # SQL TDE, Storage público, NSG abierto


class TestIntegrationAWS:
    """Tests de integración completos para AWS"""
    
    @patch('main.Reporter.generate_html')
    @patch('providers.aws_provider.boto3.Session')
    @patch('sys.argv', ['main.py', '--cloud', 'aws', '--target', 'us-east-1', '--report'])
    def test_full_aws_scan_all_checks(self, mock_boto_session, mock_reporter, capsys):
        """Test de integración completo: todas las verificaciones de AWS"""
        # Setup
        from datetime import datetime, timezone
        
        # S3 público
        s3 = MagicMock()
        s3.list_buckets.return_value = {
            'Buckets': [
                {'Name': 'prod-public-bucket'},
                {'Name': 'prod-private-bucket'}
            ]
        }
        s3.get_public_access_block.side_effect = [
            {
                'PublicAccessBlockConfiguration': {
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            },
            Exception("No policy")
        ]
        
        # IAM con claves viejas
        iam = MagicMock()
        iam.list_users.return_value = {
            'Users': [{'UserName': 'legacy-user'}]
        }
        iam.list_access_keys.return_value = {
            'AccessKeyMetadata': [{
                'CreateDate': datetime(2022, 1, 1, tzinfo=timezone.utc)
            }]
        }
        
        # EC2: EIP orphan, SG abierto, volumen sin encriptar
        ec2 = MagicMock()
        ec2.describe_addresses.return_value = {
            'Addresses': [{'PublicIp': '54.123.45.67'}]
        }
        ec2.describe_security_groups.return_value = {
            'SecurityGroups': [{
                'GroupName': 'prod-sg',
                'IpPermissions': [{
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }]
            }]
        }
        ec2.describe_volumes.return_value = {
            'Volumes': [
                {'VolumeId': 'vol-unencrypted-123', 'Encrypted': False}
            ]
        }
        
        mock_boto_session.return_value.client.side_effect = lambda service: {
            's3': s3, 'iam': iam, 'ec2': ec2
        }[service]
        
        # Execute
        main()
        
        # Verify
        captured = capsys.readouterr()
        assert "AWS" in captured.out
        
        # Verificar llamada al reporter
        mock_reporter.assert_called_once()
        results = mock_reporter.call_args[0][0]
        
        # Debe haber detectado: 1 S3 público, 1 S3 sin policy, 1 IAM key vieja,
        # 1 EIP orphan, 1 SG abierto, 1 volumen sin encriptar = 6 problemas
        assert len(results) == 6
        
        # Verificar tipos de problemas
        problem_types = [r[1] for r in results]
        assert 'S3' in problem_types
        assert 'IAM Key' in problem_types
        assert 'EIP' in problem_types
        assert 'Security Group' in problem_types
        assert 'EBS Volume' in problem_types


class TestIntegrationGCP:
    """Tests de integración completos para GCP"""
    
    @patch('main.Reporter.generate_html')
    @patch('providers.gcp_provider.compute_v1.DisksClient')
    @patch('providers.gcp_provider.compute_v1.InstancesClient')
    @patch('sys.argv', ['main.py', '--cloud', 'gcp', '--target', 'my-prod-project', '--report'])
    def test_full_gcp_scan(self, mock_instances, mock_disks, mock_reporter, capsys):
        """Test de integración completo: scan GCP completo"""
        # Setup instances con IP pública
        instance = Mock()
        instance.name = "prod-vm-001"
        nic = Mock()
        access_config = Mock()
        access_config.nat_i_p = "35.123.45.67"
        nic.access_configs = [access_config]
        instance.network_interfaces = [nic]
        
        inst_response = Mock()
        inst_response.instances = [instance]
        mock_instances.return_value.aggregated_list.return_value = [
            ("us-central1-a", inst_response)
        ]
        
        # Setup disks: uno sin encriptar, uno huérfano
        disk1 = Mock()
        disk1.name = "disk-unencrypted"
        disk1.disk_encryption_key = None
        disk1.users = ["instance-1"]
        
        disk2 = Mock()
        disk2.name = "disk-orphan"
        disk2.disk_encryption_key = Mock()
        disk2.users = []
        
        disk_response = Mock()
        disk_response.disks = [disk1, disk2]
        mock_disks.return_value.aggregated_list.return_value = [
            ("us-central1-a", disk_response),
            ("us-central1-a", disk_response)
        ]
        
        # Execute
        main()
        
        # Verify
        captured = capsys.readouterr()
        assert "GCP" in captured.out
        
        mock_reporter.assert_called_once()
        results = mock_reporter.call_args[0][0]
        
        # Verificar problemas detectados
        assert len(results) >= 3  # VM con IP pública, disco sin encriptar, disco huérfano
        
        problems = [r[2] for r in results]
        assert any("Public IP" in p for p in problems)
        assert any("Not KMS Encrypted" in p for p in problems)
        assert any("ORPHAN" in p for p in problems)


class TestIntegrationErrorHandling:
    """Tests de integración para manejo de errores"""
    
    @patch('providers.azure_provider.DefaultAzureCredential')
    @patch('sys.argv', ['main.py', '--cloud', 'azure', '--target', 'rg-test'])
    def test_azure_authentication_failure(self, mock_cred, capsys):
        """Debe manejar fallo de autenticación en Azure"""
        mock_cred.side_effect = Exception("Authentication failed")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "❌ Error crítico durante el escaneo" in captured.out
    
    @patch('providers.aws_provider.boto3.Session')
    @patch('sys.argv', ['main.py', '--cloud', 'aws', '--target', 'us-west-2'])
    def test_aws_api_failure(self, mock_session, capsys):
        """Debe manejar fallos de API en AWS"""
        s3 = MagicMock()
        s3.list_buckets.side_effect = Exception("Access Denied")
        
        mock_session.return_value.client.return_value = s3
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1


class TestIntegrationOutputFormats:
    """Tests de integración para formatos de salida"""
    
    @patch('main.Reporter.generate_html')
    @patch('providers.azure_provider.DefaultAzureCredential')
    @patch('providers.azure_provider.ComputeManagementClient')
    @patch('providers.azure_provider.SqlManagementClient')
    @patch('providers.azure_provider.StorageManagementClient')
    @patch('providers.azure_provider.NetworkManagementClient')
    @patch('sys.argv', ['main.py', '--cloud', 'azure', '--target', 'rg-test'])
    @patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub'})
    def test_console_output_table_format(
        self, mock_net, mock_storage, mock_sql, mock_compute, 
        mock_cred, mock_reporter, capsys
    ):
        """Debe mostrar resultados en formato tabla en consola"""
        # Setup con datos mínimos
        mock_compute.return_value.disks.list_by_resource_group.return_value = []
        mock_sql.return_value.servers.list_by_resource_group.return_value = []
        mock_storage.return_value.storage_accounts.list_by_resource_group.return_value = []
        mock_net.return_value.network_security_groups.list.return_value = []
        
        main()
        
        captured = capsys.readouterr()
        
        # Verificar formato de tabla (tabulate genera bordes)
        assert "+" in captured.out or "|" in captured.out
        assert "Recurso" in captured.out
        assert "Tipo" in captured.out
        assert "Hallazgo" in captured.out
        assert "Severidad" in captured.out
