"""Tests unitarios para todos los providers"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timezone
from providers.azure_provider import AzureProvider
from providers.aws_provider import AWSProvider
from providers.gcp_provider import GCPProvider


class TestAzureProvider:
    """Tests para AzureProvider"""
    
    @patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'})
    @patch('providers.azure_provider.ComputeManagementClient')
    @patch('providers.azure_provider.SqlManagementClient')
    @patch('providers.azure_provider.StorageManagementClient')
    @patch('providers.azure_provider.NetworkManagementClient')
    @patch('providers.azure_provider.DefaultAzureCredential')
    def test_scan_orphan_disks(self, mock_cred, mock_net, mock_storage, mock_sql, mock_compute):
        """Debe detectar discos huérfanos (no managed)"""
        # Setup
        disk1 = Mock()
        disk1.name = "disk-orphan"
        disk1.managed_by = None
        
        disk2 = Mock()
        disk2.name = "disk-managed"
        disk2.managed_by = "vm-instance"
        
        mock_compute.return_value.disks.list_by_resource_group.return_value = [disk1, disk2]
        mock_sql.return_value.servers.list_by_resource_group.return_value = []
        mock_storage.return_value.storage_accounts.list_by_resource_group.return_value = []
        mock_net.return_value.network_security_groups.list.return_value = []
        
        provider = AzureProvider()
        results = provider.scan("rg-test")
        
        # Verify
        orphan_results = [r for r in results if "ORPHAN" in r[2] or "DRIFT" in r[2]]
        assert len(orphan_results) == 1
        assert orphan_results[0][0] == "disk-orphan"
    
    @patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'})
    @patch('providers.azure_provider.ComputeManagementClient')
    @patch('providers.azure_provider.SqlManagementClient')
    @patch('providers.azure_provider.StorageManagementClient')
    @patch('providers.azure_provider.NetworkManagementClient')
    @patch('providers.azure_provider.DefaultAzureCredential')
    def test_scan_sql_tde_disabled(self, mock_cred, mock_net, mock_storage, mock_sql, mock_compute):
        """Debe detectar SQL Server sin TDE habilitado"""
        # Setup
        server = Mock()
        server.name = "sql-server-test"
        
        tde = Mock()
        tde.status = "Disabled"
        
        mock_compute.return_value.disks.list_by_resource_group.return_value = []
        mock_sql.return_value.servers.list_by_resource_group.return_value = [server]
        mock_sql.return_value.transparent_data_encryptions.get.return_value = tde
        mock_storage.return_value.storage_accounts.list_by_resource_group.return_value = []
        mock_net.return_value.network_security_groups.list.return_value = []
        
        provider = AzureProvider()
        results = provider.scan("rg-test")
        
        # Verify
        tde_results = [r for r in results if "TDE" in r[2]]
        assert len(tde_results) == 1
        assert "CRITICAL" in tde_results[0][2]
    
    @patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'})
    @patch('providers.azure_provider.ComputeManagementClient')
    @patch('providers.azure_provider.SqlManagementClient')
    @patch('providers.azure_provider.StorageManagementClient')
    @patch('providers.azure_provider.NetworkManagementClient')
    @patch('providers.azure_provider.DefaultAzureCredential')
    def test_scan_storage_public_access(self, mock_cred, mock_net, mock_storage, mock_sql, mock_compute):
        """Debe detectar Storage Accounts con acceso público"""
        # Setup
        account = Mock()
        account.name = "storageaccount"
        account.allow_blob_public_access = True
        
        mock_compute.return_value.disks.list_by_resource_group.return_value = []
        mock_sql.return_value.servers.list_by_resource_group.return_value = []
        mock_storage.return_value.storage_accounts.list_by_resource_group.return_value = [account]
        mock_net.return_value.network_security_groups.list.return_value = []
        
        provider = AzureProvider()
        results = provider.scan("rg-test")
        
        # Verify
        storage_results = [r for r in results if "Storage" in r[1]]
        assert len(storage_results) == 1
        assert "Public Access" in storage_results[0][2]
    
    @patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'})
    @patch('providers.azure_provider.ComputeManagementClient')
    @patch('providers.azure_provider.SqlManagementClient')
    @patch('providers.azure_provider.StorageManagementClient')
    @patch('providers.azure_provider.NetworkManagementClient')
    @patch('providers.azure_provider.DefaultAzureCredential')
    def test_scan_nsg_open_admin_ports(self, mock_cred, mock_net, mock_storage, mock_sql, mock_compute):
        """Debe detectar NSG con puertos admin abiertos"""
        # Setup
        nsg = Mock()
        nsg.name = "nsg-test"
        
        rule = Mock()
        rule.access = "Allow"
        rule.source_address_prefix = "*"
        rule.destination_port_range = "22"
        
        nsg.security_rules = [rule]
        
        mock_compute.return_value.disks.list_by_resource_group.return_value = []
        mock_sql.return_value.servers.list_by_resource_group.return_value = []
        mock_storage.return_value.storage_accounts.list_by_resource_group.return_value = []
        mock_net.return_value.network_security_groups.list.return_value = [nsg]
        
        provider = AzureProvider()
        results = provider.scan("rg-test")
        
        # Verify
        nsg_results = [r for r in results if "NSG" in r[1]]
        assert len(nsg_results) == 1
        assert "Open Admin Port" in nsg_results[0][2]


class TestAWSProvider:
    """Tests para AWSProvider"""
    
    @patch('providers.aws_provider.boto3.Session')
    def test_scan_public_s3_bucket(self, mock_session):
        """Debe detectar buckets S3 con acceso público"""
        # Setup
        s3 = MagicMock()
        s3.list_buckets.return_value = {'Buckets': [{'Name': 'test-bucket'}]}
        s3.get_public_access_block.return_value = {
            'PublicAccessBlockConfiguration': {
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        }
        
        iam = MagicMock()
        iam.list_users.return_value = {'Users': []}
        
        ec2 = MagicMock()
        ec2.describe_addresses.return_value = {'Addresses': []}
        ec2.describe_security_groups.return_value = {'SecurityGroups': []}
        ec2.describe_volumes.return_value = {'Volumes': []}
        
        mock_session.return_value.client.side_effect = lambda service: {
            's3': s3, 'iam': iam, 'ec2': ec2
        }[service]
        
        provider = AWSProvider()
        results = provider.scan("us-east-1")
        
        # Verify
        s3_results = [r for r in results if r[1] == "S3"]
        assert len(s3_results) == 1
        assert "Public Access" in s3_results[0][2]
    
    @patch('providers.aws_provider.boto3.Session')
    def test_scan_old_access_keys(self, mock_session):
        """Debe detectar claves de acceso antiguas (> 90 días)"""
        # Setup
        s3 = MagicMock()
        s3.list_buckets.return_value = {'Buckets': []}
        
        iam = MagicMock()
        iam.list_users.return_value = {'Users': [{'UserName': 'old-user'}]}
        iam.list_access_keys.return_value = {
            'AccessKeyMetadata': [{
                'CreateDate': datetime(2023, 1, 1, tzinfo=timezone.utc)
            }]
        }
        
        ec2 = MagicMock()
        ec2.describe_addresses.return_value = {'Addresses': []}
        ec2.describe_security_groups.return_value = {'SecurityGroups': []}
        ec2.describe_volumes.return_value = {'Volumes': []}
        
        mock_session.return_value.client.side_effect = lambda service: {
            's3': s3, 'iam': iam, 'ec2': ec2
        }[service]
        
        provider = AWSProvider()
        results = provider.scan("us-east-1")
        
        # Verify
        iam_results = [r for r in results if "IAM Key" in r[1]]
        assert len(iam_results) == 1
        assert "days old" in iam_results[0][2]
    
    @patch('providers.aws_provider.boto3.Session')
    def test_scan_orphan_eips(self, mock_session):
        """Debe detectar EIPs sin instancia asociada"""
        # Setup
        s3 = MagicMock()
        s3.list_buckets.return_value = {'Buckets': []}
        
        iam = MagicMock()
        iam.list_users.return_value = {'Users': []}
        
        ec2 = MagicMock()
        ec2.describe_addresses.return_value = {
            'Addresses': [
                {'PublicIp': '1.2.3.4'},  # Sin InstanceId
                {'PublicIp': '5.6.7.8', 'InstanceId': 'i-123'}
            ]
        }
        ec2.describe_security_groups.return_value = {'SecurityGroups': []}
        ec2.describe_volumes.return_value = {'Volumes': []}
        
        mock_session.return_value.client.side_effect = lambda service: {
            's3': s3, 'iam': iam, 'ec2': ec2
        }[service]
        
        provider = AWSProvider()
        results = provider.scan("us-east-1")
        
        # Verify
        eip_results = [r for r in results if "EIP" in r[1]]
        assert len(eip_results) == 1
        assert "ORPHAN" in eip_results[0][2]
    
    @patch('providers.aws_provider.boto3.Session')
    def test_scan_unencrypted_volumes(self, mock_session):
        """Debe detectar volúmenes EBS sin encriptar"""
        # Setup
        s3 = MagicMock()
        s3.list_buckets.return_value = {'Buckets': []}
        
        iam = MagicMock()
        iam.list_users.return_value = {'Users': []}
        
        ec2 = MagicMock()
        ec2.describe_addresses.return_value = {'Addresses': []}
        ec2.describe_security_groups.return_value = {'SecurityGroups': []}
        ec2.describe_volumes.return_value = {
            'Volumes': [
                {'VolumeId': 'vol-123', 'Encrypted': False},
                {'VolumeId': 'vol-456', 'Encrypted': True}
            ]
        }
        
        mock_session.return_value.client.side_effect = lambda service: {
            's3': s3, 'iam': iam, 'ec2': ec2
        }[service]
        
        provider = AWSProvider()
        results = provider.scan("us-east-1")
        
        # Verify
        vol_results = [r for r in results if "EBS Volume" in r[1]]
        assert len(vol_results) == 1
        assert "Unencrypted" in vol_results[0][2]


class TestGCPProvider:
    """Tests para GCPProvider"""
    
    @patch('providers.gcp_provider.compute_v1.DisksClient')
    @patch('providers.gcp_provider.compute_v1.InstancesClient')
    def test_scan_instance_with_public_ip(self, mock_instances, mock_disks):
        """Debe detectar instancias con IP pública"""
        # Setup instances
        instance = Mock()
        instance.name = "instance-1"
        nic = Mock()
        access_config = Mock()
        access_config.nat_i_p = "34.56.78.90"
        nic.access_configs = [access_config]
        instance.network_interfaces = [nic]
        
        response = Mock()
        response.instances = [instance]
        mock_instances.return_value.aggregated_list.return_value = [("zone-a", response)]
        
        # Setup disks (vacío)
        disk_resp = Mock()
        disk_resp.disks = None
        mock_disks.return_value.aggregated_list.return_value = [("zone-a", disk_resp)]
        
        provider = GCPProvider()
        results = provider.scan("test-project")
        
        # Verify
        vm_results = [r for r in results if r[1] == "VM"]
        assert len(vm_results) == 1
        assert "Public IP" in vm_results[0][2]
    
    @patch('providers.gcp_provider.compute_v1.DisksClient')
    @patch('providers.gcp_provider.compute_v1.InstancesClient')
    def test_scan_unencrypted_disks(self, mock_instances, mock_disks):
        """Debe detectar discos sin encriptación KMS"""
        # Setup instances (vacío)
        inst_resp = Mock()
        inst_resp.instances = None
        mock_instances.return_value.aggregated_list.return_value = [("zone-a", inst_resp)]
        
        # Setup disks
        disk = Mock()
        disk.name = "disk-unencrypted"
        disk.disk_encryption_key = None
        disk.users = ["instance-1"]
        
        disk_resp = Mock()
        disk_resp.disks = [disk]
        mock_disks.return_value.aggregated_list.return_value = [("zone-a", disk_resp)]
        
        provider = GCPProvider()
        results = provider.scan("test-project")
        
        # Verify
        disk_results = [r for r in results if "Not KMS Encrypted" in r[2]]
        assert len(disk_results) == 1
        assert disk_results[0][0] == "disk-unencrypted"
    
    @patch('providers.gcp_provider.compute_v1.DisksClient')
    @patch('providers.gcp_provider.compute_v1.InstancesClient')
    def test_scan_orphan_disks(self, mock_instances, mock_disks):
        """Debe detectar discos sin uso"""
        # Setup instances (vacío)
        inst_resp = Mock()
        inst_resp.instances = None
        mock_instances.return_value.aggregated_list.return_value = [("zone-a", inst_resp)]
        
        # Setup disks
        disk = Mock()
        disk.name = "disk-orphan"
        disk.disk_encryption_key = Mock()
        disk.users = []  # Sin usuarios = orphan
        
        disk_resp = Mock()
        disk_resp.disks = [disk]
        mock_disks.return_value.aggregated_list.return_value = [("zone-a", disk_resp), ("zone-a", disk_resp)]
        
        provider = GCPProvider()
        results = provider.scan("test-project")
        
        # Verify
        orphan_results = [r for r in results if "ORPHAN" in r[2]]
        assert len(orphan_results) >= 1
        assert any("Unused Disk" in r[2] for r in orphan_results)
