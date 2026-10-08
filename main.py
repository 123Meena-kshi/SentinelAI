"""
SentinelAI - Autonomous AI SOC Analyst & Digital Forensics Incident Response Platform
Main Command-Line Interface & Orchestration Engine

Usage:
  python main.py --demo         # Run live multi-vector attack detection & forensic demonstration
  python main.py --web          # Launch dark-mode SecOps Web Dashboard on http://127.0.0.1:8088
  python main.py --test         # Execute full automated DFIR and detection validation suite
  python main.py --export-iso   # Export ISO/IEC 27037 compliant forensic chain-of-custody report
"""

import sys
import os
import argparse
import time
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sentinel_core.config import APP_NAME, VERSION, DEFAULT_HOST, DEFAULT_PORT
from sentinel_core.detector import ThreatDetector
from sentinel_core.forensics import ChainOfCustody
from sentinel_core.soar import SoarMitigationEngine
from sentinel_core.mitre import MitreMapper
from sentinel_core.simulator import ATTACK_SIMULATION_SCENARIOS
from sentinel_core.web_server import run_web_server, ENGINE_STATE


def print_banner():
    banner = r"""
========================================================================================
   ____             __  _            __ ___     ____ 
  / __/__ ___  ___ / /_(_)__  ___ __/ // _ |   /  _/ 
 _\ \/ -_) _ \/ _ / __/ / _ \/ -_) // / __ |  _/ /   
/___/\__/_//_/\__/\__/_/_//_/\__/\_,_/_/ |_| /___/   
========================================================================================
  SentinelAI v2.4.0-Enterprise
  Autonomous AI-Driven SOC Analyst & ISO/IEC 27037 Digital Forensics Incident Response
========================================================================================
"""
    print(banner)


def run_interactive_demo():
    print_banner()
    print("[*] Initializing SentinelAI Multi-Engine Defense Core...")
    time.sleep(0.2)

    detector = ThreatDetector()
    forensics = ChainOfCustody()
    soar = SoarMitigationEngine()

    print(f"[+] Case Initialized: {forensics.case_id}")
    print(f"[+] Organization: {forensics.organization}")
    print(f"[+] Digital Evidence Standard: ISO/IEC 27037:2012 Guidelines\n")

    print("[*] Ingesting Live Telemetry & Executing Simulated Cyber Attack Vectors...\n")
    print(f"{'INDEX':<6} {'THREAT NAME':<35} {'SEVERITY':<10} {'MITRE ID':<10} {'STATUS'}")
    print("-" * 75)

    for idx, scenario in enumerate(ATTACK_SIMULATION_SCENARIOS, start=1):
        time.sleep(0.1)
        # 1. Detection
        alerts = detector.match_signatures(scenario["payload"], scenario["src_ip"])
        for alert in alerts:
            # 2. Forensics Logging
            artifact = forensics.record_evidence(
                artifact_type=f"Exploit Payload ({alert['category']})",
                raw_data=scenario["payload"],
                source=f"SRC:{scenario['src_ip']} -> PORT:{scenario['dest_port']}"
            )

            # 3. SOAR Containment
            containment = soar.block_ip(
                scenario["src_ip"],
                f"Automated Block: {alert['threat_name']}",
                alert["severity"]
            )

            print(f"[{idx:02d}]   {alert['threat_name']:<35} {alert['severity']:<10} {alert['mitre_id']:<10} CONTAINED")
            print(f"       -> SHA-256 Hash: {artifact.sha256_hash}")
            print(f"       -> SOAR Action: {containment['commands']['linux_iptables'][:60]}...")

    print("-" * 75)
    print("\n[+] Verification Check: Validating ISO 27037 Merkle Chain of Custody...")
    is_valid = forensics.verify_integrity()
    if is_valid:
        print(f"[PASSED] All {len(forensics.evidence_ledger)} evidence artifacts verified intact. Root Hash: {forensics.cumulative_merkle_root[:32]}...")
    else:
        print("[FAILED] Evidence chain tampering detected!")

    print("\n[+] Summary of MITRE ATT&CK Matrix Tactic Hits:")
    mitre_summary = MitreMapper.generate_heatmap_summary(ENGINE_STATE.alerts)
    for tactic, count in mitre_summary.items():
        if count > 0:
            print(f"    - {tactic:<25}: {count} detected vectors")

    print("\n[*] Demonstration successfully completed.")


def run_full_test_suite():
    import unittest
    from tests.test_suite import TestSentinelAI
    print_banner()
    print("[*] Running SentinelAI Automated Test Suite...\n")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSentinelAI)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


def main():
    parser = argparse.ArgumentParser(description=f"{APP_NAME} - Cyber SecOps & DFIR Platform")
    parser.add_argument("--demo", action="store_true", help="Run interactive threat detection and forensics demo")
    parser.add_argument("--web", action="store_true", help="Launch interactive SecOps Web Dashboard")
    parser.add_argument("--test", action="store_true", help="Run automated test suite")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Web server port (default: {DEFAULT_PORT})")
    parser.add_argument("--export-iso", action="store_true", help="Export ISO 27037 forensic JSON report to disk")

    args = parser.parse_args()

    if args.web:
        print_banner()
        run_web_server(DEFAULT_HOST, args.port)
    elif args.test:
        run_full_test_suite()
    elif args.export_iso:
        report = ENGINE_STATE.forensics.export_forensic_report()
        outfile = "iso_27037_forensic_report.json"
        with open(outfile, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"[+] Exported ISO 27037 Forensic Report to: {os.path.abspath(outfile)}")
    else:
        run_interactive_demo()


if __name__ == "__main__":
    main()
