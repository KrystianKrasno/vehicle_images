from html_visual import generate_vehicle_html


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
