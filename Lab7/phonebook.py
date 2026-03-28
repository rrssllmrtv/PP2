import csv
from connect import get_connection

def reset_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS contacts")

    conn.commit()
    cur.close()
    conn.close()


def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE contacts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            phone VARCHAR(20) NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

def is_duplicate(name, phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM contacts WHERE name=%s AND phone=%s",
        (name, phone)
    )

    exists = cur.fetchone() is not None

    cur.close()
    conn.close()

    return exists

def clear_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("TRUNCATE TABLE contacts RESTART IDENTITY")

    conn.commit()
    cur.close()
    conn.close()

def insert_from_csv(filename="contacts.csv"):
    conn = get_connection()
    cur = conn.cursor()

    with open(filename, "r") as f:
        reader = csv.reader(f)

        for row in reader:
            if len(row) >= 2:
                name = row[0].strip()
                phone = row[1].strip()

                if not is_duplicate(name, phone):
                    cur.execute(
                        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
                        (name, phone)
                    )

    conn.commit()
    cur.close()
    conn.close()


def insert_from_console():
    name = input("Enter name: ").strip()
    phone = input("Enter phone: ").strip()

    if is_duplicate(name, phone):
        print("Duplicate contact ignored")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()

def show_all_contacts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM contacts ORDER BY id")
    rows = cur.fetchall()

    if not rows:
        print("Phonebook is empty")
    else:
        for row in rows:
            print(row)

    cur.close()
    conn.close()

def search_by_name():
    name = input("Enter name: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM contacts WHERE name ILIKE %s",
        (f"%{name}%",)
    )

    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()


def search_by_phone():
    prefix = input("Enter phone prefix: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM contacts WHERE phone LIKE %s",
        (prefix + "%",)
    )

    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()


def update_name():
    old_name = input("Enter old name: ")
    new_name = input("Enter new name: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE contacts SET name=%s WHERE name=%s",
        (new_name, old_name)
    )

    conn.commit()
    cur.close()
    conn.close()


def update_phone():
    name = input("Enter name: ")
    new_phone = input("Enter new phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE contacts SET phone=%s WHERE name=%s",
        (new_phone, name)
    )

    conn.commit()
    cur.close()
    conn.close()

def delete_contact():
    mode = input("Delete by (1-name / 2-phone): ")

    conn = get_connection()
    cur = conn.cursor()

    if mode == "1":
        name = input("Enter name: ")
        cur.execute("DELETE FROM contacts WHERE name=%s", (name,))
    elif mode == "2":
        phone = input("Enter phone: ")
        cur.execute("DELETE FROM contacts WHERE phone=%s", (phone,))

    conn.commit()
    cur.close()
    conn.close()


def search_menu():
    while True:
        print("\n--- SEARCH ---")
        print("1 - By name")
        print("2 - By phone")
        print("0 - Back")

        c = input("Choose: ")

        if c == "1":
            search_by_name()
        elif c == "2":
            search_by_phone()
        elif c == "0":
            break


def update_menu():
    while True:
        print("\n--- UPDATE ---")
        print("1 - Name")
        print("2 - Phone")
        print("0 - Back")

        c = input("Choose: ")

        if c == "1":
            update_name()
        elif c == "2":
            update_phone()
        elif c == "0":
            break


def delete_menu():
    while True:
        print("\n--- DELETE ---")
        print("1 - Delete contact")
        print("0 - Back")

        c = input("Choose: ")

        if c == "1":
            delete_contact()
        elif c == "0":
            break


reset_table()
create_table()
clear_table()


while True:
    print("\n--- PHONEBOOK ---")
    print("1 - Load from CSV")
    print("2 - Add contact")
    print("3 - Show all")
    print("4 - Search")
    print("5 - Update")
    print("6 - Delete")
    print("0 - Exit")

    choice = input("Your choice: ")

    if choice == "1":
        insert_from_csv()
    elif choice == "2":
        insert_from_console()
    elif choice == "3":
        show_all_contacts()
    elif choice == "4":
        search_menu()
    elif choice == "5":
        update_menu()
    elif choice == "6":
        delete_menu()
    elif choice == "0":
        break