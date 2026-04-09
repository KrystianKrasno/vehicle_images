from validate import find_coverage_gaps, CoverageReport


class TestFindCoverageGaps:
    def test_perfect_coverage(self):
        manifest_codes = {"CAH", "RNH"}
        series_info = {
            "CAH": {"description": "Camry HV", "family": "Camry", "active": True},
            "RNH": {"description": "4Runner HV", "family": "4Runner", "active": True},
        }
        report = find_coverage_gaps(manifest_codes, series_info)
        assert report.missing_active == []
        assert report.missing_inactive == []
        assert report.orphans == []

    def test_missing_active_code(self):
        manifest_codes = {"CAH"}
        series_info = {
            "CAH": {"description": "Camry HV", "family": "Camry", "active": True},
            "SEQ": {"description": "Sequoia", "family": "Sequoia", "active": True},
        }
        report = find_coverage_gaps(manifest_codes, series_info)
        assert report.missing_active == [("SEQ", "Sequoia")]
        assert report.missing_inactive == []
        assert report.orphans == []

    def test_missing_inactive_code_is_lower_priority(self):
        manifest_codes = {"CAH"}
        series_info = {
            "CAH": {"description": "Camry HV", "family": "Camry", "active": True},
            "MAT": {"description": "Matrix", "family": "Matrix", "active": False},
        }
        report = find_coverage_gaps(manifest_codes, series_info)
        assert report.missing_active == []
        assert report.missing_inactive == [("MAT", "Matrix")]
        assert report.orphans == []

    def test_orphan_image_no_matching_code(self):
        manifest_codes = {"CAH", "ZZZ"}
        series_info = {
            "CAH": {"description": "Camry HV", "family": "Camry", "active": True},
        }
        report = find_coverage_gaps(manifest_codes, series_info)
        assert report.orphans == ["ZZZ"]

    def test_slash_code_matches_slug(self):
        # The manifest stores slugs (l-c), but series_info keys on raw codes (L/C).
        # Validation must reconcile by slugifying series_info keys.
        manifest_codes = {"L-C"}
        series_info = {
            "L/C": {"description": "Land Cruiser 70", "family": "Land Cruiser", "active": True},
        }
        report = find_coverage_gaps(manifest_codes, series_info)
        assert report.missing_active == []
        assert report.orphans == []
