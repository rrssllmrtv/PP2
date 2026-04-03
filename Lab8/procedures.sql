CREATE OR REPLACE PROCEDURE insert_or_update_user(p_name VARCHAR, p_phone VARCHAR)
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM contacts
        WHERE name = p_name
    ) THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE delete_user(p_value VARCHAR)
AS $$
BEGIN
    DELETE FROM contacts
    WHERE name = p_value
       OR phone = p_value;
END;
$$ LANGUAGE plpgsql;