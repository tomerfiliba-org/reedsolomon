import unittest
import sys
from random import sample
from reedsolo import RSCodec, ReedSolomonError

try:
    bytearray
except NameError:
    from reedsolo import bytearray


class TestReedSolomon(unittest.TestCase):
    def test_simple(self):
        rs = RSCodec(10)
        msg = bytearray("hello world " * 10, "utf8")
        enc = rs.encode(msg)
        dec = rs.decode(enc)
        self.assertEqual(dec, msg)
    
    def test_correction(self):
        rs = RSCodec(10)
        msg = bytearray("hello world " * 10, "utf8")
        enc = rs.encode(msg)
        self.assertEqual(rs.decode(enc), msg)
        for i in [27, -3, -9, 7, 0]:
            enc[i] = 99
            self.assertEqual(rs.decode(enc), msg)
        enc[82] = 99
        self.assertRaises(ReedSolomonError, rs.decode, enc)
    
    def test_long(self):
        rs = RSCodec(10)
        msg = bytearray("a" * 10000, "utf8")
        enc = rs.encode(msg)
        dec = rs.decode(enc)
        self.assertEqual(dec, msg)
        enc[177] = 99
        enc[2212] = 88
        dec2 = rs.decode(enc)
        self.assertEqual(dec2, msg)
        
    def test_prim_fcr_basic(self):
        nn = 30
        kk = 18
        tt = nn - kk
        rs = RSCodec(tt, fcr=120, prim=0x187)
        hexencmsg = '00faa123555555c000000354064432c02800fe97c434e1ff5365' \
            'cf8fafe4'
        strf = str if sys.version_info[0] >= 3 else unicode    
        encmsg = bytearray.fromhex(strf(hexencmsg))
        decmsg = encmsg[:kk]
        tem = rs.encode(decmsg)
        self.assertEqual(encmsg, tem, msg="encoded does not match expected")
        tdm = rs.decode(tem)
        self.assertEqual(tdm, decmsg, msg="decoded does not match original")
        tem1 = bytearray(tem) # clone a copy
        # encoding and decoding intact message seem OK, so test errors
        numerrs = tt >> 1 # inject tt/2 errors (expected to recover fully)
        for i in sample(range(nn), numerrs): # inject errors in random places
            tem1[i] ^= 0xff # flip all 8 bits
        tdm = rs.decode(tem1)
        self.assertEqual(tdm, decmsg,
            msg="decoded with errors does not match original")
        tem1 = bytearray(tem) # clone another copy
        numerrs += 1 # inject tt/2 + 1 errors (expected to fail and detect it)
        for i in sample(range(nn), numerrs): # inject errors in random places
            tem1[i] ^= 0xff # flip all 8 bits
        # if this fails, it means excessive errors not detected
        self.assertRaises(ReedSolomonError, rs.decode, tem1)

    def test_prim_fcr_long(self):
        nn = 48
        kk = 34
        tt = nn - kk
        rs = RSCodec(tt, fcr=120, prim=0x187)
        hexencmsg = '08faa123555555c000000354064432c0280e1b4d090cfc04887400' \
            '000003500000000e1985ff9c6b33066ca9f43d12e8'
        strf = str if sys.version_info[0] >= 3 else unicode    
        encmsg = bytearray.fromhex(strf(hexencmsg))
        decmsg = encmsg[:kk]
        tem = rs.encode(decmsg)
        self.assertEqual(encmsg, tem, msg="encoded does not match expected")
        tdm = rs.decode(tem)
        self.assertEqual(tdm, decmsg, 
            msg="decoded does not match original")
        tem1 = bytearray(tem)
        numerrs = tt >> 1
        for i in sample(range(nn), numerrs):
            tem1[i] ^= 0xff
        tdm = rs.decode(tem1)
        self.assertEqual(tdm, decmsg,
            msg="decoded with errors does not match original")
        tem1 = bytearray(tem)
        numerrs += 1
        for i in sample(range(nn), numerrs):
            tem1[i] ^= 0xff
        self.assertRaises(ReedSolomonError, rs.decode, tem1)

if __name__ == "__main__":
    unittest.main()
