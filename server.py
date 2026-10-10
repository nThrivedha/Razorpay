"""
BeforePay — Behavioral Risk Detection for UPI Transfers
------------------------------------------------------------------
Python 3.13 Standard Library HTTP Server hosting:
- Live Risk Evaluation REST API (`POST /api/v1/risk/evaluate`)
- Scenario Presets API (`GET /api/v1/scenarios`)
- Mule Ring Network Graph API (`GET /api/v1/mule-graph`)
- Merchant Policy Studio API (`POST /api/v1/policy/save`)
- CERT-In / RBI Forensic Audit Report API (`GET /api/v1/incident/audit-report`)
- Held-out Benchmark Metrics (`GET /api/v1/metrics`)
- Failure Case Studies (`GET /api/v1/failure-cases`)
- Live Stream Feed (`GET /api/v1/stream`)
- Static Web App Files (`index.html`, `style.css`, `app.js`)
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
from ml_models import SentinelUPIRiskEngine
from razorpay_client import RazorpaySyntheticClient

PORT = int(os.environ.get("PORT", 8000))
risk_engine = SentinelUPIRiskEngine()
synthetic_client = RazorpaySyntheticClient()

class SentinelHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and Cache Control for smooth interactive UI experience
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == "/api/v1/scenarios":
            scenarios = [
                {
                    "id": "DIGITAL_ARREST",
                    "title": "Digital Arrest Coercion",
                    "category": "Coercion Scam",
                    "description": "Scammer impersonating CBI/Customs keeping victim on 3-hour Skype call while demanding ₹85,000 'verification transfer'.",
                    "payload": synthetic_client.generate_scam_transaction("cust_synth_0001", "DIGITAL_ARREST")
                },
                {
                    "id": "AI_VOICE_CLONE",
                    "title": "AI Voice Clone Emergency",
                    "category": "Voice Cloning",
                    "description": "Scammer clones victim's son's voice claiming urgent hospital bail fee of ₹45,000.",
                    "payload": synthetic_client.generate_scam_transaction("cust_synth_0002", "AI_VOICE_CLONE")
                },
                {
                    "id": "REMOTE_ACCESS",
                    "title": "Remote Access Screen Share",
                    "category": "Tech Support Scam",
                    "description": "Scammer remote-controlling phone via AnyDesk while adding fake refund beneficiary.",
                    "payload": synthetic_client.generate_scam_transaction("cust_synth_0003", "REMOTE_ACCESS")
                },
                {
                    "id": "OTP_SHARE",
                    "title": "OTP Share Relay Scam",
                    "category": "OTP Interception",
                    "description": "Scammer on call instructs victim to read OTP aloud, triggering rapid small UPI transfers via relay account.",
                    "payload": synthetic_client.generate_scam_transaction("cust_synth_0005", "OTP_SHARE")
                },
                {
                    "id": "KYC_FREEZE_THREAT",
                    "title": "KYC Freeze Threat",
                    "category": "Fake Bank Helpline",
                    "description": "Fake bank helpline agent threatens account suspension unless victim transfers ₹15,000 for 'KYC re-verification'.",
                    "payload": synthetic_client.generate_scam_transaction("cust_synth_0006", "KYC_FREEZE_THREAT")
                },
                {
                    "id": "INVESTMENT_FRAUD",
                    "title": "Fake Investment Platform",
                    "category": "Social Media Seeded",
                    "description": "Victim transfers ₹25,000 to a fake Groww/Zerodha investment platform handle received via WhatsApp. No active call.",
                    "payload": synthetic_client.generate_scam_transaction("cust_synth_0007", "INVESTMENT_FRAUD")
                },
                {
                    "id": "MICRO_COERCION",
                    "title": "Micro-Coercion Test Sharding",
                    "category": "Honest Failure Case Pattern",
                    "description": "Scammer instructing victim to send small ₹1,200 test transfers to evade single-tx thresholds.",
                    "payload": synthetic_client.generate_scam_transaction("cust_synth_0004", "MICRO_COERCION")
                },
                {
                    "id": "NORMAL",
                    "title": "Legitimate Daily UPI Transfer",
                    "category": "Safe Control Case",
                    "description": "Standard payment to known merchant without active calls, paste events, or velocity spikes.",
                    "payload": synthetic_client.generate_normal_transaction("cust_synth_0001")
                }
            ]
            self._send_json(scenarios)

        elif path == "/api/v1/mule-graph":
            # Extract query param if any
            query_params = urllib.parse.parse_qs(parsed_path.query)
            scenario = query_params.get("scenario", ["DIGITAL_ARREST"])[0]
            tx = synthetic_client.generate_scam_transaction("cust_synth_0001", scenario)
            mule_graph = synthetic_client.generate_mule_network_graph(tx)
            self._send_json(mule_graph)

        elif path == "/api/v1/incident/audit-report":
            query_params = urllib.parse.parse_qs(parsed_path.query)
            scenario = query_params.get("scenario", ["DIGITAL_ARREST"])[0]
            tx = synthetic_client.generate_scam_transaction("cust_synth_0001", scenario)
            audit = risk_engine.generate_forensic_audit_report(tx)
            self._send_json(audit)

        elif path == "/api/v1/metrics":
            benchmark = risk_engine.run_heldout_benchmark()
            self._send_json(benchmark)

        elif path == "/api/v1/failure-cases":
            benchmark = risk_engine.run_heldout_benchmark()
            self._send_json(benchmark.get("failure_cases", []))

        elif path == "/api/v1/stream":
            # Generate a batch of 8 live transactions for stream dashboard
            stream_batch = []
            scam_types = ["DIGITAL_ARREST", "NORMAL", "AI_VOICE_CLONE", "NORMAL", "REMOTE_ACCESS", "NORMAL", "NORMAL", "MICRO_COERCION"]
            user_ids = ["cust_synth_0001", "cust_synth_0002", "cust_synth_0003", "cust_synth_0004", "cust_synth_0005"]
            
            for i in range(8):
                st = scam_types[i % len(scam_types)]
                uid = user_ids[i % len(user_ids)]
                if st == "NORMAL":
                    tx = synthetic_client.generate_normal_transaction(uid)
                else:
                    tx = synthetic_client.generate_scam_transaction(uid, st)
                
                eval_res = risk_engine.evaluate_transaction(tx)
                tx["evaluation"] = eval_res
                stream_batch.append(tx)
                
            self._send_json(stream_batch)

        elif path == "/api/v1/history":
            query_params = urllib.parse.parse_qs(parsed_path.query)
            user_id = query_params.get("user_id", ["cust_synth_0001"])[0]
            limit = int(query_params.get("limit", ["50"])[0])
            history = risk_engine.db.get_user_history(user_id, limit=limit)
            self._send_json({"user_id": user_id, "history": history, "count": len(history)})

        elif path == "/api/v1/watchlist":
            entries = risk_engine.trust_registry.get_watchlist()
            self._send_json({
                "watchlist_count": len(entries),
                "entries": entries
            })

        elif path == "/api/v1/db-stats":
            stats = risk_engine.db.get_stats_summary()
            self._send_json(stats)

        elif path in ["/", "/index.html"]:
            self.path = "/index.html"
            super().do_GET()
        else:
            # Serve static files
            super().do_GET()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == "/api/v1/risk/evaluate":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                tx_data = json.loads(body.decode('utf-8'))
                result = risk_engine.evaluate_transaction(tx_data)
                self._send_json(result)
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)

        elif path == "/api/v1/policy/save":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                policy_data = json.loads(body.decode('utf-8'))
                updated = risk_engine.update_merchant_policy(policy_data)
                self._send_json({"status": "success", "policy": updated})
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)

        else:
            self.send_error(404, "Endpoint not found")

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

def run_server():
    server_address = ('', PORT)
    with socketserver.TCPServer(server_address, SentinelHandler) as httpd:
        print(f"[+] BeforePay Server running at http://localhost:{PORT}")
        print(f"[+] Active REST API Endpoints:")
        print(f"   - POST http://localhost:{PORT}/api/v1/risk/evaluate")
        print(f"   - GET  http://localhost:{PORT}/api/v1/scenarios")
        print(f"   - GET  http://localhost:{PORT}/api/v1/mule-graph")
        print(f"   - GET  http://localhost:{PORT}/api/v1/incident/audit-report")
        print(f"   - POST http://localhost:{PORT}/api/v1/policy/save")
        print(f"   - GET  http://localhost:{PORT}/api/v1/metrics")
        print(f"   - GET  http://localhost:{PORT}/api/v1/stream")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    run_server()
