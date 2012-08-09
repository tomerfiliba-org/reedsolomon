import unittest
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


if __name__ == "__main__":
    unittest.main()
