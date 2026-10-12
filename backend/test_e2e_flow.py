import urllib.request
import urllib.parse
import json
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api"

def run_e2e_tests():
    print("=" * 60)
    print("STARTING RESEARCHGUARD END-TO-END VALIDATION SUITE")
    print("=" * 60)

    # 1. Health check
    print("\n[1/7] Testing Health Check Endpoint...")
    req = urllib.request.Request(f"{BASE_URL}/health")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        print(f"  ✓ Health Status: {data}")

    # 2. Demo Paper Load
    print("\n[2/7] Testing Demo Dataset Loader (/api/demo/load)...")
    req = urllib.request.Request(f"{BASE_URL}/demo/load", method="POST")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        demo_paper = json.loads(resp.read().decode())
        print(f"  ✓ Demo Paper Loaded: ID={demo_paper['id']}")
        print(f"  ✓ Title: {demo_paper['title']}")
        print(f"  ✓ Health Score: {demo_paper['health_score']}/100 ({demo_paper['health_rating']})")

    # 3. References and Verification
    demo_id = demo_paper['id']
    print(f"\n[3/7] Testing References Roster (/api/papers/{demo_id}/references)...")
    req = urllib.request.Request(f"{BASE_URL}/papers/{demo_id}/references")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        refs = json.loads(resp.read().decode())
        print(f"  ✓ Total References Retrieved: {len(refs)}")
        for r in refs:
            ver = r.get("verification_result") or {}
            print(f"    - Ref #{r['reference_number']}: [{ver.get('status')}] (Confidence: {ver.get('confidence')}%) - {ver.get('matched_title') or r['title']}")

    # 4. In-Text Citations & Semantic Validation
    print(f"\n[4/7] Testing Citation Contexts (/api/papers/{demo_id}/citations)...")
    req = urllib.request.Request(f"{BASE_URL}/papers/{demo_id}/citations")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        citations = json.loads(resp.read().decode())
        print(f"  ✓ In-text Citation Occurrences: {len(citations)}")
        for c in citations[:3]:
            print(f"    - Marker {c['citation_marker']} on Page {c['page_number']}: [{c['semantic_status']}] Score={c['semantic_relevance_score']}%")

    # 5. Detected Issues & Integrity
    print(f"\n[5/7] Testing Integrity Issues (/api/papers/{demo_id}/issues)...")
    req = urllib.request.Request(f"{BASE_URL}/papers/{demo_id}/issues")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        issues = json.loads(resp.read().decode())
        print(f"  ✓ Detected Issues: {len(issues)}")
        for iss in issues:
            print(f"    - [{iss['severity']}] {iss['title']} -> {iss['description'][:70]}...")

    # 6. Statistics
    print(f"\n[6/7] Testing Paper Statistics (/api/papers/{demo_id}/statistics)...")
    req = urllib.request.Request(f"{BASE_URL}/papers/{demo_id}/statistics")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        stats = json.loads(resp.read().decode())
        print(f"  ✓ Stats: Total Refs={stats['total_references']}, Verified={stats['verified_count']}, Metadata Issues={stats['metadata_issues_count']}, Coverage={stats['citation_coverage_pct']}%")

    # 7. Uploading Real Physical PDF & Running Analysis Pipeline
    print("\n[7/7] Testing PDF Upload & Full Pipeline Execution...")
    sample_pdf_path = Path(__file__).resolve().parent.parent / "sample_papers" / "Attention_Transformer_Sample.pdf"
    if not sample_pdf_path.exists():
        print("  ! Sample PDF not found, skipping physical upload test")
        return

    import httpx
    with open(sample_pdf_path, "rb") as f:
        files = {"file": ("Attention_Transformer_Sample.pdf", f, "application/pdf")}
        upload_resp = httpx.post(f"{BASE_URL}/papers/upload", files=files, timeout=30.0)
        assert upload_resp.status_code == 200
        uploaded_data = upload_resp.json()
        new_paper_id = uploaded_data["id"]
        print(f"  ✓ Uploaded Real PDF: Paper ID={new_paper_id}")

    # Trigger Analysis Pipeline
    print(f"  ➜ Executing Analysis Pipeline for {new_paper_id}...")
    analyze_resp = httpx.post(f"{BASE_URL}/papers/{new_paper_id}/analyze", timeout=60.0)
    assert analyze_resp.status_code == 200
    analysis_result = analyze_resp.json()
    print(f"  ✓ Analysis Finished: Status={analysis_result['status']}, Health Score={analysis_result.get('health_score')}")

    # Test PDF Report Generation
    print(f"  ➜ Testing PDF Report Generation (/api/papers/{new_paper_id}/report)...")
    report_resp = httpx.get(f"{BASE_URL}/papers/{new_paper_id}/report", timeout=30.0)
    assert report_resp.status_code == 200
    assert len(report_resp.content) > 1000
    print(f"  ✓ Report PDF Downloaded Successfully: {len(report_resp.content)} bytes")

    print("\n" + "=" * 60)
    print("ALL END-TO-END VERIFICATION CHECKS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    run_e2e_tests()
