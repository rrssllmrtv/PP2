CREATE OR REPLACE FUNCTION search_contacts(pattern_text TEXT)
RETURNS TABLE (
    id INT,
    name VARCHAR,
    phone VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.phone
    FROM contacts c
    WHERE c.name ILIKE '%' || pattern_text || '%'
       OR c.phone ILIKE '%' || pattern_text || '%'
    ORDER BY c.id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION insert_many_users(p_names TEXT[], p_phones TEXT[])
RETURNS TABLE (
    bad_name TEXT,
    bad_phone TEXT
)
AS $$
DECLARE
    i INT;
    current_name TEXT;
    current_phone TEXT;
BEGIN
    IF array_length(p_names, 1) IS NULL OR array_length(p_phones, 1) IS NULL THEN
        RETURN;
    END IF;

    FOR i IN 1 .. LEAST(array_length(p_names, 1), array_length(p_phones, 1))
    LOOP
        current_name := trim(p_names[i]);
        current_phone := trim(p_phones[i]);

        IF current_phone ~ '^[0-9]+$' THEN
            IF EXISTS (
                SELECT 1
                FROM contacts
                WHERE name = current_name
            ) THEN
                UPDATE contacts
                SET phone = current_phone
                WHERE name = current_name;
            ELSE
                INSERT INTO contacts(name, phone)
                VALUES (current_name, current_phone);
            END IF;
        ELSE
            bad_name := current_name;
            bad_phone := current_phone;
            RETURN NEXT;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE (
    id INT,
    name VARCHAR,
    phone VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.phone
    FROM contacts c
    ORDER BY c.id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;