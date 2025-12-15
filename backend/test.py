# Test 1: Create HS256 token
from jose import jwt

hs256_token = jwt.encode({"sub": "test"}, "secret", algorithm="HS256")
print(f"HS256 Token: {hs256_token}")

# Test 2: Try to decode with RS256 only
try:
    payload = jwt.decode(hs256_token, "secret", algorithms=["RS256"])
    print("✗ UNEXPECTED: HS256 token verified with RS256!")
except Exception as e:
    print(f"✓ EXPECTED: {e}")

# Test 3: Try to decode with HS256 only
try:
    payload = jwt.decode(hs256_token, "secret", algorithms=["HS256"])
    print("✓ EXPECTED: HS256 token verified with HS256")
except Exception as e:
    print(f"✗ UNEXPECTED: {e}")