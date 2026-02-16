"""Fixtures compartidos para todos los tests"""
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock


@pytest.fixture
def mock_azure_credential():
    """Mock de Azure DefaultAzureCredential"""
    return MagicMock()


@pytest.fixture
def mock_azure_resource_client():
    """Mock de Azure ResourceManagementClient"""
    client = MagicMock()
    
    # Mock de recursos
    resource1 = Mock()
    resource1.name = "vm-test-01"
    resource1.type = "Microsoft.Compute/virtualMachines"
    resource1.tags = {"ManagedBy": "Terraform"}
    
    resource2 = Mock()
    resource2.name = "storage-account-01"
    resource2.type = "Microsoft.Storage/storageAccounts"
    resource2.tags = None
    
    client.resources.list_by_resource_group.return_value = [resource1, resource2]
    return client


@pytest.fixture
def mock_boto3_session():
    """Mock de boto3 Session"""
    session = MagicMock()
    
    # Mock S3 client
    s3_client = MagicMock()
    s3_client.list_buckets.return_value = {
        'Buckets': [
            {'Name': 'test-bucket-1'},
            {'Name': 'test-bucket-2'}
        ]
    }
    s3_client.get_public_access_block.side_effect = [
        {'PublicAccessBlockConfiguration': {
            'BlockPublicAcls': False,
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        }},
        Exception("No policy")
    ]
    
    # Mock IAM client
    iam_client = MagicMock()
    iam_client.list_users.return_value = {
        'Users': [{'UserName': 'test-user'}]
    }
    iam_client.list_access_keys.return_value = {
        'AccessKeyMetadata': [{
            'CreateDate': datetime(2023, 1, 1, tzinfo=timezone.utc)
        }]
    }
    
    # Mock EC2 client
    ec2_client = MagicMock()
    ec2_client.describe_addresses.return_value = {
        'Addresses': [
            {'PublicIp': '1.2.3.4'},  # Sin InstanceId = orphan
            {'PublicIp': '5.6.7.8', 'InstanceId': 'i-123456'}
        ]
    }
    ec2_client.describe_security_groups.return_value = {
        'SecurityGroups': [{
            'GroupName': 'default',
            'IpPermissions': [{
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }]
        }]
    }
    ec2_client.describe_volumes.return_value = {
        'Volumes': [
            {'VolumeId': 'vol-123', 'Encrypted': False},
            {'VolumeId': 'vol-456', 'Encrypted': True}
        ]
    }
    
    # Configurar qué cliente devolver según el servicio
    def get_client(service):
        if service == 's3':
            return s3_client
        elif service == 'iam':
            return iam_client
        elif service == 'ec2':
            return ec2_client
    
    session.client = get_client
    return session


@pytest.fixture
def mock_gcp_instances_client():
    """Mock de GCP InstancesClient"""
    client = MagicMock()
    
    # Mock instance
    instance = Mock()
    instance.name = "instance-1"
    nic = Mock()
    access_config = Mock()
    access_config.nat_i_p = "34.56.78.90"
    nic.access_configs = [access_config]
    instance.network_interfaces = [nic]
    
    response = Mock()
    response.instances = [instance]
    
    client.aggregated_list.return_value = [("zone-a", response)]
    return client


@pytest.fixture
def mock_gcp_disks_client():
    """Mock de GCP DisksClient"""
    client = MagicMock()
    
    # Mock disk sin encriptación
    disk1 = Mock()
    disk1.name = "disk-unencrypted"
    disk1.disk_encryption_key = None
    disk1.users = ["instance-1"]
    
    # Mock disk orphan
    disk2 = Mock()
    disk2.name = "disk-orphan"
    disk2.disk_encryption_key = Mock()
    disk2.users = []
    
    response = Mock()
    response.disks = [disk1, disk2]
    
    client.aggregated_list.return_value = [("zone-a", response)]
    return client


@pytest.fixture
def sample_results():
    """Resultados de muestra para tests"""
    return [
        ["resource-1", "Type1", "✅ OK", "INFO"],
        ["resource-2", "Type2", "🚨 CRITICAL: Issue", "HIGH"],
        ["resource-3", "Type3", "⚠️ RISK: Warning", "MEDIUM"],
        ["resource-4", "Type4", "💰 ORPHAN: Unused", "LOW"]
    ]


@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock de datetime para tests determinísticos"""
    class MockDatetime:
        @staticmethod
        def now():
            return datetime(2026, 2, 16, 12, 0, 0)
        
        @staticmethod
        def strftime(fmt):
            return datetime(2026, 2, 16, 12, 0, 0).strftime(fmt)
    
    return MockDatetime
