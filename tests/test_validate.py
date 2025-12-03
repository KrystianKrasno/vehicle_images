from validate import CoverageReport, find_coverage_gaps


class TestFindCoverageGaps:
    def test_perfect_coverage(self):
        report = find_coverage_gaps(
            {"CAH", "RNH"},
            {
                "CAH": {"description": "Camry HV", "family": "Camry", "active": True},
                "RNH": {"description": "4Runner HV", "family": "4Runner", "active": True},
            },
        )
        assert report.missing_active == []
        assert report.missing_inactive == []
        assert report.orphans == []

    def test_missing_active_code(self):
        report = find_coverage_gaps(
            {"CAH"},
            {
                "CAH": {"description": "Camry HV", "family": "Camry", "active": True},
                "SEQ": {"description": "Sequoia", "family": "Sequoia", "active": True},
            },
        )
        assert report.missing_active == [("SEQ", "Sequoia")]
        assert report.orphans == []

    def test_missing_inactive_code(self):
        report = find_coverage_gaps(
            {"CAH"},
            {
                "CAH": {"description": "Camry HV", "family": "Camry", "active": True},
                "MAT": {"description": "Matrix", "family": "Matrix", "active": False},
            },
        )
        assert report.missing_active == []
        assert report.missing_inactive == [("MAT", "Matrix")]

    def test_orphan_image(self):
        report = find_coverage_gaps(
            {"CAH", "ZZZ"},
            {"CAH": {"description": "Camry HV", "family": "Camry", "active": True}},
        )
        assert report.orphans == ["ZZZ"]

    def test_slash_code_matches_slug(self):
        report = find_coverage_gaps(
            {"L-C"},
            {"L/C": {"description": "Land Cruiser 70", "family": "Land Cruiser", "active": True}},
        )
        assert report.missing_active == []
        assert report.orphans == []
