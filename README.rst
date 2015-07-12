Reed Solomon
============

A pure-python `universal errors-and-erasures Reed-Solomon Codec <http://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction>`_
, based on the wonderful tutorial at
`wikiversity <http://en.wikiversity.org/wiki/Reed%E2%80%93Solomon_codes_for_coders>`_,
written by "Bobmath" and "LRQ3000".

The code of wikiversity is here consolidated into a nice API with exceptions handling.
The algorithm can correct up to 2*e+v <= nsym, where e is the number of errors,
v the number of erasures and nsym = n-k = the number of ECC (error correction code) symbols.
This means that you can either correct exactly floor(nsym/2) errors, or nsym erasures
(errors where you know the position), and a combination of both errors and erasures.
The code should work on pretty much any reasonable version of python (2.4-3.2),
but I'm only testing on 2.5 - 3.2.

The codec has quite reasonable performances if you either use PyPy on the pure-python
implementation (reedsolo.py) or either if you compile the Cython extension creedsolo.py
(which is about 2x faster than PyPy). You can expect encoding rate of several MB/s.

.. note::
   The codec is universal, meaning that it can decode any message encoded by another RS encoder
   as long as you provide the correct parameters.
   Note however that even if the algorithms and calculations can support Galois Fields > 2^8, the
   current implementation is based on bytearray structures to get faster computations. But this is
   easily fixable, just change bytearray to array('i', [...]) and it should work flawlessly for any GF.

   The algorithm itself can handle messages up to (2^c_exp)-1 symbols, including the ECC symbols,
   and each symbol can only have a value of up to (2^c_exp)-1. By default, we use the field GF(2^8),
   which means that you are limited to values between 0 and 255 (perfect to represent a single hexadecimal
   symbol on computers, so you can encode any binary stream) and limited to messages+ecc of maximum
   length 255. However, you can "chunk" longer messages to fit them into the message length limit.
   The ``RSCodec`` class will automatically apply chunking, by splitting longer messages into chunks and
   encode/decode them separately; it shouldn't make a difference from an API perspective (ie, from your POV).

::

    >>> rs = RSCodec(10)
    >>> rs.encode([1,2,3,4])
    b'\x01\x02\x03\x04,\x9d\x1c+=\xf8h\xfa\x98M'
    >>> rs.encode(b'hello world')
    b'hello world\xed%T\xc4\xfd\xfd\x89\xf3\xa8\xaa'
    >>> rs.decode(b'hello world\xed%T\xc4\xfd\xfd\x89\xf3\xa8\xaa')
    b'hello world'
    >>> rs.decode(b'heXlo worXd\xed%T\xc4\xfdX\x89\xf3\xa8\xaa')     # 3 errors
    b'hello world'
    >>> rs.decode(b'hXXXo worXd\xed%T\xc4\xfdX\x89\xf3\xa8\xaa')     # 5 errors
    b'hello world'
    >>> rs.decode(b'hXXXo worXd\xed%T\xc4\xfdXX\xf3\xa8\xaa')        # 6 errors - fail
    Traceback (most recent call last):
      ...
    ReedSolomonError: Could not locate error

    >>> rs = RSCodec(12)
    >>> rs.encode(b'hello world')
    b'hello world?Ay\xb2\xbc\xdc\x01q\xb9\xe3\xe2='
    >>> rs.decode(b'hello worXXXXy\xb2XX\x01q\xb9\xe3\xe2=')         # 6 errors - ok
    b'hello world'

    If you want full control, you can skip the API and directly use the library as-is. Here's how:

    First you need to init the precomputed tables:
    >> init_tables(0x11d)
    Pro tip: if you get the error: ValueError: byte must be in range(0, 256), please check that your prime polynomial is correct for your field.

    Then to encode:
    >> mesecc = rs_encode_msg(mes, n-k)

    To decode:
    >> mes, ecc = rs_correct_msg(mes + ecc, n-k, erase_pos=erase_pos)
    
    If the decoding fails, it will normally automatically check and raise a ReedSolomonError exception that you can handle.
    However if you want to manually check if the repaired message is correct, you can do so:
    >> rsman.check(rmes + recc, k=k)

    Read the sourcecode's comments for more infos about how it works, and for the various parameters you can setup if
    you need to interface with other RS codecs.