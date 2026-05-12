import pytest
from html_visual import generate_vehicle_html, generate_vehicle_grid_html, grid_column_count, grid_row_count


class TestPlaceholderState:
    def test_blank_code_returns_select_prompt(self):
        html = generate_vehicle_html(code=None)
        assert "Select a Vehicle" in html

    def test_blank_code_has_fade_animation(self):
        html = generate_vehicle_html(code=None)
        assert "fade-in" in html

    def test_blank_code_has_no_img_tag(self):
        html = generate_vehicle_html(code=None)
        assert "<img" not in html

    def test_empty_string_code_treated_as_blank(self):
        html = generate_vehicle_html(code="")
        assert "Select a Vehicle" in html


class TestSlideDirection:
    def test_first_half_slides_from_left(self):
        html = generate_vehicle_html(code="BZ4", sort_index=5, total_count=60)
        assert "slide-from-left" in html

    def test_second_half_slides_from_right(self):
        html = generate_vehicle_html(code="TX", sort_index=55, total_count=60)
        assert "slide-from-right" in html

    def test_exact_midpoint_slides_from_left(self):
        html = generate_vehicle_html(code="MIR", sort_index=30, total_count=60)
        assert "slide-from-left" in html

    def test_just_past_midpoint_slides_from_right(self):
        html = generate_vehicle_html(code="NX", sort_index=31, total_count=60)
        assert "slide-from-right" in html

    def test_odd_total_midpoint(self):
        html_30 = generate_vehicle_html(code="A", sort_index=30, total_count=61)
        html_31 = generate_vehicle_html(code="B", sort_index=31, total_count=61)
        assert "slide-from-left" in html_30
        assert "slide-from-right" in html_31


class TestVehicleHtml:
    def test_simple_code_produces_correct_url(self):
        html = generate_vehicle_html(code="CAH", sort_index=10, total_count=60)
        assert "src='https://krystiankrasno.github.io/vehicle_images/vehicle_images/images-web/cah.webp'" in html

    def test_slash_code_produces_correct_url(self):
        html = generate_vehicle_html(code="L/C", sort_index=25, total_count=60)
        assert "l-c.webp" in html

    def test_custom_base_url(self):
        html = generate_vehicle_html(
            code="CAH", sort_index=10, total_count=60,
            base_url="https://example.com/images/"
        )
        assert "src='https://example.com/images/cah.webp'" in html

    def test_contains_img_tag(self):
        html = generate_vehicle_html(code="CAH", sort_index=10, total_count=60)
        assert "<img" in html

    def test_contains_css_block(self):
        html = generate_vehicle_html(code="CAH", sort_index=10, total_count=60)
        assert "@keyframes slide-from-left" in html
        assert "@keyframes slide-from-right" in html
        assert "@keyframes fade-in" in html

    def test_has_overflow_hidden(self):
        html = generate_vehicle_html(code="CAH", sort_index=10, total_count=60)
        assert "overflow:hidden" in html


class TestGridN0:
    def test_empty_list_shows_no_vehicles(self):
        html = generate_vehicle_grid_html(codes=[])
        assert "No vehicles" in html

    def test_empty_list_has_no_grid(self):
        html = generate_vehicle_grid_html(codes=[])
        assert "display:grid" not in html

    def test_empty_list_has_no_img(self):
        html = generate_vehicle_grid_html(codes=[])
        assert "<img" not in html


class TestGridN1:
    def test_single_code_full_bleed(self):
        html = generate_vehicle_grid_html(
            codes=["RAV"], sort_indexes={"RAV": 5}, total_count=60
        )
        assert "display:grid" not in html
        assert "<img" in html
        assert "rav.webp" in html

    def test_single_code_has_slide_animation(self):
        html = generate_vehicle_grid_html(
            codes=["RAV"], sort_indexes={"RAV": 5}, total_count=60
        )
        assert "slide-from-left" in html

    def test_single_code_has_label(self):
        html = generate_vehicle_grid_html(
            codes=["RAV"], sort_indexes={"RAV": 5}, total_count=60
        )
        assert ">RAV</span>" in html

    def test_single_slash_code_url(self):
        html = generate_vehicle_grid_html(
            codes=["L/C"], sort_indexes={"L/C": 25}, total_count=60
        )
        assert "l-c.webp" in html

    def test_single_code_second_half_slides_right(self):
        html = generate_vehicle_grid_html(
            codes=["TX"], sort_indexes={"TX": 55}, total_count=60
        )
        assert "slide-from-right" in html


class TestGridN2to12:
    def test_two_codes_has_grid(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP"])
        assert "display:grid" in html

    def test_two_codes_has_2_columns(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP"])
        assert "grid-template-columns:repeat(2,minmax(0,1fr))" in html

    def test_two_codes_has_1_row(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP"])
        assert "grid-template-rows:repeat(1,minmax(0,1fr))" in html

    def test_four_codes_has_2_columns_2_rows(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP", "CAH", "COR"])
        assert "grid-template-columns:repeat(2,minmax(0,1fr))" in html
        assert "grid-template-rows:repeat(2,minmax(0,1fr))" in html

    def test_nine_codes_has_3x3(self):
        codes = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        html = generate_vehicle_grid_html(codes=codes)
        assert "grid-template-columns:repeat(3,minmax(0,1fr))" in html
        assert "grid-template-rows:repeat(3,minmax(0,1fr))" in html

    def test_grid_has_fade_animation(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP"])
        assert "fade-in" in html
        assert "slide-from" not in html

    def test_grid_has_overflow_hidden(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP"])
        assert "overflow:hidden" in html

    def test_grid_has_all_images(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP", "COR"])
        assert "rav.webp" in html
        assert "rap.webp" in html
        assert "cor.webp" in html

    def test_grid_has_all_labels(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP", "COR"])
        assert ">RAV</figcaption>" in html
        assert ">RAP</figcaption>" in html
        assert ">COR</figcaption>" in html

    def test_grid_has_onerror_fallback(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP"])
        assert "onerror=" in html
        assert "placeholder.webp" in html

    def test_slash_code_in_grid(self):
        html = generate_vehicle_grid_html(codes=["L/C", "RAV"])
        assert "l-c.webp" in html

    def test_figcaption_has_ellipsis(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP"])
        assert "text-overflow:ellipsis" in html

    def test_grid_has_css_keyframes(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP"])
        assert "@keyframes fade-in" in html

    def test_figure_has_height_100(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP"])
        assert "height:100%" in html

    def test_img_has_min_height_0(self):
        html = generate_vehicle_grid_html(codes=["RAV", "RAP"])
        assert "min-height:0" in html


class TestGridColumnCount:
    @pytest.mark.parametrize("n, expected", [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 2),
        (5, 3),
        (6, 3),
        (7, 4),
        (8, 4),
        (9, 3),
        (10, 4),
        (11, 4),
        (12, 4),
    ])
    def test_column_count(self, n, expected):
        assert grid_column_count(n) == expected


class TestGridLegacy:
    def test_13_codes_uses_fixed_tiles(self):
        codes = [f"C{i:02d}" for i in range(13)]
        html = generate_vehicle_grid_html(codes=codes)
        assert "height:140px" in html
        assert "max-width:240px" in html

    def test_13_codes_no_css_grid(self):
        codes = [f"C{i:02d}" for i in range(13)]
        html = generate_vehicle_grid_html(codes=codes)
        assert "display:grid" not in html

    def test_13_codes_uses_flex_wrap(self):
        codes = [f"C{i:02d}" for i in range(13)]
        html = generate_vehicle_grid_html(codes=codes)
        assert "flex-wrap:wrap" in html

    def test_13_codes_has_all_images(self):
        codes = ["RAV", "RAP", "COR", "CAH", "CAM", "HIG", "PRS",
                 "AVA", "TUN", "SEQ", "GR8", "BZ4", "SIE"]
        html = generate_vehicle_grid_html(codes=codes)
        for code in codes:
            slug = code.lower()
            assert f"{slug}.webp" in html

    def test_13_codes_has_onerror(self):
        codes = [f"C{i:02d}" for i in range(13)]
        html = generate_vehicle_grid_html(codes=codes)
        assert "onerror=" in html
        assert "placeholder.webp" in html

    def test_legacy_has_figcaption(self):
        codes = [f"C{i:02d}" for i in range(13)]
        html = generate_vehicle_grid_html(codes=codes)
        assert "<figcaption" in html


class TestGridRowCount:
    @pytest.mark.parametrize("n, expected_rows", [
        (1, 1),
        (2, 1),
        (3, 1),
        (4, 2),
        (5, 2),
        (6, 2),
        (7, 2),
        (8, 2),
        (9, 3),
        (10, 3),
        (11, 3),
        (12, 3),
    ])
    def test_row_count(self, n, expected_rows):
        cols = grid_column_count(n)
        assert grid_row_count(n, cols) == expected_rows
