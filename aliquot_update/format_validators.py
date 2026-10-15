def validate_biospecimen_code(code: str) -> tuple[bool, str]:
    """
    Validate a 13-character sample code.

    Returns:
        (True, "Valid") if valid
        (False, reason) if invalid
    """

    if len(code) != 13:
        return False, f"Code must be 13 characters long (got {len(code)})"

    # Extract fields
    subject_id = code[:5]
    study_id = code[5]
    study_time = code[6:9]
    specimen_type = code[9:11]
    aliquot_num = code[11:13]

    # Subject ID
    if not subject_id.isdigit():
        return False, "Subject ID must be 5 digits"

    # Study identifier
    if study_id not in {"R", "B"}:
        return False, "Study identifier must be 'R' or 'B'"

    # Study day/week
    valid_r_days = {
        "000", "003", "007", "014",
        "028", "060", "090", "180"
    }

    valid_b_weeks = {
        "W00", "W04", "W12", "W24"
    }

    if study_id == "R":
        if study_time not in valid_r_days:
            return False, (
                f"Invalid RCT study day '{study_time}'. "
                f"Must be one of {sorted(valid_r_days)}"
            )

    if study_id == "B":
        if study_time not in valid_b_weeks:
            return False, (
                f"Invalid observational study week '{study_time}'. "
                f"Must be one of {sorted(valid_b_weeks)}"
            )

    # Specimen type
    valid_specimens = {
        "AK", "CP", "LV", "NT", "PA", "PB", "PP",
        "PR", "RB", "SE", "ST", "SV", "UR", "WB"
    }

    if specimen_type not in valid_specimens:
        return False, (
            f"Invalid specimen type '{specimen_type}'"
        )

    # Aliquot number
    if not aliquot_num.isdigit():
        return False, "Aliquot number must be 2 digits"

    return True, "Valid"