import hashlib
import os

# RFC 3526 Group 14, 2048-bit MODP Group
P_HEX = """
    FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1
    29024E08 8A67CC74 020BBEA6 3B139B22 514A0879 8E3404DD
    EF9519B3 CD3A431B 302B0A6D F25F1437 4FE1356D 6D51C245
    E485B576 625E7EC6 F44C42E9 A637ED6B 0BFF5CB6 F406B7ED
    EE386BFB 5A899FA5 AE9F2411 7C4B1FE6 49286651 ECE45B3D
    C2007CB8 A163BF05 98DA4836 1C55D39A 69163FA8 FD24CF5F
    83655D23 DCA3AD96 1C62F356 208552BB 9ED52907 7096966D
    670C354E 4ABC9804 F1746C08 CA18217C 32905E46 2E36CE3B
    E39E00D8 21166826 0B0BD23F 73C12912 6116755D CE73A2FA
    82234892 092413F6 43961A2C 33417C20 EF14A720 02710443
    52477161 39430219 191B1F12 328ED848 98C10840 4B406A21
    7E717F02 E1059097 0C2D5CD2 5301D89B AD30A697 A21C0ECA
    335198B0 3BB5E5D1 EAD06B1F 6941A595 9C524BAF 4A42A12D
    D7A0266B 404E071A 04130EE4 D696E7C9 7355B6F0 782E7D14
    B7443D39 1A291A76 444414D0 99D45222 3D8A65CB 5E2F4119
    FF431FF5 EE893C40 35472093 07F1C19F AD292742 137644C4
    329F9171 305D9737 3C6F8602 E1B464F2 51E1681B 09880B6B
    177A23D1 94B4D789 61D02A91 D9049487 6F87D380 D6898BD3
    4286121D 5A6D8866 5181F877 8C5389E0 60E661C0 21EAF493
    45474D1C 3432C7CD 4A2C46C9 D1177692 B8558A4D 0074212F
    57406BB8 561C6295 6795B409 C0632349 E043B426 E8373418
    70DB29D3 7A811808 D5B1FFC8 E05F8652 D7F056A4 95E92341
    E8B92857 C452424F 2A145C83 43D56064 E978564F 4CC3379D
    363F3254 B4B18461 719B53A4 7008129C 39464619 B2732959
    1667A7D7 E9F46A1A 7D17D911 854D2027 D60D6442 65C96728
    B3E3ED4D 3636F833 50284D87 295191C8 FD2943A7 C157C475
    0A36D611 EDF718D8 79C5C384 1C526F67 6B7C37A3 39B27878
    FFFFFFFF FFFFFFFF
"""
P = int(P_HEX.replace(" ", "").replace("\n", ""), 16)
G = 2

def generate_dh_keys():
    private_key = int.from_bytes(os.urandom(256), 'big') % (P - 1) + 1
    public_key = pow(G, private_key, P)
    return private_key, public_key

def compute_shared_secret(private_key, partner_public_key):
    shared_secret_int = pow(partner_public_key, private_key, P)
    return hashlib.sha256(str(shared_secret_int).encode()).digest()

def _xor_cipher(data, key, nonce):
    res = bytearray()
    for i in range(len(data)):
        # Include nonce in the hash to ensure unique keystream per message
        keystream_byte = hashlib.sha256(key + nonce + i.to_bytes(4, 'big')).digest()[0]
        res.append(data[i] ^ keystream_byte)
    return res

def encrypt(message, shared_secret):
    if shared_secret is None:
        return message
    nonce = os.urandom(16)
    data = message.encode()
    encrypted_bytes = _xor_cipher(data, shared_secret, nonce)
    # Prepend nonce to the ciphertext
    return (nonce + encrypted_bytes).hex()

def decrypt(ciphertext_hex, shared_secret):
    if shared_secret is None:
        return ciphertext_hex
    try:
        raw_data = bytes.fromhex(ciphertext_hex)
        if len(raw_data) < 16:
            return ciphertext_hex
        nonce = raw_data[:16]
        data = raw_data[16:]
        decrypted_bytes = _xor_cipher(data, shared_secret, nonce)
        return decrypted_bytes.decode()
    except Exception:
        return ciphertext_hex
