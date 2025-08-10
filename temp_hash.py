import hashlib
password = "salesman"
hashed = hashlib.sha256(password.encode()).hexdigest()
print(f"Hash for 'salesman': {hashed}")
