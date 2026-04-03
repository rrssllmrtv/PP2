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
    load_sql_file("functions.sql")
    load_sql_file("procedures.sql")


def search_by_pattern():
    pattern = input("enter pattern: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
    rows = cur.fetchall()

    if rows:
        print("\nfound contacts:")
        for row in rows:
            print(row)
    else:
        print("\nnothing found")

    cur.close()
    conn.close()


def insert_or_update_one():
    name = input("enter name: ").strip()
    phone = input("enter phone: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL insert_or_update_user(%s, %s)", (name, phone))
    conn.commit()

    print("\ninsert/update done")

    cur.close()
    conn.close()


def insert_many():
    n = int(input("how many contacts to enter "))

    names = []
    phones = []

    for i in range(n):
        print(f"\ncontact #{i + 1}")
        name = input("enter name: ").strip()
        phone = input("enter phone: ").strip()

        names.append(name)
        phones.append(phone)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM insert_many_users(%s, %s)", (names, phones))
    bad_rows = cur.fetchall()
    conn.commit()

    print("\nbulk insert/update finished")

    if bad_rows:
        print("\nincorrect data:")
        for row in bad_rows:
            print(row)
    else:
        print("all contacts were processed successfully")

    cur.close()
    conn.close()


def show_paginated():
    limit_value = int(input("enter limit: "))
    offset_value = int(input("enter offset: "))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM get_contacts_paginated(%s, %s)",
        (limit_value, offset_value)
    )
    rows = cur.fetchall()

    if rows:
        print("\ncontacts:")
        for row in rows:
            print(row)
    else:
        print("\nno contacts for this page")

    cur.close()
    conn.close()


def delete_by_name_or_phone():
    value = input("enter username or phone to delete: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL delete_user(%s)", (value,))
    conn.commit()

    print("\ndeleted")

    cur.close()
    conn.close()


def show_all_contacts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM contacts ORDER BY id")
    rows = cur.fetchall()

    if rows:
        print("\nall contacts:")
        for row in rows:
            print(row)
    else:
        print("\ntable is empty")

    cur.close()
    conn.close()


setup_database_objects()

while True:
    print("\n---- phonebook with functions and procedures ----")
    print("1 - search by pattern")
    print("2 - insert or update one user")
    print("3 - insert many users")
    print("4 - show contacts with pagination")
    print("5 - delete by username or phone")
    print("6 - show all contacts")
    print("0 - exit")

    choice = input("choose: ").strip()

    if choice == "1":
        search_by_pattern()
    elif choice == "2":
        insert_or_update_one()
    elif choice == "3":
        insert_many()
    elif choice == "4":
        show_paginated()
    elif choice == "5":
        delete_by_name_or_phone()
    elif choice == "6":
        show_all_contacts()
    elif choice == "0":
        print("goodbye")
        break
    else:
        print("invalid choice")