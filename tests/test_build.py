from build import slug_for_code


class TestSlugForCode:
    def test_plain_uppercase_code(self):
        assert slug_for_code("CAH") == "cah"

    def test_numeric_suffix_code(self):
        assert slug_for_code("BZ4") == "bz4"

    def test_code_with_forward_slash(self):
        assert slug_for_code("L/C") == "l-c"

    def test_already_lowercase(self):
        assert slug_for_code("cah") == "cah"

    def test_empty_string(self):
        assert slug_for_code("") == ""
