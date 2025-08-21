from app.core import security

pwd = "test123#"
hash = "$2b$12$uTp8EdOJbNm1OoM2g0zRIOrnSpHn4dmGVndzojWRjmwwoVkqNSzae"
# hash = security.hash_password(pwd)

# print(security.verify_password(pwd, hash))

# pwd2 = "test123"
# hash_again = security.hash_password(pwd)
# print(security.verify_password(pwd2, hash_again))

hashed = hash.strip()

print(security.verify_password(pwd, hashed))