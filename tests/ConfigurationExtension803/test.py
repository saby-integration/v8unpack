from base64 import b64decode
import hashlib

with open('./tmp/decode_stage_1/54477ae0-e46e-466a-b7b2-629b261e2ff4', 'rb') as file:
    a = file.read()

b = hashlib.sha1(a).digest().hex()
pass