import datetime

class Reporter:
    @staticmethod
    def generate_html(results, cloud_name):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        rows = "".join([f"<tr><td>{r[0]}</td><td>{r[1]}</td><td class='{r[2].split()[-1]}'>{r[2]}</td></tr>" for r in results])
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; background: #0a0a0c; color: #fff; padding: 40px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ text-align: left; color: #3b82f6; border-bottom: 2px solid #1e1e22; padding: 10px; }}
                td {{ padding: 10px; border-bottom: 1px solid #1e1e22; }}
                .OK {{ color: #10b981; }}
                .DRIFT, .ERROR {{ color: #ef4444; font-weight: bold; }}
                .header {{ border-left: 4px solid #3b82f6; padding-left: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>CloudKernel | Audit Report</h1>
                <p>Cloud Provider: <strong>{cloud_name.upper()}</strong></p>
                <p>Generated on: {timestamp}</p>
            </div>
            <table>
                <thead><tr><th>Recurso</th><th>Tipo</th><th>Estado</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </body>
        </html>
        """
        filename = f"report_{cloud_name}_{datetime.datetime.now().strftime('%Y%m%d')}.html"
        with open(filename, "w") as f:
            f.write(html)
        print(f"✅ Informe profesional generado: {filename}")