import unittest
from reedsolo import RSCodec, ReedSolomonError


class TestReedSolomon(unittest.TestCase):
    def test_simple(self):
        rs = RSCodec(10)
        msg = "hello world " * 10
        enc = rs.encode(msg)
        dec = rs.decode(enc)
        self.assertEquals(dec, msg)
    
    def test_correction(self):
        rs = RSCodec(10)
        msg = "hello world " * 10
        enc = rs.encode(msg)
        if hasattr(__builtins__, "bytearray"):
            enc = bytearray(enc)
        else:
            enc = [ord(x) for x in enc]
        self.assertEquals(rs.decode(enc), msg)
        for i in [27, -3, -9, 7, 0]:
            enc[i] = 99
            self.assertEquals(rs.decode(enc), msg)
        enc[82] = 99
        self.assertRaises(ReedSolomonError, rs.decode, enc)
    
    def test_long(self):
        rs = RSCodec(10)
        msg = "a" * 10000
        enc = rs.encode(msg)
        dec = rs.decode(enc)
        self.assertEquals(dec, msg)
        enc2 = enc[:177] + "X" + enc[178:2212] + "Y" + enc[2213:]
        dec2 = rs.decode(enc2)
        self.assertEquals(dec2, msg)


if __name__ == "__main__":
    unittest.main()
