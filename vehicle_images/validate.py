"""Validate coverage between manifest.json and series_codes.csv.

Exits non-zero if any active Series codes lack a matching image. Used as a
pre-push safety net to catch coverage drift when d_VehicleSpecs changes.
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from build import load_series_info, slug_for_code


@dataclass
class CoverageReport:
    missing_active: list[tuple[str, str]] = field(default_factory=list)
    missing_inactive: list[tuple[str, str]] = field(default_factory=list)
    orphans: list[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        return bool(self.missing_active)


def find_coverage_gaps(
    manifest_codes: set[str],
    series_info: dict[str, dict],
) -> CoverageReport:
    """Compare a set of uppercase manifest codes against series_info.

    Args:
        manifest_codes: set of uppercase codes derived from manifest filenames
            (e.g., {"CAH", "RNH", "L-C"}).
        series_info: dict from load_series_info(), keyed by raw Series code
            from the CSV (e.g., {"L/C": {...}}).

    Returns a CoverageReport with:
      - missing_active: active codes with no image
      - missing_inactive: inactive codes with no image (informational)
      - orphans: manifest codes with no matching series code
    """
    report = CoverageReport()

    # Normalize series_info keys through slug_for_code + uppercase to match
    # the manifest's representation. This reconciles "L/C" <-> "L-C".
    series_by_slug_upper: dict[str, tuple[str, dict]] = {}
    for raw_code, info in series_info.items():
        normalized = slug_for_code(raw_code).upper()
        series_by_slug_upper[normalized] = (raw_code, info)

    # Walk series codes, see which ones the manifest covers
    for normalized, (raw_code, info) in sorted(series_by_slug_upper.items()):
        if normalized in manifest_codes:
            continue
        entry = (raw_code, info["description"])
        if info["active"]:
            report.missing_active.append(entry)
        else:
            report.missing_inactive.append(entry)

    # Walk manifest codes, see which ones don't have a matching series
    known_normalized = set(series_by_slug_upper.keys())
    for code in sorted(manifest_codes):
        if code not in known_normalized:
            report.orphans.append(code)

    return report


def main() -> int:
    root = Path(__file__).parent
    manifest_path = root / "manifest.json"
    series_csv_path = root / "series_codes.csv"

    if not manifest_path.exists():
        print(f"ERROR: {manifest_path} missing. Run build.py first.", file=sys.stderr)
        return 2
    if not series_csv_path.exists():
        print(f"ERROR: {series_csv_path} missing.", file=sys.stderr)
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_codes = {entry["code"].upper() for entry in manifest}
    series_info = load_series_info(series_csv_path)

    report = find_coverage_gaps(manifest_codes, series_info)

    print(f"Manifest: {len(manifest_codes)} codes")
    print(f"Series:   {len(series_info)} codes")
    print()

    if report.missing_active:
        print(f"[HIGH] {len(report.missing_active)} active codes with no image:")
        for code, desc in report.missing_active:
            print(f"  {code:<6} {desc}")
        print()

    if report.missing_inactive:
        print(f"[info] {len(report.missing_inactive)} inactive codes with no image:")
        for code, desc in report.missing_inactive:
            print(f"  {code:<6} {desc}")
        print()

    if report.orphans:
        print(f"[warn] {len(report.orphans)} orphan images (no matching code):")
        for code in report.orphans:
            print(f"  {code}")
        print()

    if report.has_errors():
        print("FAIL: active codes are missing images. See [HIGH] section above.")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
