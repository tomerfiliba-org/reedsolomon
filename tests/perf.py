# Copyright FranzForstmayr 2021
# Copyright Stephen Karl Larroque lrq3000 2021

import sys
import numpy as np
from reedsolo import RSCodec
from creedsolo import RSCodec as cRSCodec
import perfplot
import itertools

name = f'perf_v{sys.version_info.major}.{sys.version_info.minor}'

def func(rscoder, array):
    enc = rscoder.encode(array)
    return rscoder.decode(enc)[0]

codecs = {
    "p": RSCodec,
    "c": cRSCodec
}

nsym = [8, 16]

codecs_nsyms = [myfunc(x) for myfunc, x in itertools.product(codecs.values(), nsym)]
codecs_nsyms_names = ["%s%i" % (x1, x2) for x1, x2 in itertools.product(codecs.keys(), nsym)]

out = perfplot.bench(
    setup = lambda n: np.random.randint(0,255,size=n, dtype=np.uint8),
    kernels = [
        lambda a: func(codec, a) for codec in codecs_nsyms
    ],
    labels = [codec_name for codec_name in codecs_nsyms_names],
    n_range = [2 ** k for k in range(20)],
)
out.show()
out.save(name + ".png", transparent=True, bbox_inches="tight")
