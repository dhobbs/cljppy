from cljppy import partition_all, partial
from cljppy.core import identity
from cljppy.reducers.FuturePool import FuturePool


def fold(reduce_fn, coll, combine_fn=None, chunksize=2048):
    """
    Parallel reduce. Uses a pool of <cpus> workers, and splits the
    collection into <chunk_size=2048> size chunks.

    Initialises the reduce on each thread with combine_fn()
    (i.e. calling combine_fn with zero args)

    combine_fn defaults to reduce_fn
    """
    if combine_fn is None:
        combine_fn = reduce_fn

    r_fn = lambda s: reduce(reduce_fn, s, combine_fn())
    chunk_results = FuturePool(r_fn, partition_all(chunksize, coll), chunksize=1).deref()
    return reduce(combine_fn, chunk_results, combine_fn())


class Reducible(object):
    def __init__(self, collection, reducer=identity):
        if isinstance(collection, Reducible):
            self.__collection = collection
            self.__reducer = lambda x: collection.__reducer(reducer(x))

        else:
            self.__collection = collection
            self.__reducer = reducer

    def __iter__(self):
        return iter(self.__collection)

    def __len__(self):
        return len(self.__collection)

    def __str__(self):
        return "Reducible <" + str(self.__collection) + ">"

    def __repr__(self):
        return "Reducible <" + str(self.__collection) + ">"

    def reduce(self, f):
        return fold(self.__reducer(f), self.__collection)