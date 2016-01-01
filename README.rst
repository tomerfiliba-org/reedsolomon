Reed Solomon
============

.. image:: https://travis-ci.org/lrq3000/reedsolomon.svg?branch=master
    :target: https://travis-ci.org/lrq3000/reedsolomon

.. image:: https://coveralls.io/repos/lrq3000/reedsolomon/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/lrq3000/reedsolomon?branch=master

A pure-python `universal errors-and-erasures Reed-Solomon Codec <http://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction>`_
, based on the wonderful tutorial at
`wikiversity <http://en.wikiversity.org/wiki/Reed%E2%80%93Solomon_codes_for_coders>`_,
written by "Bobmath" and "LRQ3000".

The code of wikiversity is here consolidated into a nice API with exceptions handling.
The algorithm can correct up to 2*e+v <= nsym, where e is the number of errors,
v the number of erasures and nsym = n-k = the number of ECC (error correction code) symbols.
This means that you can either correct exactly floor(nsym/2) errors, or nsym erasures
(errors where you know the position), and a combination of both errors and erasures.
The code should work on pretty much any reasonable version of python (2.4-3.5),
but I'm only testing on 2.7 - 3.4.

The codec has quite reasonable performances if you either use PyPy on the pure-python
implementation (reedsolo.py) or either if you compile the Cython extension creedsolo.py
(which is about 2x faster than PyPy). You can expect encoding rate of several MB/s.

This library is also thoroughly unit tested so that any encoding/decoding case should be covered.

.. note::
   The codec is universal, meaning that it can decode any message encoded by another RS encoder
   as long as you provide the correct parameters.
   Note however that if you use higher fields (ie, bigger c_exp), the algorithms will be slower, first because
   we cannot then use the optimized bytearray() structure but only array.array('i', ...), and also because
   Reed-Solomon's complexity is quadratic (both in encoding and decoding), so this means that the longer
   your messages, the longer it will take to encode/decode (quadratically!).

   The algorithm itself can handle messages up to (2^c_exp)-1 symbols, including the ECC symbols,
   and each symbol can have a value of up to (2^c_exp)-1 (indeed, both the message length and the maximum
   value for one character is constrained by the same mathematical reason). By default, we use the field GF(2^8),
   which means that you are limited to values between 0 and 255 (perfect to represent a single hexadecimal
   symbol on computers, so you can encode any binary stream) and limited to messages+ecc of maximum
   length 255. However, you can "chunk" longer messages to fit them into the message length limit.
   The ``RSCodec`` class will automatically apply chunking, by splitting longer messages into chunks and
   encode/decode them separately; it shouldn't make a difference from an API perspective (ie, from your POV).

::

    # Initialization
    >>> from reedsolo import RSCodec
    >>> rsc = RSCodec(10)  # 10 ecc symbols

    # Encoding
    >>> rsc.encode([1,2,3,4])
    b'\x01\x02\x03\x04,\x9d\x1c+=\xf8h\xfa\x98M'
    >>> rsc.encode(b'hello world')
    b'hello world\xed%T\xc4\xfd\xfd\x89\xf3\xa8\xaa'

    # Decoding (repairing)
    >>> rsc.decode(b'hello world\xed%T\xc4\xfd\xfd\x89\xf3\xa8\xaa')[0]
    b'hello world'
    >>> rsc.decode(b'heXlo worXd\xed%T\xc4\xfdX\x89\xf3\xa8\xaa')[0]     # 3 errors
    b'hello world'
    >>> rsc.decode(b'hXXXo worXd\xed%T\xc4\xfdX\x89\xf3\xa8\xaa')[0]     # 5 errors
    b'hello world'
    >>> rsc.decode(b'hXXXo worXd\xed%T\xc4\xfdXX\xf3\xa8\xaa')[0]        # 6 errors - fail
    Traceback (most recent call last):
      ...
    ReedSolomonError: Could not locate error

    >>> rsc = RSCodec(12)  # using 2 more ecc symbols (to correct max 6 errors or 12 erasures)
    >>> rsc.encode(b'hello world')
    b'hello world?Ay\xb2\xbc\xdc\x01q\xb9\xe3\xe2='
    >>> rsc.decode(b'hello worXXXXy\xb2XX\x01q\xb9\xe3\xe2=')[0]         # 6 errors - ok
    b'hello world'
    >>> rsc.decode(b'helXXXXXXXXXXy\xb2XX\x01q\xb9\xe3\xe2=', erase_pos=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16])[0]  # 12 erasures - OK
    b'hello world'

    # Checking
    >> rsc.check(b'hello worXXXXy\xb2XX\x01q\xb9\xe3\xe2=')
    [False]
    >> rmes, rmesecc = rsc.decode(b'hello worXXXXy\xb2XX\x01q\xb9\xe3\xe2=')
    >> rsc.check(rmesecc)
    [True]

    # To use longer chunks or bigger values than 255 (may be very slow)
    >> rsc = RSCodec(12, nsize=4095)  # always use a power of 2 minus 1
    >> rsc = RSCodec(12, c_exp=12)  # alternative way to set nsize=4095
    >> mes = 'a' * (4095-12)
    >> mesecc = rsc.encode(mes)
    >> mesecc[2] = 1
    >> mesecc[-1] = 1
    >> rmes, rmesecc = rsc.decode(mesecc)
    >> rsc.check(mesecc)
    [False]
    >> rsc.check(rmesecc)
    [True]

    If you want full control, you can skip the API and directly use the library as-is. Here's how:

    First you need to init the precomputed tables:
    >> import reedsolo as rs
    >> rs.init_tables(0x11d)
    Pro tip: if you get the error: ValueError: byte must be in range(0, 256), please check that your prime polynomial is correct for your field.
    Pro tip2: by default, you can only encode messages of max length and max symbol value = 256. If you want to encode bigger messages,
    please use the following (where c_exp is the exponent of your Galois Field, eg, 12 = max length 2^12 = 4096):
    >> prim = rs.find_prime_polys(c_exp=12, fast_primes=True, single=True)
    >> rs.init_tables(c_exp=12, prim=prim)
    
    Let's define our RS message and ecc size:
    >> n = 255  # length of total message+ecc
    >> nsym = 12  # length of ecc
    >> mes = "a" * (n-nsym)  # generate a sample message

    To optimize, you can precompute the generator polynomial:
    >> gen = rs.rs_generator_poly_all(n)

    Then to encode:
    >> mesecc = rs.rs_encode_msg(mes, nsym, gen=gen[nsym])

    Let's tamper our message:
    >> mesecc[1] = 0

    To decode:
    >> rmes, recc = rs.rs_correct_msg(mesecc, nsym, erase_pos=erase_pos)
    Note that both the message and the ecc are corrected (if possible of course).
    Pro tip: if you know a few erasures positions, you can specify them in a list `erase_pos` to double the repair power. But you can also just specify an empty list.

    If the decoding fails, it will normally automatically check and raise a ReedSolomonError exception that you can handle.
    However if you want to manually check if the repaired message is correct, you can do so:
    >> rs.rs_check(rmes + recc, nsym)

    Read the sourcecode's comments for more infos about how it works, and for the various parameters you can setup if
    you need to interface with other RS codecs.
