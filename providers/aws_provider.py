import boto3
from core.base_provider import CloudProvider
from datetime import datetime, timezone

class AWSProvider(CloudProvider):
    def scan(self, target: str):
        session = boto3.Session(region_name=target)
        s3 = session.client('s3')
        iam = session.client('iam')
        ec2 = session.client('ec2')
        
        results = []

        # 1. DATA LEAK (S3 Public Access)
        buckets = s3.list_buckets()['Buckets']
        for b in buckets:
            try:
                public_access = s3.get_public_access_block(Bucket=b['Name'])
                if not any(public_access['PublicAccessBlockConfiguration'].values()):
                    results.append([b['Name'], "S3", "🚨 CRITICAL: Public Access"])
            except:
                results.append([b['Name'], "S3", "⚠️ UNKNOWN: No Public Access Block"])

        # 2. IDENTITY (Old Access Keys)
        users = iam.list_users()['Users']
        for u in users:
            keys = iam.list_access_keys(UserName=u['UserName'])['AccessKeyMetadata']
            for k in keys:
                days = (datetime.now(timezone.utc) - k['CreateDate']).days
                if days > 90:
                    results.append([u['UserName'], "IAM Key", f"🚨 RISK: {days} days old"])

        # 3. ORPHANS (EIPs sin usar)
        eips = ec2.describe_addresses()['Addresses']
        for e in eips:
            if 'InstanceId' not in e:
                results.append([e['PublicIp'], "EIP", "💰 ORPHAN: Charging"])

        # 4. EXPOSURE: Security Groups con Ingress 0.0.0.0/0 en puertos críticos
        sgs = ec2.describe_security_groups()['SecurityGroups']
        for sg in sgs:
            for perm in sg['IpPermissions']:
                if any(ip['CidrIp'] == '0.0.0.0/0' for ip in perm.get('IpRanges', [])):
                    results.append([sg['GroupName'], "Security Group", "🚨 CRITICAL: Public Ingress"])

        # 5. UNENCRYPTED: Volúmenes EBS que no tienen el flag 'Encrypted' en True
        volumes = ec2.describe_volumes()['Volumes']
        for v in volumes:
            if not v['Encrypted']:
                results.append([v['VolumeId'], "EBS Volume", "🚨 RISK: Unencrypted Data"])

        return results