import unittest
from reedsolo import RSCodec
import random

class TestReedSolomon(unittest.TestCase):
    def test_simple(self):
        rs = RSCodec(10)
        msg = "hello world " * 10
        enc = rs.encode(msg)
        dec = rs.decode(enc)
        self.assertEquals(dec, msg)
    
    def test_long(self):
        rs = RSCodec(10)
        msg = "".join(chr(random.randint(0, 255)) for _ in range(100)) * 1000
        enc = rs.encode(msg)
        dec = rs.decode(enc)
        self.assertEquals(dec, msg)
        enc2 = enc[:177] + "X" + enc[178:22177] + "Y" + enc[22178:]
        dec2 = rs.decode(enc2)
        self.assertEquals(dec2, msg)


if __name__ == "__main__":
    unittest.main()
