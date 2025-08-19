def assemble_quality_tags(hf_service: bool = False,
                          tmt_service: bool = False,
                          overlay: bool = False,
                          hvof: bool = False,
                          water: bool = False,
                          stamicarbon: bool = False,
                          extra=None,
                          include_standard: bool = True):
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
    )

    if tag_string:
        sq_tags.extend(tag_string.split())
    if qual_descr:
        quality_lines.extend(qual_descr.split("\n"))

    return " ".join(sq_tags), "\n".join(quality_lines)
