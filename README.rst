Reed Solomon
============

A pure-python `Reed Solomon <http://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction>`_
encoder/decoder, based on the wonderful tutorial at 
`wikiversity <http://en.wikiversity.org/wiki/Reed%E2%80%93Solomon_codes_for_coders>`_,
written by "Bobmath".

I only consolidated the code a little and added exceptions and a simple API. 
To my understanding, the algorithm can correct up to ``nsym/2`` of the errors in 
the message, where ``nsym`` is the number of bytes in the error correction code.
The code should work on pretty much any reasonable version of python (2.4-3.2), 
but I'm only testing on 2.6-3.2.

.. note::
   I claim not authorship of the code, and take no responsibility on the correctness 
   of the algorithm. It's way too much finite-field algebra for me :)
   
   I've released this package as I needed an ECC codec for another project I'm working on, 
   and I couldn't find anything on the web (that still works).

::

    >>> rs = RSCodec(10)
    >>> rs.encode([1,2,3,4])
    '\x01\x02\x03\x04,\x9d\x1c+=\xf8h\xfa\x98M'
    >>> rs.encode("hello world")
    'hello world\xed%T\xc4\xfd\xfd\x89\xf3\xa8\xaa'
    >>> rs.decode(b'hello world\xed%T\xc4\xfd\xfd\x89\xf3\xa8\xaa')
    'hello world'
    >>> rs.decode(b'hello worXd\xed%T\xc4\xfd\xfd\x89\xf3\xa8\xaa')  # 1 error
    'hello world'
    >>> rs.decode(b'heXlo worXd\xed%T\xc4\xfdX\x89\xf3\xa8\xaa')     # 3 errors
    'hello world'
    >>> rs.decode(b'hXXlo worXd\xed%T\xc4\xfdX\x89\xf3\xa8\xaa')     # 4 errors
    'hello world'
    >>> rs.decode(b'hXXXo worXd\xed%T\xc4\xfdX\x89\xf3\xa8\xaa')     # 5 errors
    'hello world'
    >>> rs.decode(b'hXXXo worXd\xed%T\xc4\xfdXX\xf3\xa8\xaa')        # 6 errors - fail
    Traceback (most recent call last):
      ...
    ReedSolomonError: Could not locate error

    >>> rs = RSCodec(12)
    >>> rs.encode("hello world")
    'hello world?Ay\xb2\xbc\xdc\x01q\xb9\xe3\xe2='
    >>> rs.decode(b'hello worXXXXy\xb2XX\x01q\xb9\xe3\xe2=')         # 6 errors - ok
    'hello world'



