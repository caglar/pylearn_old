"""

Classes that define how vector spaces are formatted

Most of our models can be viewed as linearly transforming
one vector space to another. These classes define how the
vector spaces should be represented as theano/numpy
variables.

For example, the VectorSpace class just represents a
vector space with a vector, and the model can transform
between spaces with a matrix multiply. The Conv2DSpace
represents a vector space as an image, and the model
can transform between spaces with a 2D convolution.

To make models as general as possible, models should be
written in terms of Spaces, rather than in terms of
numbers of hidden units, etc. The model should also be
written to transform between spaces using a generic
linear transformer from the pylearn2.linear module.

The Space class is needed so that the model can specify
what kinds of inputs it needs and what kinds of outputs
it will produce when communicating with other parts of
the library. The model also uses Space objects internally
to allocate parameters like hidden unit bias terms in
the right space.

"""

import numpy as np
import theano.tensor as T
from theano.tensor import TensorType
from theano import config
import functools

class Space(object):
    """ Defines a vector space that can be transformed by a linear operator """

    def get_origin(self):
        """ Returns the origin in this space """
        raise NotImplementedError()

    def get_origin_batch(self, n):
        """ Returns a batch of n copies of the origin """
        raise NotImplementedError()

    def make_theano_batch(self, name = None, dtype = None):
        """ Returns a theano tensor capable of representing a batch of points
            in the space """

        raise NotImplementedError()


class VectorSpace(Space):
    """ Defines a space whose points are defined as fixed-length vectors """

    def __init__(self, dim):
        """

        dim: the length of the fixed-length vector

        """

        self.dim = dim

    @functools.wraps(Space.get_origin)
    def get_origin(self):

        return np.zeros((self.dim,))

    @functools.wraps(Space.get_origin_batch)
    def get_origin_batch(self, n):

        return np.zeros((n,self.dim))

    @functools.wraps(Space.make_theano_batch)
    def make_theano_batch(self, name = None, dtype = None):

        if dtype is None:
            dtype = config.floatX

        return T.matrix(name = name, dtype = dtype)


class Conv2DSpace(Space):
    """ Defines a space whose points are defined as multi-channel images """

    def __init__(self, shape, nchannels):
        """
            shape: (rows, cols)
            nchannels: # of channels in the image
        """

        self.shape = shape
        self.nchannels = nchannels

    @functools.wraps(Space.get_origin)
    def get_origin(self):
        return np.zeros((self.shape[0], self.shape[1], self.nchannels))

    @functools.wraps(Space.get_origin_batch)
    def get_origin_batch(self, n):
        return np.zeros((n, self.shape[0], self.shape[1], self.nchannels))

    @functools.wraps(Space.make_theano_batch)
    def make_theano_batch(self, name = None, dtype = None):

        if dtype is None:
            dtype = config.floatX

        return TensorType( dtype = dtype, broadcastable = (False, False, False, self.nchannels == 1) )(name = name)
