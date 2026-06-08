"""Decode the JetHop token structure"""
import base64

s = 'IwY2xjawSIaL1leHRuA2FlbQIxMABicmlkETF1WkY1dHhzSUI2RDJENVdjc3J0YwZhcHBfaWQQMjIyMDM5MTc4ODIwMDg5MgABHl9qNSZ_b6rYfI_rp_cgWhvM3FNZCo00YdNEwFtWZg0mqrIynjnxzhYXDEEJ_aem_l0nEyBchyVNXwwajUfKs9w'

# Split by possible base64-decodable chunks (4 chars each)
decoded_parts = []
for i in range(0, len(s) - len(s)%4, 4):
    chunk = s[i:i+4]
    c_std = chunk.replace('_', '/').replace('-', '+')
    try:
        data = base64.b64decode(c_std)
        printable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
        decoded_parts.append((chunk, data, printable))
    except:
        pass

for i, (chunk, data, printable) in enumerate(decoded_parts):
    print(f'{i:3d}: [{chunk}] -> [{printable}] ({len(data)} bytes)')

print()
# Full decode with proper padding
s2 = s.replace('_', '/').replace('-', '+')
rem = len(s2) % 4
if rem:
    s2 += '=' * (4 - rem)
    
data = base64.b64decode(s2)
print(f'Full decode ({len(data)} bytes):')
hex_str = data.hex()
for i in range(0, len(hex_str), 80):
    print(hex_str[i:i+80])

# Check first few bytes
print(f'\nFirst byte: 0x{data[0]:02x}')
val = int.from_bytes(data[1:5], 'big')
print(f'Bytes 1-4 as int: {val}')

# Look for field-length-value pattern
for i in range(0, min(len(data), 80), 5):
    if i + 5 <= len(data):
        t = data[i]
        ln = data[i+1]
        dv = data[i+2:i+2+ln] if ln <= 3 else data[i+2:i+5]
        print(f'  offset {i}: type=0x{t:02x} len={ln} data={dv.hex()}')
