import unittest
from reedsolo import RSCodec, ReedSolomonError


class TestReedSolomon(unittest.TestCase):
    def test_simple(self):
        rs = RSCodec(10)
        msg = b"hello world " * 10
        enc = rs.encode(msg)
        dec = rs.decode(enc)
        self.assertEquals(dec, msg)
    
    def test_correction(self):
        rs = RSCodec(10)
        msg = b"hello world " * 10
        enc = rs.encode(msg)
        self.assertEquals(rs.decode(enc), msg)
        for i in [27, -3, -9, 7, 0]:
            enc[i] = 99
            self.assertEquals(rs.decode(enc), msg)
        enc[82] = 99
        self.assertRaises(ReedSolomonError, rs.decode, enc)
    
    def test_long(self):
        rs = RSCodec(10)
        msg = b"a" * 10000
        enc = rs.encode(msg)
        dec = rs.decode(enc)
        self.assertEquals(dec, msg)
        enc[177] = 99
        enc[2212] = 88
        dec2 = rs.decode(enc)
        self.assertEquals(dec2, msg)


if __name__ == "__main__":
    unittest.main()
