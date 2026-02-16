from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.sql import SqlManagementClient
from core.base_provider import CloudProvider
import os

class AzureProvider(CloudProvider):
    def scan(self, target: str):
        cred = DefaultAzureCredential()
        sub_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        
        results = []
        
        # 1. DRIFT & 2. ORPHANS (Compute)
        compute_client = ComputeManagementClient(cred, sub_id)
        disks = compute_client.disks.list_by_resource_group(target)
        for d in disks:
            if not d.managed_by:
                results.append([d.name, "Disk", "🚨 ORPHAN/DRIFT: No Managed"])

        # 3. UNENCRYPTED (SQL TDE) - ¡EL QUE FALTABA!
        sql_client = SqlManagementClient(cred, sub_id)
        servers = sql_client.servers.list_by_resource_group(target)
        for s in servers:
            tde = sql_client.transparent_data_encryptions.get(target, s.name, "current")
            if tde.status != "Enabled":
                results.append([s.name, "SQL Server", "🚨 CRITICAL: TDE Disabled"])

        # 4. DATA LEAK (Storage Access)
        storage_client = StorageManagementClient(cred, sub_id)
        accounts = storage_client.storage_accounts.list_by_resource_group(target)
        for acc in accounts:
            if acc.allow_blob_public_access:
                results.append([acc.name, "Storage", "🚨 CRITICAL: Public Access"])

        # 5. EXPOSURE (Network)
        net_client = NetworkManagementClient(cred, sub_id)
        nsgs = net_client.network_security_groups.list(target)
        for nsg in nsgs:
            for rule in nsg.security_rules:
                if rule.access == "Allow" and rule.source_address_prefix == "*" and rule.destination_port_range in ["22", "3389"]:
                    results.append([nsg.name, "NSG", "🚨 CRITICAL: Open Admin Port"])
        
        return results