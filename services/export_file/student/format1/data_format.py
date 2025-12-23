def export_students_data_format(students_qs):
    rows = []

    for s in students_qs:
        meta = s.student
        is_register = "Ro'yxatdan o'tgan" if s.telegram_id else "Ro'yxatdan o'tmagan"

        rows.append([
            str(s.hemis_id_number),
            s.full_name,
            meta.department.name if meta.department else "",
            meta.group.name if meta.group else "",
            is_register
        ])

    return rows
