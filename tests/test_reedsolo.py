import unittest
from reedsolo import RSCodec, ReedSolomonError

try:
    bytearray
except NameError:
    from reedsolo import bytearray


class TestReedSolomon(unittest.TestCase):
    def test_simple(self):
        rs = RSCodec(10)
        msg = b"hello world " * 10
        enc = rs.encode(msg)
        dec = rs.decode(enc)
        self.assertEquals(dec, bytearray(msg))
    
    def test_correction(self):
        rs = RSCodec(10)
        msg = b"hello world " * 10
        enc = rs.encode(msg)
        self.assertEquals(rs.decode(enc), bytearray(msg))
        for i in [27, -3, -9, 7, 0]:
            enc[i] = 99
            self.assertEquals(rs.decode(enc), bytearray(msg))
        enc[82] = 99
        self.assertRaises(ReedSolomonError, rs.decode, enc)
    
    def test_long(self):
        rs = RSCodec(10)
        msg = b"a" * 10000
        enc = rs.encode(msg)
        dec = rs.decode(enc)
        self.assertEquals(dec, bytearray(msg))
        enc[177] = 99
        enc[2212] = 88
        dec2 = rs.decode(enc)
        self.assertEquals(dec2, bytearray(msg))


if __name__ == "__main__":
    unittest.main()
