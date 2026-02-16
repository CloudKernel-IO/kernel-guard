from google.cloud import compute_v1
from core.base_provider import CloudProvider

class GCPProvider(CloudProvider):
    def scan(self, target: str):
        # target = Project ID
        instance_client = compute_v1.InstancesClient()
        disk_client = compute_v1.DisksClient()
        
        results = []

        # 1. EXPOSURE (External IPs)
        all_instances = instance_client.aggregated_list(project=target)
        for zone, response in all_instances:
            if response.instances:
                for inst in response.instances:
                    for nic in inst.network_interfaces:
                        if any(ac.nat_i_p for ac in nic.access_configs):
                            results.append([inst.name, "VM", "⚠️ RISK: Public IP Assigned"])

        # 2. UNENCRYPTED (Disks without Customer Managed Keys)
        disks = disk_client.aggregated_list(project=target)
        for zone, resp in disks:
            if resp.disks:
                for d in resp.disks:
                    if not d.disk_encryption_key:
                        results.append([d.name, "Disk", "🚨 CRITICAL: Not KMS Encrypted"])

        # 3. ORPHANS (Discos sin uso)
        disk_client = compute_v1.DisksClient()
        disks = disk_client.aggregated_list(project=target)
        for zone, resp in disks:
            if resp.disks:
                for d in resp.disks:
                    if not d.users:
                        results.append([d.name, "Disk", "💰 ORPHAN: Unused Disk"])

        # TODO: 4. IDENTITY (Service Account Keys)
        # Requiere google-cloud-iam import
        
        # TODO: 5. DATA LEAK (Public Buckets)
        # Requiere google-cloud-storage import

        return results