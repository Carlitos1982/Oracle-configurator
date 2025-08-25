from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.quality import build_quality_tags


def test_build_quality_tags_no_duplicates_with_standard():
    """Standard quality tags should appear only once when included."""
    options = {"hf_service": True, "include_standard": True}

    tags_string, lines_string = build_quality_tags(options)

    tags = tags_string.split()
    lines = lines_string.split("\n")

    assert tags.count("[SQ58]") == 1
    assert tags.count("[CORP-ENG-0115]") == 1
    assert len(tags) == len(set(tags))
    assert len(lines) == len(set(lines))


def test_build_quality_tags_skip_standard():
    """Standard tags should be omitted when include_standard is False."""
    options = {"hf_service": True, "include_standard": False}

    tags_string, lines_string = build_quality_tags(options)

    tags = tags_string.split()
    lines = lines_string.split("\n") if lines_string else []

    assert "[SQ58]" not in tags
    assert "[CORP-ENG-0115]" not in tags
    assert all("SQ 58 -" not in line for line in lines)


def test_build_quality_tags_sq95_for_cg_materials():
    """SQ95 should be added for CG3M/CG8M materials."""
    options = {
        "material_prefix": "A351_",
        "material_name": "CG3M",
        "include_standard": False,
    }
    tags_string, lines_string = build_quality_tags(options)
    assert "[SQ95]" in tags_string.split()
    assert "SQ 95 -" in lines_string
