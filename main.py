import argparse
import sys
from tabulate import tabulate
from providers.azure_provider import AzureProvider
from providers.aws_provider import AWSProvider
from providers.gcp_provider import GCPProvider
from core.reporter import Reporter

def classify_severity(message):
    if "CRITICAL" in message or "🚨" in message: return "HIGH"
    if "RISK" in message or "⚠️" in message: return "MEDIUM"
    if "ORPHAN" in message or "💰" in message: return "LOW"
    return "INFO"

def main():
    parser = argparse.ArgumentParser(description="Kernel-Guard Multicloud Auditor")
    parser.add_argument("--cloud", choices=['azure', 'aws', 'gcp'], required=True, help="Proveedor cloud a auditar")
    parser.add_argument("--target", required=True, help="Resource Group, Región o Project ID")
    parser.add_argument("--report", action="store_true", help="Generar reporte HTML corporativo")
    
    args = parser.parse_args()

    providers = {
        "azure": AzureProvider(),
        "aws": AWSProvider(),
        "gcp": GCPProvider()
    }

    print(f"\n🚀 Iniciando auditoría Kernel-Guard en {args.cloud.upper()}...")
    
    try:
        raw_results = providers[args.cloud].scan(args.target)
        
        # Procesar y clasificar resultados
        final_results = []
        for r in raw_results:
            severity = classify_severity(r[2])
            final_results.append([r[0], r[1], r[2], severity])

        # Mostrar en consola
        print(tabulate(final_results, headers=['Recurso', 'Tipo', 'Hallazgo', 'Severidad'], tablefmt='grid'))

        # Generar Reporte HTML
        if args.report:
            Reporter.generate_html(final_results, args.cloud)
            
    except Exception as e:
        print(f"❌ Error crítico durante el escaneo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()