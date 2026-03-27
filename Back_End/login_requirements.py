def checkcolnames(cursor):
    query = '''
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = (%s)
            AND TABLE_SCHEMA = (%s)
            '''
    cursor.execute(query, ('user_priv_info', 'healthsys')) 
    return [row[0] for row in cursor.fetchall()]

def id_requirements(cursor, id: str):
    '''
    1. id has to be new one
    2. length is between 8 and 20
    3. id should contain alphabets(English, MUST HAVE), numbers or _
    '''
    # Step 1 #
    cursor.execute("SELECT 1 FROM user_priv_info WHERE user_id = %s", (id,))
    existing = cursor.fetchone()

    if existing is not None:
        return f"Sorry, the ID {id} is already taken."

    # Step 2 #
    if len(id) < 8 or len(id) > 20:
        return "id should consist of 8~20 characters"

    # Step 3 #
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    for ch in id:
        if ch not in allowed_chars:
            return f"{ch} is not valid character for id"

    return None

def pw_requirements(pw: str):
    '''
    1. length is between 8 and 20
    2. pw should be a mixture of alphabets(English), numbers, and special characters
    '''
    # Step 1 #
    if len(pw) < 8 or len(pw) > 20:
        return "pw should consist of 8~20 characters"

    # Step 2 #
    alphabets = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numbers = "0123456789"
    special_characters = "!@#$%^&*()-_=+[]|;:,.<>}{?/"

    has_alpha = any(c in alphabets for c in pw)
    has_number = any(c in numbers for c in pw)
    has_special = any(c in special_characters for c in pw)

    if not (has_alpha and has_number and has_special):
        return "Password must include letters, numbers, and special characters"

    return None
