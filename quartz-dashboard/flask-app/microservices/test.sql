SELECT AES_ENCRYPT('mytext','mykeystring', '', 'hkdf', 'salt', 'info'), 
        AES_ENCRYPT('mytext','mykeystring', '', 'pbkdf2_hmac','salt', '2000'), 
        MD5('abc');