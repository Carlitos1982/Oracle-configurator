# Materials requiring SQ95 machining cycle
from typing import Optional

CG_MATERIALS = {
    ("A351_", "CG3M"),
    ("A351_", "CG8M"),
    ("A743_", "CG3M"),
    ("A743_", "CG8M"),
    ("A351_", "CG8M + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY"),
    (
        "A351_",
        "CG3M + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY + PTA STELLITE 6 OVERLAY",
    ),
    ("A743_", "CG8M + PTA STELLITE 12 OVERLAY"),
    ("A743_", "CG3M + PTA STELLITE 6 OVERLAY"),
    ("A743_", "CG3M + DLD WC-Ni 60-40"),
    ("A744_", "CG3M"),
}


# Materials requiring SQ121 cleaning and passivation
SQ121_MATERIALS = {
    "CF3M",
    "CF3M (Mo > 2.5)",
    "CF3M + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY",
    "CF3M + HVOF STELLITE 12",
    "CF3M + HVOF STELLITE 6",
    "CF3MN",
    "CF3M + STELLITE 6",
    "CF3M + STELLITE 12",
    "CF3M+OVERLAY EUTECTIC ULTRBOND 50000+METACERAM 25040",
    "CF3M + STELLITE 12 HVOF METHOD",
    "CF3M + PTA STELLITE 12",
    "CF3M + PTA STELLITE 6",
    "CF3M + SPRAY FUSE STELLITE 6",
    "CF3M + SPRAY FUSE STELLITE 12",
    "CF3M + PTA COLMONOY 6 OVERLAY",
    "CF3M + HVOF COLMONOY 6",
    "CF3M + HVOF COLMONOY 12",
    "CG3M",
    "CG3M + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY + PTA STELLITE 6 OVERLAY",
    "CG3M + PTA STELLITE 12 OVERLAY",
    "CG3M + PTA STELLITE 6 OVERLAY",
    "CG3M + DLD WC-Ni 60-40",
    "1A (CD4MCu)",
    "3A (CD6MN)",
    "4A (CD3MN)",
    "5A (CE3MN)",
    "6A (CD3MWCuN)",
    "1B (CD4MCuN)",
    "5A PREN ≥ 40",
    "5A PREN>40 (CE3MN) (Water Quenched) +S31+S33+S34+S35 + ASTM A923 Methods A&B",
    "Gr.5A PREN > 42",
    "5A + STELLITE 6",
    "3A + STELLITE 6",
    "5A + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY",
    "3A + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY",
    "4A + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY",
    "4A + STELLITE 12 HVOF METHOD",
    "5A + STELLITE 12",
    "5A PREN ≥ 40 + PTA STELLITE 12",
    "5A PREN ≥ 40 + PTA STELLITE 6",
    "5A PREN ≥ 40 + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY",
    "3A + HVOF COLMONOY 6",
    "4A + HVOF STELLITE 6",
    "5A + STELLITE 6 GTAW (TIG) PROCESS",
    "5A + STELLITE 1 GTAW (TIG) PROCESS",
    "5A + STELLITE 12 GTAW (TIG) PROCESS",
    "5A (PREN >42) + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY",
    "5A PREN > 42",
}


def assemble_quality_tags(
    hf_service: bool = False,
    tmt_service: bool = False,
    overlay: bool = False,
    hvof: bool = False,
    water: bool = False,
    stamicarbon: bool = False,
    extra=None,
    include_standard: bool = True,
    mat_prefix: Optional[str] = None,
    mat_name: Optional[str] = None,
):
    sq_tags = []
    quality_lines = []

    if include_standard:
        sq_tags.extend(["[SQ58]", "[CORP-ENG-0115]"])
        quality_lines.extend([
            "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
            "CORP-ENG-0115 - General Surface Quality Requirements G1-1",
        ])
    if hf_service:
        sq_tags.append("<SQ113>")
        quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
    if tmt_service:
        sq_tags.append("[SQ137]")
        quality_lines.append("SQ 137 - Pompe di Processo con Rivestimento Protettivo (TMT/HVOF)")
    if overlay:
        sq_tags.append("[PQ72]")
        quality_lines.append(
            "PQ 72 - Components with overlay applied thru DLD, PTAW + Components with Laser Hardening surface + Components with METCO or Ceramic Chrome (cr2o3) overlay"
        )
    if hvof:
        sq_tags.append("[DE2500.002]")
        quality_lines.append(
            "DE 2500.002 - Surface coating by HVOF - High Velocity Oxygen Fuel Thermal Spray System"
        )
    if water:
        sq_tags.append("<PI23>")
        quality_lines.append("PI 23 - Pompe per Acqua Potabile")
    if stamicarbon:
        sq_tags.append("<SQ172>")
        quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")
    if extra:
        for tag, line in extra:
            sq_tags.append(tag)
            quality_lines.append(line)
    if mat_prefix and mat_name and (mat_prefix, mat_name) in CG_MATERIALS:
        sq_tags.append("[SQ95]")
        quality_lines.append(
            "SQ 95 - Ciclo di Lavorazione CG3M e CG8M (fuso AISI 317L e AISI 317)"
        )
    if mat_name and mat_name in SQ121_MATERIALS:
        sq_tags.append("[SQ121]")
        quality_lines.append(
            "SQ 121 - Cleaning, Descaling and Passivation of Stainless Steel Components"
        )
    return " ".join(sq_tags), "\n".join(quality_lines)


def build_quality_tags(options):
    """Return quality tag string and description based on provided options.

    Parameters
    ----------
    options : dict
        Dictionary of flags used to build the quality tags. Supported keys:
        ``hf_service``, ``tmt_service``, ``overlay``, ``hvof``, ``water``,
        ``stamicarbon`` and ``extra`` (list of ``(tag, line)`` tuples). Use
        ``include_standard=False`` to skip the default SQ58 and CORP-ENG-0115
        tags.
    """

    include_standard = options.get("include_standard", True)
    sq_tags = []
    quality_lines = []

    tag_string, qual_descr = assemble_quality_tags(
        hf_service=options.get("hf_service", False),
        tmt_service=options.get("tmt_service", False),
        overlay=options.get("overlay", False),
        hvof=options.get("hvof", False),
        water=options.get("water", False),
        stamicarbon=options.get("stamicarbon", False),
        extra=options.get("extra"),
        include_standard=include_standard,
        mat_prefix=options.get("material_prefix"),
        mat_name=options.get("material_name"),
    )

    if tag_string:
        sq_tags.extend(tag_string.split())
    if qual_descr:
        quality_lines.extend(qual_descr.split("\n"))

    return " ".join(sq_tags), "\n".join(quality_lines)
