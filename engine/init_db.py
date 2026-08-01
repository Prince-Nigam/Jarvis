import csv
import os
import re
import sqlite3

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jarvis.db"
)

# contacts.csv expected location (project root)
CONTACTS_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "contacts.csv"
)


def _clean_phone(number: str) -> str:
    """Strip spaces, dashes from phone number. Keep leading +."""
    if not number:
        return ""
    cleaned = re.sub(r"[\s\-()]", "", number)
    return cleaned


def _build_name(row: dict) -> str:
    """
    Build a full name from Google Contacts CSV columns.
    Uses 'First Name', 'Middle Name', 'Last Name' if available.
    """
    parts = [
        row.get("First Name", "").strip(),
        row.get("Middle Name", "").strip(),
        row.get("Last Name", "").strip(),
    ]
    name = " ".join(p for p in parts if p)
    return name


def init_database():
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS sys_command("
        "id INTEGER PRIMARY KEY, name VARCHAR(100), path VARCHAR(1000))"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS web_command("
        "id INTEGER PRIMARY KEY, name VARCHAR(100), url VARCHAR(1000))"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS contacts("
        "id INTEGER PRIMARY KEY, name VARCHAR(200), "
        "mobile_no VARCHAR(255), email VARCHAR(255))"
    )

    # Seed default web commands
    defaults = [
        ("youtube", "https://www.youtube.com/"),
        ("whatsapp", "https://web.whatsapp.com/"),
        ("google", "https://www.google.com/"),
    ]
    for name, url in defaults:
        cursor.execute("SELECT 1 FROM web_command WHERE name = ?", (name,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO web_command (name, url) VALUES (?, ?)", (name, url)
            )

    # Auto-import contacts from contacts.csv if it exists
    _import_contacts_from_csv(cursor)

    con.commit()
    con.close()


def _import_contacts_from_csv(cursor):
    """
    Import contacts from Google Contacts exported CSV.
    Supports both simple format (name, mobile_no, email)
    and Google Contacts export format (First Name, Middle Name, Last Name, Phone 1 - Value, etc.)
    Skips duplicates based on mobile_no.
    """
    if not os.path.exists(CONTACTS_CSV):
        return

    try:
        with open(CONTACTS_CSV, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames or []
            imported = 0

            for row in reader:
                # ── Determine name ──────────────────────────────────────────
                if "name" in headers:
                    # Simple format
                    name = row.get("name", "").strip()
                else:
                    # Google Contacts format
                    name = _build_name(row)

                # ── Determine phone ─────────────────────────────────────────
                if "mobile_no" in headers:
                    mobile_no = _clean_phone(row.get("mobile_no", ""))
                else:
                    # Google Contacts format — find first phone column
                    phone_cols = [h for h in headers if "Phone" in h and "Value" in h]
                    mobile_no = ""
                    for col in phone_cols:
                        val = _clean_phone(row.get(col, ""))
                        if val:
                            mobile_no = val
                            break

                # ── Determine email ─────────────────────────────────────────
                if "email" in headers:
                    email = row.get("email", "").strip()
                else:
                    email_cols = [h for h in headers if "E-mail" in h and "Value" in h]
                    email = row.get(email_cols[0], "").strip() if email_cols else ""

                if not name or not mobile_no:
                    continue  # skip incomplete rows

                # Add +91 prefix if missing for Indian numbers
                if not mobile_no.startswith("+") and len(mobile_no) == 10:
                    mobile_no = "+91" + mobile_no

                # Skip if already exists
                cursor.execute(
                    "SELECT 1 FROM contacts WHERE mobile_no = ?", (mobile_no,)
                )
                if cursor.fetchone():
                    continue

                cursor.execute(
                    "INSERT INTO contacts (name, mobile_no, email) VALUES (?, ?, ?)",
                    (name, mobile_no, email),
                )
                imported += 1

        if imported > 0:
            print(f"[DB] Imported {imported} new contacts from contacts.csv")
    except Exception as e:
        print(f"[DB] Could not import contacts.csv: {e}")
