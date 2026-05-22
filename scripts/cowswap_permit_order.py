from eth_utils import keccak, to_bytes, to_hex
from eth_keys import keys
from eth_account import Account
import requests, json, time

KEY = '0x76f99c0ecad9c0b52d30764326acdd5cf2540b9f3af36276d023890fe1a04550'
ADDR = '0xD0366D78055b8c637c44d769D1A1371106d13552'
pk = keys.PrivateKey(bytes.fromhex(KEY[2:]))

SETTLEMENT = '0x9008D19f58AAbD9eD0D60971565AA8510560ab41'
VAULT_RELAYER = '0xC92E8bdf79f0507f65a392b0ab4667716BFE0110'
USDC = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
WETH = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
CHAIN_ID = 1

ap = lambda a: bytes.fromhex(a[2:].lower()).rjust(32, b'\x00')

# ============================================================
# STEP 1: Sign USDC EIP-2612 permit for VaultRelayer
# ============================================================
print("=== STEP 1: Sign USDC EIP-2612 Permit ===")

# USDC permit domain
# USDC on mainnet: name="USD Coin", version="2"
usdc_domain_sep = keccak(
    keccak(to_bytes(text='EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)')) +
    keccak(to_bytes(text='USD Coin')) +
    keccak(to_bytes(text='2')) +
    (1).to_bytes(32, 'big') +
    ap(USDC)
)
print('USDC domain separator:', '0x' + usdc_domain_sep.hex())

# PERMIT_TYPEHASH
permit_type_hash = keccak(to_bytes(text='Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)'))
print('PERMIT_TYPEHASH:', '0x' + permit_type_hash.hex())

# Permit values
owner = ADDR
spender = VAULT_RELAYER
value = 2**256 - 1  # max uint256 (unlimited approval through permit)
nonce = 0  # we verified nonces[ADDR] = 0 earlier
deadline = 9999999999  # far future

# Compute permit digest = keccak256(\\x19\\x01 ++ domainSeparator ++ hashStruct(permit))
permit_struct_hash = keccak(
    permit_type_hash +
    ap(owner) + ap(spender) +
    value.to_bytes(32, 'big') +
    nonce.to_bytes(32, 'big') +
    deadline.to_bytes(32, 'big')
)
permit_digest = keccak(b'\x19\x01' + usdc_domain_sep + permit_struct_hash)
print('Permit digest:', '0x' + permit_digest.hex())

# Sign the permit
permit_sig = pk.sign_msg_hash(permit_digest)
v = permit_sig.v
r = permit_sig.r.to_bytes(32, 'big')
s = permit_sig.s.to_bytes(32, 'big')
print(f'Permit signature: v={v}, r=0x{r.hex()}, s=0x{s.hex()}')

# Build permit callData for USDC.permit()
# function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s)
# selector = keccak256("permit(address,address,uint256,uint256,uint8,bytes32,bytes32)")[:4]
permit_selector = keccak(to_bytes(text='permit(address,address,uint256,uint256,uint8,bytes32,bytes32)'))[:4]
permit_callData = (
    permit_selector +
    ap(owner) + ap(spender) +
    value.to_bytes(32, 'big') +
    deadline.to_bytes(32, 'big') +
    bytes([0] * 31 + [v]) +  # uint8 padded to 32 bytes
    r + s
)
print('Permit callData length:', len(permit_callData))
assert len(permit_callData) == 4 + 32*7  # 4 bytes selector + 7 * 32 bytes args

# ============================================================
# STEP 2: Build appData JSON with hooks
# ============================================================
print("\n=== STEP 2: Build appData with hooks ===")

appData = {
    "appCode": "YaqeenBot",
    "metadata": {
        "hooks": {
            "pre": [
                {
                    "callData": '0x' + permit_callData.hex(),
                    "gasLimit": "80000",
                    "target": USDC
                }
            ]
        }
    },
    "version": "1.0.0"
}
appData_json = json.dumps(appData, separators=(',', ':'), sort_keys=False)
# Also compute with alphabetically sorted keys (like SDK's stringifyDeterministic)
appData_json_sorted = json.dumps(appData, separators=(',', ':'), sort_keys=True)
print('Sorted appData JSON:', appData_json_sorted[:200] + '...')
appData_hash = keccak(to_bytes(text=appData_json_sorted))
appData_hash = keccak(to_bytes(text=appData_json))
print('appData Hash:', '0x' + appData_hash.hex())
print('appData JSON:', appData_json[:200] + '...')

# ============================================================
# STEP 3: Upload appData to API
# ============================================================
print("\n=== STEP 3: Upload appData to API ===")

app_data_hash_hex = '0x' + appData_hash.hex()
upload_r = requests.put(f'https://api.cow.fi/mainnet/api/v1/app_data/{app_data_hash_hex}',
    json={'fullAppData': appData_json},
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
print(f'Upload appData status: {upload_r.status_code}')
if upload_r.status_code not in (200, 201):
    print('Upload response:', upload_r.text[:300])

# ============================================================
# STEP 4: Get quote with appData hash
# ============================================================
print("\n=== STEP 4: Get Quote ===")

quote_r = requests.post('https://api.cow.fi/mainnet/api/v1/quote', json={
    'sellToken': USDC, 'buyToken': WETH,
    'sellAmountBeforeFee': '2140000',
    'kind': 'sell',
    'from': ADDR, 'receiver': ADDR,
    'validFor': 1800,
    'signingScheme': 'eip712',
    'appData': app_data_hash_hex,  # Use hash after uploading
}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)

if quote_r.status_code != 200:
    print('Quote error:', quote_r.status_code)
    print(quote_r.text[:500])
    exit(1)

q = quote_r.json()['quote']
sell = str(int(q['sellAmount']) + int(q['feeAmount']))
buy = str(int(int(q['buyAmount']) * 0.995))
valid_to = q['validTo']
quote_id = quote_r.json().get('id', None)
print('Quote received: sell', sell, 'buy', buy)
print('Using appDataHash:', app_data_hash_hex)

# ============================================================
# STEP 5: Sign the order with corrected type hash
# ============================================================
print("\n=== STEP 5: Sign Order ===")

# CORRECT ORDER_TYPE_HASH (uses string not bytes32 for kind, sellTokenBalance, buyTokenBalance)
order_type_hash = keccak(to_bytes(text='Order(address sellToken,address buyToken,address receiver,uint256 sellAmount,uint256 buyAmount,uint32 validTo,bytes32 appData,uint256 feeAmount,string kind,bool partiallyFillable,string sellTokenBalance,string buyTokenBalance)'))
kind_hash = keccak(to_bytes(text='sell'))
erc20_hash = keccak(to_bytes(text='erc20'))
app_data_hash_bytes = bytes.fromhex(app_data_hash_hex[2:])

# Build order struct hash
order_encoded = (
    order_type_hash +
    ap(USDC) + ap(WETH) + ap(ADDR) +
    int(sell).to_bytes(32, 'big') +
    int(buy).to_bytes(32, 'big') +
    valid_to.to_bytes(32, 'big') +
    app_data_hash_bytes +
    (0).to_bytes(32, 'big') +  # feeAmount = 0
    kind_hash +
    b'\x00' * 31 + b'\x00' +  # partiallyFillable = false
    erc20_hash + erc20_hash
)
order_digest = keccak(order_encoded)

# EIP-712 digest
domain_sep = keccak(
    keccak(to_bytes(text='EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)')) +
    keccak(to_bytes(text='Gnosis Protocol')) +
    keccak(to_bytes(text='v2')) +
    (CHAIN_ID).to_bytes(32, 'big') +
    ap(SETTLEMENT)
)
digest = keccak(b'\x19\x01' + domain_sep + order_digest)

order_sig = pk.sign_msg_hash(digest)
order_sig_hex = '0x' + order_sig.to_bytes().hex()
print('Order signature:', order_sig_hex[:50] + '...')

# ============================================================
# STEP 6: Submit order (with both appData JSON + appDataHash)
# ============================================================
print("\n=== STEP 6: Submit Order ===")

# SDK pattern: upload appData first, then submit with both fullAppData and appDataHash
order_payload = {
    'sellToken': USDC,
    'buyToken': WETH,
    'receiver': ADDR,
    'sellAmount': sell,
    'buyAmount': buy,
    'validTo': valid_to,
    'appData': appData_json,  # full JSON as signed in the SDK
    'appDataHash': app_data_hash_hex,  # hash alongside
    'feeAmount': '0',
    'kind': 'sell',
    'partiallyFillable': False,
    'sellTokenBalance': 'erc20',
    'buyTokenBalance': 'erc20',
    'signingScheme': 'eip712',
    'signature': order_sig_hex,
    'from': ADDR,
    'owner': ADDR,
}
if quote_id:
    order_payload['quoteId'] = quote_id

r = requests.post('https://api.cow.fi/mainnet/api/v1/orders', json=order_payload,
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)

print('Submit status:', r.status_code)
if r.status_code == 201:
    result = r.json()
    print('SUCCESS!')
    print('Order UID:', result.get('uid', '?'))
    print('Full response:', json.dumps(result, indent=2)[:500])
else:
    print('Error:', r.text[:1000])
