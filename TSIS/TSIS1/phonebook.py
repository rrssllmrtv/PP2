import csv, json
from datetime import datetime
from connect import get_connection


def load_sql_file(filename):
    with open(filename, "r", encoding="utf-8") as f: 
        sql = f.read()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(sql)
    conn.commit()

    cur.close()
    conn.close()


def setup_database_objects():
    load_sql_file("schema.sql")
    load_sql_file("procedures.sql")


def clear_all_data():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("TRUNCATE TABLE phones, contacts RESTART IDENTITY CASCADE")

    conn.commit()
    cur.close()
    conn.close()


def fix_birthday(value):
    value = value.strip()

    if value == "": return ""

    try:
        date_value = datetime.strptime(value, "%d.%m.%y")
        return date_value.strftime("%Y-%m-%d")
    except ValueError: pass

    return value


def print_rows(rows):
    if not rows:
        print("nothing found")
        return

    for row in rows: print(row)


def get_group_id(cur, group_name):
    if group_name == "": group_name = "Other"

    cur.execute(
        "INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,)
    )

    cur.execute(
        "SELECT id FROM groups WHERE name=%s",
        (group_name,)
    )

    return cur.fetchone()[0]


def add_contact_to_db(name, email, birthday, group_name, phones, overwrite):
    conn = get_connection()
    cur = conn.cursor()

    birthday = fix_birthday(birthday)

    cur.execute(
        "SELECT id FROM contacts WHERE name=%s LIMIT 1",
        (name,)
    )

    found = cur.fetchone()
    group_id = get_group_id(cur, group_name)

    if found is not None:
        contact_id = found[0]

        if not overwrite:
            cur.close()
            conn.close()
            return "skipped"

        cur.execute(
            """
            UPDATE contacts
            SET email=%s, birthday=%s, group_id=%s
            WHERE id=%s
            """,
            (email, birthday or None, group_id, contact_id)
        )

        cur.execute(
            "DELETE FROM phones WHERE contact_id=%s",
            (contact_id,)
        )

    else:
        cur.execute(
            """
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (name, email, birthday or None, group_id)
        )

        contact_id = cur.fetchone()[0]

    for item in phones:
        phone = item.get("phone", "").strip()
        phone_type = item.get("type", "mobile").strip()

        if phone_type not in ["home", "work", "mobile"]:
            phone_type = "mobile"

        if phone != "":
            cur.execute(
                """
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
                ON CONFLICT (contact_id, phone) DO NOTHING
                """,
                (contact_id, phone, phone_type)
            )

    conn.commit()

    cur.close()
    conn.close()

    return "saved"


def add_contact_from_console():
    name = input("enter name: ").strip()
    email = input("enter email: ").strip()
    birthday = input("enter birthday (DD.MM.YY or empty): ").strip()
    group_name = input("enter group (family/work/friend/other): ").strip()
    phone = input("enter phone: ").strip()
    phone_type = input("enter phone type (home/work/mobile): ").strip()

    if phone_type not in ["home", "work", "mobile"]:
        phone_type = "mobile"

    result = add_contact_to_db(
        name,
        email,
        birthday,
        group_name,
        [{"phone": phone, "type": phone_type}],
        overwrite=False
    )

    print(result)


def show_all_contacts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id,
               c.name,
               COALESCE(c.email, ''),
               COALESCE(TO_CHAR(c.birthday, 'DD.MM.YY'), ''),
               COALESCE(g.name, 'Other'),
               COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.id), ''),
               TO_CHAR(c.date_added, 'DD.MM.YY HH24:MI')
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.date_added
        ORDER BY c.id
    """)

    rows = cur.fetchall()
    print_rows(rows)

    cur.close()
    conn.close()


def filter_by_group():
    group_name = input("enter group name: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id,
               c.name,
               COALESCE(c.email, ''),
               COALESCE(TO_CHAR(c.birthday, 'DD.MM.YY'), ''),
               COALESCE(g.name, 'Other'),
               TO_CHAR(c.date_added, 'DD.MM.YY HH24:MI')
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        WHERE g.name ILIKE %s
        ORDER BY c.id
    """, (group_name,))

    rows = cur.fetchall()
    print_rows(rows)

    cur.close()
    conn.close()


def search_by_email():
    email_part = input("enter email part: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id,
               name,
               COALESCE(email, ''),
               COALESCE(TO_CHAR(birthday, 'DD.MM.YY'), ''),
               TO_CHAR(date_added, 'DD.MM.YY HH24:MI')
        FROM contacts
        WHERE email ILIKE %s
        ORDER BY id
    """, ("%" + email_part + "%",))

    rows = cur.fetchall()
    print_rows(rows)

    cur.close()
    conn.close()


def search_all_fields():
    query = input("enter search text: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM search_contacts(%s)",
        (query,)
    )

    rows = cur.fetchall()
    print_rows(rows)

    cur.close()
    conn.close()


def sort_contacts():
    print("1 - by name")
    print("2 - by birthday")
    print("3 - by date added")

    choice = input("choose: ").strip()

    order_columns = {
        "1": "c.name",
        "2": "c.birthday",
        "3": "c.date_added"
    }

    if choice not in order_columns:
        print("invalid choice")
        return

    conn = get_connection()
    cur = conn.cursor()

    query = f"""
        SELECT c.id,
               c.name,
               COALESCE(c.email, ''),
               COALESCE(TO_CHAR(c.birthday, 'DD.MM.YY'), ''),
               COALESCE(g.name, 'Other'),
               TO_CHAR(c.date_added, 'DD.MM.YY HH24:MI')
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY {order_columns[choice]} NULLS LAST
    """

    cur.execute(query)

    rows = cur.fetchall()
    print_rows(rows)

    cur.close()
    conn.close()


def paginated_navigation():
    limit_value = int(input("enter page size: "))
    offset_value = 0

    while True:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM get_contacts_paginated(%s, %s)",
            (limit_value, offset_value)
        )

        rows = cur.fetchall()

        print("\ncurrent page:")
        print_rows(rows)

        cur.close()
        conn.close()

        command = input("next / prev / quit: ").strip().lower()

        if command == "next":
            offset_value += limit_value
        elif command == "prev":
            offset_value -= limit_value

            if offset_value < 0:
                offset_value = 0
        elif command == "quit":
            break
        else:
            print("unknown command")


def export_to_json():
    filename = input("enter json filename: ").strip()

    if filename == "":
        filename = "contacts.json"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name, c.date_added
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.id
    """)

    contacts = cur.fetchall()
    result = []

    for contact in contacts:
        contact_id = contact[0]

        cur.execute(
            "SELECT phone, type FROM phones WHERE contact_id=%s ORDER BY id",
            (contact_id,)
        )

        phone_rows = cur.fetchall()

        result.append({
            "name": contact[1],
            "email": contact[2] or "",
            "birthday": contact[3].strftime("%d.%m.%y") if contact[3] else "",
            "group": contact[4] or "Other",
            "date_added": contact[5].strftime("%d.%m.%y %H:%M") if contact[5] else "",
            "phones": [
                {"phone": p[0], "type": p[1]}
                for p in phone_rows
            ]
        })

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
    except FileNotFoundError:
        print("folder not found. enter another filename")
        cur.close()
        conn.close()
        return

    cur.close()
    conn.close()

    print("export finished")


def import_from_json():
    filename = input("enter json filename: ").strip()

    if filename == "":
        filename = "contacts.json"

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("file not found. choose this option again and enter another filename")
        return

    for item in data:
        name = item.get("name", "").strip()

        if name == "":
            continue

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT 1 FROM contacts WHERE name=%s LIMIT 1",
            (name,)
        )

        exists = cur.fetchone() is not None

        cur.close()
        conn.close()

        overwrite = False

        if exists:
            answer = input(name + " already exists. skip or overwrite? ").strip().lower()

            if answer != "overwrite":
                print("skipped")
                continue

            overwrite = True

        add_contact_to_db(
            name,
            item.get("email", ""),
            item.get("birthday", ""),
            item.get("group", "Other"),
            item.get("phones", []),
            overwrite=overwrite
        )

    print("import finished")


def import_from_csv():
    filename = input("enter csv filename: ").strip()

    if filename == "":
        filename = "contacts.csv"

    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                name = row.get("name", "").strip()

                if name == "":
                    continue

                phone = row.get("phone", "").strip()
                phone_type = row.get("type", "mobile").strip()

                if phone_type not in ["home", "work", "mobile"]:
                    phone_type = "mobile"

                birthday = fix_birthday(row.get("birthday", ""))

                result = add_contact_to_db(
                    name,
                    row.get("email", "").strip(),
                    birthday,
                    row.get("group", "Other").strip(),
                    [{"phone": phone, "type": phone_type}],
                    overwrite=False
                )

                print(name, result)

    except FileNotFoundError:
        print("file not found. choose this option again and enter another filename")
        return

    print("csv import finished")


def add_phone_menu():
    name = input("enter contact name: ").strip()
    phone = input("enter new phone: ").strip()
    phone_type = input("enter type home/work/mobile: ").strip()

    if phone_type not in ["home", "work", "mobile"]:
        phone_type = "mobile"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "CALL add_phone(%s, %s, %s)",
        (name, phone, phone_type)
    )

    conn.commit()

    cur.close()
    conn.close()

    print("phone added")


def move_to_group_menu():
    name = input("enter contact name: ").strip()
    group_name = input("enter new group: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "CALL move_to_group(%s, %s)",
        (name, group_name)
    )

    conn.commit()

    cur.close()
    conn.close()

    print("contact moved")


setup_database_objects()
clear_all_data()

while True:
    print("\n---- tsis1 phonebook ----")
    print("1 - add contact")
    print("2 - add phone to contact")
    print("3 - move contact to group")
    print("4 - search in all fields")
    print("5 - search by email")
    print("6 - filter by group")
    print("7 - sort contacts")
    print("8 - paginated navigation")
    print("9 - export to JSON")
    print("10 - import from JSON")
    print("11 - import from CSV")
    print("12 - show all contacts")
    print("0 - exit")

    choice = input("choose: ").strip()

    if choice == "1":
        add_contact_from_console()
    elif choice == "2":
        add_phone_menu()
    elif choice == "3":
        move_to_group_menu()
    elif choice == "4":
        search_all_fields()
    elif choice == "5":
        search_by_email()
    elif choice == "6":
        filter_by_group()
    elif choice == "7":
        sort_contacts()
    elif choice == "8":
        paginated_navigation()
    elif choice == "9":
        export_to_json()
    elif choice == "10":
        import_from_json()
    elif choice == "11":
        import_from_csv()
    elif choice == "12":
        show_all_contacts()
    elif choice == "0":
        print("goodbye")
        break
    else:
        print("invalid choice")