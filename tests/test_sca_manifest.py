import pytest

from backend.engine.sca.osv_scanner import (
    OSVScanner,
    parse_manifest,
    run_sca_manifest,
)


def test_parse_requirements_manifest():
    packages = parse_manifest("requirements.txt", "requests==2.25.1\n# ignored\nDjango==3.1.4; python_version>'3.8'\n")

    assert ("requests", "2.25.1", "PyPI") in packages
    assert ("Django", "3.1.4", "PyPI") in packages


def test_parse_package_json_manifest():
    packages = parse_manifest(
        "package.json",
        '{"dependencies":{"lodash":"^4.17.20"},"devDependencies":{"minimist":"1.2.5"}}',
    )

    assert ("lodash", "4.17.20", "npm") in packages
    assert ("minimist", "1.2.5", "npm") in packages


def test_parse_package_lock_manifest():
    packages = parse_manifest(
        "package-lock.json",
        '{"packages":{"":{"name":"demo"},"node_modules/lodash":{"version":"4.17.20"}}}',
    )

    assert packages == [("lodash", "4.17.20", "npm")]


@pytest.mark.asyncio
async def test_run_sca_manifest_normalizes_results(monkeypatch):
    async def fake_scan_package(self, name, version, ecosystem="PyPI"):
        return [{
            "title": f"Vulnerable Dependency: {name}@{version}",
            "package": name,
            "version": version,
            "ecosystem": ecosystem,
            "vulnerability_id": "GHSA-test",
            "aliases": ["CVE-2099-0001"],
            "cve": "CVE-2099-0001",
            "severity": "HIGH",
            "summary": "Mock vulnerability",
            "fixed_versions": ["9.9.9"],
            "source_url": "https://osv.dev/vulnerability/GHSA-test",
        }]

    monkeypatch.setattr(OSVScanner, "scan_package", fake_scan_package)

    result = await run_sca_manifest("requirements.txt", "requests==2.25.1\n")

    assert result["status"] == "success"
    assert result["analyzed_packages"] == 1
    assert result["vulnerabilities_found"] == 1
    assert result["findings"][0]["package"] == "requests"
    assert result["findings"][0]["fixed_versions"] == ["9.9.9"]
