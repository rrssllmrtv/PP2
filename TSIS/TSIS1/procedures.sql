DROP FUNCTION IF EXISTS search_contacts(TEXT);
DROP FUNCTION IF EXISTS get_contacts_paginated(INT, INT);
DROP PROCEDURE IF EXISTS add_phone(VARCHAR, VARCHAR, VARCHAR);
DROP PROCEDURE IF EXISTS move_to_group(VARCHAR, VARCHAR);


CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
AS $$
DECLARE
    contact_id_value INT;
BEGIN
    SELECT id
    INTO contact_id_value
    FROM contacts
    WHERE name = p_contact_name
    LIMIT 1;

    IF contact_id_value IS NULL THEN
        RETURN;
    END IF;

    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        p_type := 'mobile';
    END IF;

    INSERT INTO phones(contact_id, phone, type)
    VALUES (contact_id_value, p_phone, p_type)
    ON CONFLICT (contact_id, phone) DO NOTHING;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
AS $$
DECLARE
    group_id_value INT;
BEGIN
    IF p_group_name = '' THEN
        p_group_name := 'Other';
    END IF;

    INSERT INTO groups(name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id
    INTO group_id_value
    FROM groups
    WHERE name = p_group_name;

    UPDATE contacts
    SET group_id = group_id_value
    WHERE name = p_contact_name;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id INT,
    name VARCHAR,
    email TEXT,
    birthday TEXT,
    group_name TEXT,
    phones TEXT,
    date_added TEXT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id,
           c.name,
           COALESCE(c.email, '')::TEXT,
           COALESCE(TO_CHAR(c.birthday, 'DD.MM.YY'), '')::TEXT,
           COALESCE(g.name, 'Other')::TEXT,
           COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.id), '')::TEXT,
           TO_CHAR(c.date_added, 'DD.MM.YY HH24:MI')::TEXT
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE c.name ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR g.name ILIKE '%' || p_query || '%'
       OR p.phone ILIKE '%' || p_query || '%'
    GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.date_added
    ORDER BY c.id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_contacts_paginated(
    p_limit INT,
    p_offset INT
)
RETURNS TABLE (
    id INT,
    name VARCHAR,
    email TEXT,
    birthday TEXT,
    group_name TEXT,
    phones TEXT,
    date_added TEXT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id,
           c.name,
           COALESCE(c.email, '')::TEXT,
           COALESCE(TO_CHAR(c.birthday, 'DD.MM.YY'), '')::TEXT,
           COALESCE(g.name, 'Other')::TEXT,
           COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.id), '')::TEXT,
           TO_CHAR(c.date_added, 'DD.MM.YY HH24:MI')::TEXT
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON p.contact_id = c.id
    GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.date_added
    ORDER BY c.id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;