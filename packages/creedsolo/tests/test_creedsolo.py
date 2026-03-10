# To use this script easily (starting with Python 2.7), just cd to the parent folder and type the following command:
# python -m unittest discover tests

from __future__ import print_function

import unittest
import sys
from random import sample
import itertools
try:
    from itertools import izip
except ImportError:  #python3.x
    izip = zip

try:
    ModuleNotFoundError
except:  # python2.x does not have ModuleNotFoundError
    ModuleNotFoundError = ImportError

# Test whether we use Python 2 or 3
if sys.version_info >= (3, 0):
    PY3 = True
else:
    PY3 = False

# Test if we are running inside Pypy interpreter (incompatible with Cython)
inpypy = True
if PY3:
    # If Python 3, we can't just import __pypy__ to check if there is an ImportError, because it raises a ModuleNotFoundError on Travis CI that is never caught, dunno why
    # So we test manually without raising any exception
    import platform, os
    inpypy = platform.python_implementation().lower().startswith("pypy")

    # BUT if we are running inside Travis, we skip in all cases, because they put very hard limits on cython so that it's very hard for complex code to run properly
    # see also https://github.com/cython/cython/issues/2247
    # TODO: fix me, maybe we can configure travis to set a higher limit for recursion? Or there is really something wrong with the `from creedsolo import *`, but it works on local computer, so it seems to be specific to Travis
    is_travis = 'TRAVIS' in os.environ
    if is_travis:
        inpypy = True
else:
    # Python 2 way to test
    try:
        import __pypy__
    except (ImportError, ModuleNotFoundError, Exception) as exc:  # TODO: on Travis, ModuleNotFoundError cannot be caught, dunno why, so we catch all Exception and consider this means pypy is not running
        inpypy = False

cython_available = True
try:
    # If Cython is installed, try to import it to see if it works
    from Cython.Build import cythonize
except ImportError:
    # Otherwise, we skip this whole test
    cython_available = False

# Skip this whole module test if running under PyPy (incompatible with Cython)
if inpypy or not cython_available:
    # Empty test unit to show the reason of skipping
    class TestMissingDependency(unittest.TestCase):
        @unittest.skip('Missing dependency - Cython missing or PyPy present (Cython is incompatible with PyPy)')
        def test_fail():
            pass

# Else we're not under PyPy, we can run the test
else:
    __pypy__ = None

    creedsolo_exists = False
    try:
        from creedsolo import *
        creedsolo_exists = True
    except Exception:
        pass

    if not creedsolo_exists:  # skip for compatibility with Python 2.7
        # Empty test unit to show the reason of skipping
        class TestMissingDependency(unittest.TestCase):
            @unittest.skip('Missing dependency - Cython missing or PyPy present (Cython is incompatible with PyPy)')
            def test_fail():
                pass

    else:
        try:
            bytearray
        except NameError:
            from creedsolo import bytearray

        import array

        try: # compatibility with Python 3+
            xrange
        except NameError:
            xrange = range

        try:  # python2.x
            from StringIO import StringIO
        except ImportError:
            from io import StringIO


        class cTestReedSolomon(unittest.TestCase):
            def test_simple(self):
                rs = RSCodec(10)
                msg = bytearray("hello world " * 10, "latin1")
                enc = rs.encode(msg)
                dec, dec_enc, errata_pos = rs.decode(enc)
                self.assertEqual(dec, msg)
                self.assertEqual(dec_enc, enc)

            def test_correction(self):
                rs = RSCodec(10)
                msg = bytearray("hello world " * 10, "latin1")
                enc = rs.encode(msg)
                rmsg, renc, errata_pos = rs.decode(enc)
                self.assertEqual(rmsg, msg)
                self.assertEqual(renc, enc)
                for i in [27, -3, -9, 7, 0]:
                    enc[i] = 99
                    rmsg, renc, errata_pos = rs.decode(enc)
                    self.assertEqual(rmsg, msg)
                enc[82] = 99
                self.assertRaises(ReedSolomonError, rs.decode, enc)

            def test_check(self):
                rs = RSCodec(10)
                msg = bytearray("hello world " * 10, "latin1")
                enc = rs.encode(msg)
                rmsg, renc, errata_pos = rs.decode(enc)
                self.assertEqual(rs.check(enc), [True])
                self.assertEqual(rs.check(renc), [True])
                for i in [27, -3, -9, 7, 0]:
                    enc[i] = 99
                    rmsg, renc, errata_pos = rs.decode(enc)
                    self.assertEqual(rs.check(enc), [False])
                    self.assertEqual(rs.check(renc), [True])

            def test_long(self):
                rs = RSCodec(10)
                msg = bytearray("a" * 10000, "latin1")
                enc = rs.encode(msg)
                dec, dec_enc, errata_pos = rs.decode(enc)
                self.assertEqual(dec, msg)
                self.assertEqual(dec_enc, enc)
                enc2 = bytearray(enc)  # make a copy
                enc2[177] = 99
                enc2[2212] = 88
                dec2, dec_enc2, errata_pos = rs.decode(enc2)
                self.assertEqual(dec2, msg)
                self.assertEqual(dec_enc2, enc)

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
                tdm, rtem, errata_pos = rs.decode(tem)
                self.assertEqual(tdm, decmsg, msg="decoded does not match original")
                self.assertEqual(rtem, tem, msg="decoded mesecc does not match original")
                tem1 = bytearray(tem) # clone a copy
                # encoding and decoding intact message seem OK, so test errors
                numerrs = tt >> 1 # inject tt/2 errors (expected to recover fully)
                for i in sample(range(nn), numerrs): # inject errors in random places
                    tem1[i] ^= 0xff # flip all 8 bits
                tdm, _, _ = rs.decode(tem1)
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
                tdm, rtem, errata_pos = rs.decode(tem)
                self.assertEqual(tdm, decmsg, 
                    msg="decoded does not match original")
                self.assertEqual(rtem, tem, 
                    msg="decoded mesecc does not match original")
                tem1 = bytearray(tem)
                numerrs = tt >> 1
                for i in sample(range(nn), numerrs):
                    tem1[i] ^= 0xff
                tdm, rtem, errata_pos = rs.decode(tem1)
                self.assertEqual(tdm, decmsg,
                    msg="decoded with errors does not match original")
                self.assertEqual(rtem, tem,
                    msg="decoded mesecc with errors does not match original")
                tem1 = bytearray(tem)
                numerrs += 1
                for i in sample(range(nn), numerrs):
                    tem1[i] ^= 0xff
                self.assertRaises(ReedSolomonError, rs.decode, tem1)

            def test_generator_poly(self):
                '''Test if generator poly finder is working correctly and if the all generators poly finder does output the same result'''
                n = 11
                k = 3

                # Base 2 test
                fcr = 120
                generator = 2
                prim = 0x11d
                init_tables(generator=generator, prim=prim)
                g = rs_generator_poly_all(n, fcr=fcr, generator=generator)
                self.assertEqual( list(g[n-k]) , list(rs_generator_poly(n-k,fcr=fcr, generator=generator)) )
                self.assertEqual( list(g[n-k]) , [1, 106, 9, 105, 86, 5, 166, 76, 9] )

                # Base 3 test
                fcr = 0
                generator = 3
                prim = 0x11b
                init_tables(generator=generator, prim=prim)
                g = rs_generator_poly_all(n, fcr=fcr, generator=generator)
                self.assertEqual( list(g[n-k]) , list(rs_generator_poly(n-k,fcr=fcr, generator=generator)) )
                self.assertEqual( list(g[n-k]) , [1, 128, 13, 69, 36, 145, 199, 165, 30] )

            def test_prime_poly_build(self):
                '''Try if the prime polynomials finder works correctly for different GFs (ie, GF(2^6) to GF(2^10)) and with different generators'''
                params = {"count": 7,
                          "c_exp": [6, 7, 7, 8, 8, 9, 10],
                          "generator": [2, 2, 3, 2, 3, 2, 2],
                          "expected": [
                            [67, 91, 97, 103, 109, 115],
                            [131, 137, 143, 145, 157, 167, 171, 185, 191, 193, 203, 211, 213, 229, 239, 241, 247, 253],
                            [131, 137, 143, 145, 157, 167, 171, 185, 191, 193, 203, 211, 213, 229, 239, 241, 247, 253],
                            [285, 299, 301, 333, 351, 355, 357, 361, 369, 391, 397, 425, 451, 463, 487, 501],
                            [283, 313, 319, 333, 351, 355, 357, 361, 375, 397, 415, 419, 425, 451, 501, 505],
                            [529, 539, 545, 557, 563, 601, 607, 617, 623, 631, 637, 647, 661, 675, 677, 687, 695, 701, 719, 721, 731, 757, 761, 787, 789, 799, 803, 817, 827, 847, 859, 865, 875, 877, 883, 895, 901, 911, 949, 953, 967, 971, 973, 981, 985, 995, 1001, 1019],
                            [1033, 1051, 1063, 1069, 1125, 1135, 1153, 1163, 1221, 1239, 1255, 1267, 1279, 1293, 1305, 1315, 1329, 1341, 1347, 1367, 1387, 1413, 1423, 1431, 1441, 1479, 1509, 1527, 1531, 1555, 1557, 1573, 1591, 1603, 1615, 1627, 1657, 1663, 1673, 1717, 1729, 1747, 1759, 1789, 1815, 1821, 1825, 1849, 1863, 1869, 1877, 1881, 1891, 1917, 1933, 1939, 1969, 2011, 2035, 2041]
                          ]
                         }

                for i in xrange(params['count']):
                    self.assertEqual( find_prime_polys(generator=params['generator'][i], c_exp=params['c_exp'][i]) , array.array('i', params["expected"][i]) )

            def test_init_tables(self):
                '''Try if the look up table generator (galois field generator) works correctly for different parameters'''
                params = [
                                [0x11d, 2, 8],
                                [0x11b, 3, 8],
                                [0xfd, 3, 7]
                               ]
                expected = [
                                        [
                                            [0, 0, 1, 25, 2, 50, 26, 198, 3, 223, 51, 238, 27, 104, 199, 75, 4, 100, 224, 14, 52, 141, 239, 129, 28, 193, 105, 248, 200, 8, 76, 113, 5, 138, 101, 47, 225, 36, 15, 33, 53, 147, 142, 218, 240, 18, 130, 69, 29, 181, 194, 125, 106, 39, 249, 185, 201, 154, 9, 120, 77, 228, 114, 166, 6, 191, 139, 98, 102, 221, 48, 253, 226, 152, 37, 179, 16, 145, 34, 136, 54, 208, 148, 206, 143, 150, 219, 189, 241, 210, 19, 92, 131, 56, 70, 64, 30, 66, 182, 163, 195, 72, 126, 110, 107, 58, 40, 84, 250, 133, 186, 61, 202, 94, 155, 159, 10, 21, 121, 43, 78, 212, 229, 172, 115, 243, 167, 87, 7, 112, 192, 247, 140, 128, 99, 13, 103, 74, 222, 237, 49, 197, 254, 24, 227, 165, 153, 119, 38, 184, 180, 124, 17, 68, 146, 217, 35, 32, 137, 46, 55, 63, 209, 91, 149, 188, 207, 205, 144, 135, 151, 178, 220, 252, 190, 97, 242, 86, 211, 171, 20, 42, 93, 158, 132, 60, 57, 83, 71, 109, 65, 162, 31, 45, 67, 216, 183, 123, 164, 118, 196, 23, 73, 236, 127, 12, 111, 246, 108, 161, 59, 82, 41, 157, 85, 170, 251, 96, 134, 177, 187, 204, 62, 90, 203, 89, 95, 176, 156, 169, 160, 81, 11, 245, 22, 235, 122, 117, 44, 215, 79, 174, 213, 233, 230, 231, 173, 232, 116, 214, 244, 234, 168, 80, 88, 175],
                                            [1, 2, 4, 8, 16, 32, 64, 128, 29, 58, 116, 232, 205, 135, 19, 38, 76, 152, 45, 90, 180, 117, 234, 201, 143, 3, 6, 12, 24, 48, 96, 192, 157, 39, 78, 156, 37, 74, 148, 53, 106, 212, 181, 119, 238, 193, 159, 35, 70, 140, 5, 10, 20, 40, 80, 160, 93, 186, 105, 210, 185, 111, 222, 161, 95, 190, 97, 194, 153, 47, 94, 188, 101, 202, 137, 15, 30, 60, 120, 240, 253, 231, 211, 187, 107, 214, 177, 127, 254, 225, 223, 163, 91, 182, 113, 226, 217, 175, 67, 134, 17, 34, 68, 136, 13, 26, 52, 104, 208, 189, 103, 206, 129, 31, 62, 124, 248, 237, 199, 147, 59, 118, 236, 197, 151, 51, 102, 204, 133, 23, 46, 92, 184, 109, 218, 169, 79, 158, 33, 66, 132, 21, 42, 84, 168, 77, 154, 41, 82, 164, 85, 170, 73, 146, 57, 114, 228, 213, 183, 115, 230, 209, 191, 99, 198, 145, 63, 126, 252, 229, 215, 179, 123, 246, 241, 255, 227, 219, 171, 75, 150, 49, 98, 196, 149, 55, 110, 220, 165, 87, 174, 65, 130, 25, 50, 100, 200, 141, 7, 14, 28, 56, 112, 224, 221, 167, 83, 166, 81, 162, 89, 178, 121, 242, 249, 239, 195, 155, 43, 86, 172, 69, 138, 9, 18, 36, 72, 144, 61, 122, 244, 245, 247, 243, 251, 235, 203, 139, 11, 22, 44, 88, 176, 125, 250, 233, 207, 131, 27, 54, 108, 216, 173, 71, 142, 1, 2, 4, 8, 16, 32, 64, 128, 29, 58, 116, 232, 205, 135, 19, 38, 76, 152, 45, 90, 180, 117, 234, 201, 143, 3, 6, 12, 24, 48, 96, 192, 157, 39, 78, 156, 37, 74, 148, 53, 106, 212, 181, 119, 238, 193, 159, 35, 70, 140, 5, 10, 20, 40, 80, 160, 93, 186, 105, 210, 185, 111, 222, 161, 95, 190, 97, 194, 153, 47, 94, 188, 101, 202, 137, 15, 30, 60, 120, 240, 253, 231, 211, 187, 107, 214, 177, 127, 254, 225, 223, 163, 91, 182, 113, 226, 217, 175, 67, 134, 17, 34, 68, 136, 13, 26, 52, 104, 208, 189, 103, 206, 129, 31, 62, 124, 248, 237, 199, 147, 59, 118, 236, 197, 151, 51, 102, 204, 133, 23, 46, 92, 184, 109, 218, 169, 79, 158, 33, 66, 132, 21, 42, 84, 168, 77, 154, 41, 82, 164, 85, 170, 73, 146, 57, 114, 228, 213, 183, 115, 230, 209, 191, 99, 198, 145, 63, 126, 252, 229, 215, 179, 123, 246, 241, 255, 227, 219, 171, 75, 150, 49, 98, 196, 149, 55, 110, 220, 165, 87, 174, 65, 130, 25, 50, 100, 200, 141, 7, 14, 28, 56, 112, 224, 221, 167, 83, 166, 81, 162, 89, 178, 121, 242, 249, 239, 195, 155, 43, 86, 172, 69, 138, 9, 18, 36, 72, 144, 61, 122, 244, 245, 247, 243, 251, 235, 203, 139, 11, 22, 44, 88, 176, 125, 250, 233, 207, 131, 27, 54, 108, 216, 173, 71, 142],
                                            255
                                        ],
                                        [
                                            [0, 0, 25, 1, 50, 2, 26, 198, 75, 199, 27, 104, 51, 238, 223, 3, 100, 4, 224, 14, 52, 141, 129, 239, 76, 113, 8, 200, 248, 105, 28, 193, 125, 194, 29, 181, 249, 185, 39, 106, 77, 228, 166, 114, 154, 201, 9, 120, 101, 47, 138, 5, 33, 15, 225, 36, 18, 240, 130, 69, 53, 147, 218, 142, 150, 143, 219, 189, 54, 208, 206, 148, 19, 92, 210, 241, 64, 70, 131, 56, 102, 221, 253, 48, 191, 6, 139, 98, 179, 37, 226, 152, 34, 136, 145, 16, 126, 110, 72, 195, 163, 182, 30, 66, 58, 107, 40, 84, 250, 133, 61, 186, 43, 121, 10, 21, 155, 159, 94, 202, 78, 212, 172, 229, 243, 115, 167, 87, 175, 88, 168, 80, 244, 234, 214, 116, 79, 174, 233, 213, 231, 230, 173, 232, 44, 215, 117, 122, 235, 22, 11, 245, 89, 203, 95, 176, 156, 169, 81, 160, 127, 12, 246, 111, 23, 196, 73, 236, 216, 67, 31, 45, 164, 118, 123, 183, 204, 187, 62, 90, 251, 96, 177, 134, 59, 82, 161, 108, 170, 85, 41, 157, 151, 178, 135, 144, 97, 190, 220, 252, 188, 149, 207, 205, 55, 63, 91, 209, 83, 57, 132, 60, 65, 162, 109, 71, 20, 42, 158, 93, 86, 242, 211, 171, 68, 17, 146, 217, 35, 32, 46, 137, 180, 124, 184, 38, 119, 153, 227, 165, 103, 74, 237, 222, 197, 49, 254, 24, 13, 99, 140, 128, 192, 247, 112, 7],
                                            [1, 3, 5, 15, 17, 51, 85, 255, 26, 46, 114, 150, 161, 248, 19, 53, 95, 225, 56, 72, 216, 115, 149, 164, 247, 2, 6, 10, 30, 34, 102, 170, 229, 52, 92, 228, 55, 89, 235, 38, 106, 190, 217, 112, 144, 171, 230, 49, 83, 245, 4, 12, 20, 60, 68, 204, 79, 209, 104, 184, 211, 110, 178, 205, 76, 212, 103, 169, 224, 59, 77, 215, 98, 166, 241, 8, 24, 40, 120, 136, 131, 158, 185, 208, 107, 189, 220, 127, 129, 152, 179, 206, 73, 219, 118, 154, 181, 196, 87, 249, 16, 48, 80, 240, 11, 29, 39, 105, 187, 214, 97, 163, 254, 25, 43, 125, 135, 146, 173, 236, 47, 113, 147, 174, 233, 32, 96, 160, 251, 22, 58, 78, 210, 109, 183, 194, 93, 231, 50, 86, 250, 21, 63, 65, 195, 94, 226, 61, 71, 201, 64, 192, 91, 237, 44, 116, 156, 191, 218, 117, 159, 186, 213, 100, 172, 239, 42, 126, 130, 157, 188, 223, 122, 142, 137, 128, 155, 182, 193, 88, 232, 35, 101, 175, 234, 37, 111, 177, 200, 67, 197, 84, 252, 31, 33, 99, 165, 244, 7, 9, 27, 45, 119, 153, 176, 203, 70, 202, 69, 207, 74, 222, 121, 139, 134, 145, 168, 227, 62, 66, 198, 81, 243, 14, 18, 54, 90, 238, 41, 123, 141, 140, 143, 138, 133, 148, 167, 242, 13, 23, 57, 75, 221, 124, 132, 151, 162, 253, 28, 36, 108, 180, 199, 82, 246, 1, 3, 5, 15, 17, 51, 85, 255, 26, 46, 114, 150, 161, 248, 19, 53, 95, 225, 56, 72, 216, 115, 149, 164, 247, 2, 6, 10, 30, 34, 102, 170, 229, 52, 92, 228, 55, 89, 235, 38, 106, 190, 217, 112, 144, 171, 230, 49, 83, 245, 4, 12, 20, 60, 68, 204, 79, 209, 104, 184, 211, 110, 178, 205, 76, 212, 103, 169, 224, 59, 77, 215, 98, 166, 241, 8, 24, 40, 120, 136, 131, 158, 185, 208, 107, 189, 220, 127, 129, 152, 179, 206, 73, 219, 118, 154, 181, 196, 87, 249, 16, 48, 80, 240, 11, 29, 39, 105, 187, 214, 97, 163, 254, 25, 43, 125, 135, 146, 173, 236, 47, 113, 147, 174, 233, 32, 96, 160, 251, 22, 58, 78, 210, 109, 183, 194, 93, 231, 50, 86, 250, 21, 63, 65, 195, 94, 226, 61, 71, 201, 64, 192, 91, 237, 44, 116, 156, 191, 218, 117, 159, 186, 213, 100, 172, 239, 42, 126, 130, 157, 188, 223, 122, 142, 137, 128, 155, 182, 193, 88, 232, 35, 101, 175, 234, 37, 111, 177, 200, 67, 197, 84, 252, 31, 33, 99, 165, 244, 7, 9, 27, 45, 119, 153, 176, 203, 70, 202, 69, 207, 74, 222, 121, 139, 134, 145, 168, 227, 62, 66, 198, 81, 243, 14, 18, 54, 90, 238, 41, 123, 141, 140, 143, 138, 133, 148, 167, 242, 13, 23, 57, 75, 221, 124, 132, 151, 162, 253, 28, 36, 108, 180, 199, 82, 246],
                                            255
                                        ],
                                        [
                                            [0, 0, 7, 1, 14, 2, 8, 56, 21, 57, 9, 90, 15, 31, 63, 3, 28, 4, 64, 67, 16, 112, 97, 32, 22, 47, 38, 58, 70, 91, 10, 108, 35, 109, 11, 87, 71, 79, 74, 92, 23, 82, 119, 48, 104, 59, 39, 100, 29, 19, 54, 5, 45, 68, 65, 95, 77, 33, 98, 117, 17, 43, 115, 113, 42, 114, 116, 76, 18, 53, 94, 44, 78, 73, 86, 34, 81, 118, 99, 103, 30, 62, 89, 20, 126, 6, 55, 13, 111, 96, 66, 27, 46, 37, 107, 69, 36, 106, 26, 110, 61, 88, 12, 125, 52, 93, 75, 41, 72, 85, 102, 80, 84, 101, 40, 51, 105, 25, 124, 60, 24, 123, 50, 83, 122, 49, 120, 121],
                                            [1, 3, 5, 15, 17, 51, 85, 2, 6, 10, 30, 34, 102, 87, 4, 12, 20, 60, 68, 49, 83, 8, 24, 40, 120, 117, 98, 91, 16, 48, 80, 13, 23, 57, 75, 32, 96, 93, 26, 46, 114, 107, 64, 61, 71, 52, 92, 25, 43, 125, 122, 115, 104, 69, 50, 86, 7, 9, 27, 45, 119, 100, 81, 14, 18, 54, 90, 19, 53, 95, 28, 36, 108, 73, 38, 106, 67, 56, 72, 37, 111, 76, 41, 123, 112, 109, 74, 35, 101, 82, 11, 29, 39, 105, 70, 55, 89, 22, 58, 78, 47, 113, 110, 79, 44, 116, 97, 94, 31, 33, 99, 88, 21, 63, 65, 62, 66, 59, 77, 42, 126, 127, 124, 121, 118, 103, 84, 1, 3, 5, 15, 17, 51, 85, 2, 6, 10, 30, 34, 102, 87, 4, 12, 20, 60, 68, 49, 83, 8, 24, 40, 120, 117, 98, 91, 16, 48, 80, 13, 23, 57, 75, 32, 96, 93, 26, 46, 114, 107, 64, 61, 71, 52, 92, 25, 43, 125, 122, 115, 104, 69, 50, 86, 7, 9, 27, 45, 119, 100, 81, 14, 18, 54, 90, 19, 53, 95, 28, 36, 108, 73, 38, 106, 67, 56, 72, 37, 111, 76, 41, 123, 112, 109, 74, 35, 101, 82, 11, 29, 39, 105, 70, 55, 89, 22, 58, 78, 47, 113, 110, 79, 44, 116, 97, 94, 31, 33, 99, 88, 21, 63, 65, 62, 66, 59, 77, 42, 126, 127, 124, 121, 118, 103, 84],
                                            127
                                        ]
                                    ]
                for i in xrange(len(params)):
                    p = params[i]
                    expected_log_t, expected_exp_t, expected_field_charac_t = expected[i]
                    log_t, exp_t, field_charac_t = init_tables(prim=p[0], generator=p[1], c_exp=p[2])
                    self.assertEqual( field_charac_t, expected_field_charac_t )
                    self.assertEqual( list(log_t) , expected_log_t )
                    self.assertEqual( list(exp_t) , expected_exp_t )

            def test_consistent_erasures_report(self):
                # Ensure we always at least return the erasures we used as input
                rs = RSCodec(10)
                msg = rs.encode(bytearray("hello world ", "latin1"))
                self.assertEqual(rs.decode(msg, erase_pos=bytearray([1]))[2], bytearray([1]))
                self.assertEqual(rs.decode(msg, erase_pos=bytearray([1]))[2], bytearray([1]))
                msg[1] = 0xFF
                self.assertEqual(rs.decode(msg)[2], bytearray([1]))
                self.assertEqual(rs.decode(msg, erase_pos=bytearray([1]))[2], bytearray([1]))

            def test_consistent_erasures_report_2(self):
                # Ensure we always at least return the erasures we used as input
                _ = init_tables()
                # parameters
                nsym = 4
                # generate the polynomials before calling rs_*_encode_msg(), as otherwise we will get an error saying that gen is not set with Cython)
                gen = rs_generator_poly(nsym)
                # Encode the messages
                msg = rs_encode_msg(bytearray(range(10)), nsym=nsym, gen=gen)
                self.assertEqual(rs_correct_msg(msg, nsym=nsym, erase_pos=bytearray([1]))[2], bytearray([1]))
                self.assertEqual(rs_correct_msg(msg, nsym=nsym, erase_pos=bytearray([1]))[2], bytearray([1]))
                msg[1] = 0xFF
                self.assertEqual(rs_correct_msg(msg, nsym=nsym)[2], bytearray([1]))
                self.assertEqual(rs_correct_msg(msg, nsym=nsym, erase_pos=bytearray([1]))[2], bytearray([1]))

            def test_erasures_chunking(self):
                # Test whether providing positions for erasures in the 2nd chunk or later is working
                rs = RSCodec(30)
                encoded = rs.encode(bytearray("0" * 226, "latin1"))
                _, _, _ = rs.decode(encoded, erase_pos=bytearray([255]), only_erasures=True)
                # If it works, no exception should be raised

            def test_too_many_ecc_symbols(self):
                RSCodec(254).encode(bytearray("a", "latin1"))
                self.assertRaises(ValueError, RSCodec, 255) # nsym=255
                self.assertRaises(ValueError, RSCodec, 2000) # nsym=2000

            def test_generate_all_poly_and_different_nsym_at_encode(self):
                '''Test encoding with various ECC symbols length using the same encoder.'''
                codec_250 = RSCodec(250, single_gen=True)
                codec_240 = RSCodec(240, single_gen=True)
                codec_all = RSCodec(250, single_gen=False)  # this is the multi-nsym encoder, single_gen=False is required
                msgorig = bytearray("hello world!", "latin1")
                self.assertEqual(bytearray(codec_250.encode(msgorig)), bytearray(codec_all.encode(msgorig)))  # need to instanciate the memoryviews into bytearrays to be comparable
                self.assertEqual(bytearray(codec_250.encode(msgorig)), bytearray(codec_all.encode(msgorig, nsym=250)))
                self.assertEqual(bytearray(codec_240.encode(msgorig)), bytearray(codec_all.encode(msgorig, nsym=240)))

            def test_different_nsym_at_decode(self):
                '''Test decoding with various ECC symbols length using the same decoder.'''
                codec_250 = RSCodec(250, single_gen=True)  # note that single_gen=False is not necessary here for multi-nsym decoding, it's only for multi-nsym encoding
                codec_240 = RSCodec(240, single_gen=True)
                msgorig = bytearray("hello world!"*3, "latin1")
                enc_250 = codec_250.encode(msgorig)
                enc_240 = codec_240.encode(msgorig)
                for i in [27, -3, -9, 7, 0]:
                    enc_250[i] = 99
                    enc_240[i] = 99
                    rmsg_250_250, _, _ = codec_250.decode(enc_250, 250)
                    rmsg_250_240, _, _ = codec_250.decode(enc_240, 240)  # this is the tricky one
                    rmsg_240_250, _, _ = codec_240.decode(enc_250, 250)  # this is the other tricky one
                    rmsg_240_240, _, _ = codec_240.decode(enc_240, 240)
                    self.assertEqual(rmsg_250_250, msgorig)
                    self.assertEqual(rmsg_250_240, msgorig)
                    self.assertEqual(rmsg_240_250, msgorig)
                    self.assertEqual(rmsg_240_240, msgorig)

        class cTestGFArithmetics(unittest.TestCase):
            '''Test Galois Field arithmetics'''

            def test_multiply_nolut(self):
                '''Try to multiply without look-up tables (necessary to build the look-up tables!)'''
                a = 30
                b = 19

                generator=2
                prim=0x11d

                # Compare the LUT multiplication and noLUT
                init_tables(prim=prim, generator=generator)
                self.assertEqual(gf_mul(a, b), gf_mult_noLUT(a, b, prim=prim))

                # More Galois Field multiplications
                self.assertEqual( gf_mult_noLUT(5, 6, prim=0x11b, field_charac_full=256) , 30 )
                self.assertEqual( gf_mult_noLUT(3, 125, prim=0x11b, field_charac_full=256) , 135 )
                self.assertEqual( gf_mult_noLUT(2, 200, prim=0x11d, field_charac_full=256) , 141 )
                self.assertEqual( gf_mult_noLUT_slow(2, 200, prim=0x11d) , 141 )
                # Multiplications in GF(2^7)
                self.assertEqual( gf_mult_noLUT(3, 125, prim=0xfd, field_charac_full=128) , 122 )
                # Multiplications outside of the finite field (we revert to standard integer multiplications just to see if it works)
                self.assertEqual( gf_mult_noLUT(3, 125, prim=0, carryless=False) , 375 )
                self.assertEqual( gf_mult_noLUT_slow(4, 125, prim=0) , 500 ) # the second method, just to check that everything's alright

            def test_gf_operations(self):
                '''Try various Galois Field 2 operations'''
                init_tables(prim=0x11d, generator=2, c_exp=8)

                a = 30
                b = 19

                # Addition and subtraction (they are the same in GF(2^p)
                self.assertEqual(gf_add(0, 0), 0)
                self.assertEqual(gf_add(0, 0), gf_sub(0, 0))
                self.assertEqual(gf_add(1, 0), 1)
                self.assertEqual(gf_add(1, 0), gf_sub(1, 0))
                self.assertEqual(gf_add(0, 1), 1)
                self.assertEqual(gf_add(0, 1), gf_sub(0, 1))
                self.assertEqual(gf_add(1, 1), 0)
                self.assertEqual(gf_add(1, 1), gf_sub(1, 1))
                self.assertEqual(gf_add(a, b), 13)
                self.assertEqual(gf_add(a, b), gf_sub(a, b))
                self.assertEqual(gf_add(0, b), b)
                self.assertEqual(gf_add(0, b), gf_sub(0, b))
                self.assertEqual(gf_add(a, 0), a)
                self.assertEqual(gf_add(a, 0), gf_sub(a,0))
                self.assertEqual(gf_add(a, 1), (a+1))
                self.assertEqual(gf_add(a, 1), gf_sub(a, 1))
                self.assertEqual(gf_add(1, a), (a+1))
                self.assertEqual(gf_add(1, a), gf_sub(1, a))
                self.assertEqual(gf_add(255, 1), 254)

                # Negation
                self.assertEqual(gf_neg(a), a)
                self.assertEqual(gf_neg(b), b)

                # Division
                self.assertEqual(gf_div(a, 1), a)
                self.assertEqual(gf_div(12, 3), 4)
                self.assertEqual(gf_div(a, b), 222)
                self.assertEqual(gf_div(b, a), 25)
                self.assertEqual(gf_div(0, a), 0)
                self.assertRaises(ZeroDivisionError, gf_div, *[a, 0])

        class cTestSimpleFuncs(unittest.TestCase):
            '''Test simple functions and see if the results are equivalent with optimized functions'''

            def test_gf_poly_mul_simple(self):
                a = bytearray([1, 12, 14, 9])
                b = bytearray([0, 23, 2, 15])
                self.assertEqual(gf_poly_mul(a, b), gf_poly_mul_simple(a, b))

            def test_gf_poly_neg(self):
                a = bytearray([1, 12, 14, 9])
                self.assertEqual(gf_poly_neg(a), a)

            def test_rs_simple_encode_msg(self):
                a = bytearray("hello world", "latin1")
                nsym = 10
                fcr = 120
                generator = 2
                prim = 0x11d
                # Init the RS codec
                init_tables(generator=generator, prim=prim)
                gen = rs_generator_poly(nsym, fcr=fcr, generator=generator)
                # Encode the message (note that we need to use rs_generator_poly() before calling rs_*_encode_msg(), as otherwise we will get an error saying that gen is not set)
                self.assertEqual(rs_simple_encode_msg(a, nsym, gen=gen), rs_encode_msg(a, nsym, gen=gen))

        class cTestRSCodecUniversalCrossValidation(unittest.TestCase):
            '''Ultimate set of tests of a full set of different parameters for encoding and decoding. If this passes, the codec is universal and can correctly interface with any other RS codec!'''

            def test_main(self):
                def cartesian_product_dict_items(dicts):
                    return (dict(izip(dicts, x)) for x in itertools.product(*dicts.values()))

                debugg = False # if one or more tests don't pass, you can enable this flag to True to get verbose output to debug

                orig_mes = bytearray("hello world", "latin1")
                n = len(orig_mes)*2
                k = len(orig_mes)
                nsym = n-k
                istart = 0

                params = {"count": 5,
                          "fcr": [120, 0, 1, 1, 1],
                          "prim": [0x187, 0x11d, 0x11b, 0xfd, 0xfd],
                          "generator": [2, 2, 3, 3, 2],
                          "c_exponent": [8, 8, 8, 7, 7],
                         }
                cases = {
                         "errmode": [1, 2, 3, 4],
                         "erratasnb_errorsnb_onlyeras": [[8, 3, False], [6, 5, False], [5, 5, False], [11, 0, True], [11, 0, False], [0,0, False]], # errata number (errors+erasures), erasures number and only_erasures: the last item is the value for only_erasures (True/False)
                         }

                ############################$

                results_br = []
                results_rs = []

                it = 0
                for p in xrange(params["count"]):
                    fcr = params["fcr"][p]
                    prim = params["prim"][p]
                    generator = params["generator"][p]
                    c_exponent = params["c_exponent"][p]

                    for case in cartesian_product_dict_items(cases):
                        errmode = case["errmode"]
                        erratanb = case["erratasnb_errorsnb_onlyeras"][0]
                        errnb = case["erratasnb_errorsnb_onlyeras"][1]
                        only_erasures = case["erratasnb_errorsnb_onlyeras"][2]
                        
                        it += 1
                        if debugg:
                            print("it ", it)
                            print("param", p)
                            print(case)

                        # REEDSOLO
                        # Init the RS codec
                        init_tables(generator=generator, prim=prim, c_exp=c_exponent)
                        g = rs_generator_poly_all(n, fcr=fcr, generator=generator)
                        # Encode the message
                        rmesecc = rs_encode_msg(orig_mes, n-k, gen=g[n-k])
                        rmesecc_orig = bytearray(rmesecc[:]) # make a copy of the original message to check later if fully corrected (because the syndrome may be wrong sometimes)
                        # Tamper the message
                        if erratanb > 0:
                            if errmode == 1:
                                sl = slice(istart, istart+erratanb)
                            elif errmode == 2:
                                sl = slice(-istart-erratanb-(n-k), -(n-k))
                            elif errmode == 3:
                                sl = slice(-istart-erratanb-1, -1)
                            elif errmode == 4:
                                sl = slice(-istart-erratanb, None)
                            if debugg:
                                print("Removed slice:", list(rmesecc[sl]), rmesecc[sl])
                            rmesecc[sl] = [0] * erratanb
                        # Generate the erasures positions (if any)
                        erase_pos = [x for x in xrange(len(rmesecc)) if rmesecc[x] == 0]
                        if errnb > 0: erase_pos = erase_pos[:-errnb] # remove the errors positions (must not be known by definition)
                        if debugg:
                            print("erase_pos", erase_pos)
                            print("coef_pos", [len(rmesecc) - 1 - pos for pos in erase_pos])
                            print("Errata total: ", erratanb-errnb + errnb*2, " -- Correctable? ", (erratanb-errnb + errnb*2 <= nsym))
                        # Decoding the corrupted codeword
                        # -- Forney syndrome method
                        try:
                            rmes, recc, errata_pos = rs_correct_msg(rmesecc, n-k, fcr=fcr, generator=generator, erase_pos=bytearray(erase_pos), only_erasures=only_erasures)
                            rmesecc_post = bytearray(rmes) + bytearray(recc)
                            results_br.append( rs_check(rmesecc_post, n-k, fcr=fcr, generator=generator) ) # check if correct by syndrome analysis (can be wrong)
                            results_br.append( rmesecc_orig == rmesecc_post ) # check if correct by comparing to the original message (always correct)
                            if debugg and not rs_check(rmesecc_post, n-k, fcr=fcr, generator=generator) or not (rmesecc_orig == rmesecc_post): raise ReedSolomonError("False!!!!!")
                        except ReedSolomonError as exc:
                            results_br.append(False)
                            results_br.append(False)
                            if debugg:
                                print("====")
                                print("ERROR! Details:")
                                print("param", p)
                                print(case)
                                print(erase_pos)
                                print("original_msg", rmesecc_orig)
                                print("tampered_msg", rmesecc)
                                print("decoded_msg", rmesecc_post)
                                print("checks: ", rs_check(rmesecc_post, n-k, fcr=fcr, generator=generator), rmesecc_orig == rmesecc_post)
                                print("====")
                                raise exc
                        # -- Without Forney syndrome method
                        try:
                            rmes, recc, errata_pos = rs_correct_msg_nofsynd(rmesecc, n-k, fcr=fcr, generator=generator, erase_pos=bytearray(erase_pos), only_erasures=only_erasures)
                            rmesecc_post = bytearray(rmes) + bytearray(recc)
                            results_br.append( rs_check(rmesecc_post, n-k, fcr=fcr, generator=generator) )
                            results_br.append( rmesecc_orig == rmesecc_post )
                        except ReedSolomonError as exc:
                            results_br.append(False)
                            results_br.append(False)

                        if debugg: print("-----")

                self.assertTrue(results_br.count(True) == len(results_br))

        class TestHelperFuncs(unittest.TestCase):
            '''Test helper functions'''

            def test_maxerrata(self):
                rs = RSCodec(10)
                self.assertEqual(rs.maxerrata(), (5, 10))
                self.assertEqual(rs.maxerrata(erasures=8), (1, 8))
                self.assertEqual(rs.maxerrata(errors=2), (2, 6))
                self.assertRaises(ReedSolomonError, rs.maxerrata, erasures=11)
                self.assertRaises(ReedSolomonError, rs.maxerrata, errors=6)

            def test_maxerrata_verbose(self):
                output = StringIO()
                sys.stdout = output
                rs = RSCodec(10)
                rs.maxerrata(verbose=True)
                rs.maxerrata(erasures=2, verbose=True)
                rs.maxerrata(errors=4, verbose=True)
                sys.stdout = sys.__stdout__
                self.assertEqual(output.getvalue(), "This codec can correct up to 5 errors and 10 erasures independently\nThis codec can correct up to 4 errors and 2 erasures simultaneously\nThis codec can correct up to 4 errors and 2 erasures simultaneously\n")


if __name__ == "__main__":
    unittest.main()
