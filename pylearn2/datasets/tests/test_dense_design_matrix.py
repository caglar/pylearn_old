import numpy as np

from pylearn2.datasets.dense_design_matrix import DenseDesignMatrix
from pylearn2.datasets.dense_design_matrix import DefaultViewConverter
from pylearn2.utils import serial


def test_init_with_X_or_topo():
    #tests that constructing with topo_view works
    #tests that construction with design matrix works
    #tests that conversion from topo_view to design matrix and back works
    #tests that conversion the other way works too
    rng = np.random.RandomState([1,2,3])
    topo_view = rng.randn(5,2,2,3)
    d1 = DenseDesignMatrix(topo_view = topo_view)
    X = d1.get_design_matrix()
    d2 = DenseDesignMatrix(X = X, view_converter = d1.view_converter)
    topo_view_2 = d2.get_topological_view()
    assert np.allclose(topo_view,topo_view_2)
    X = rng.randn(*X.shape)
    topo_view_3 = d2.get_topological_view(X)
    X2 = d2.get_design_matrix(topo_view_3)
    assert np.allclose(X,X2)


def test_init_with_vc():
    d = DenseDesignMatrix(view_converter = DefaultViewConverter([1,2,3]))

def test_split_datasets():
    #Load and create ddm from cifar100
    path = "/data/lisa/data/cifar100/cifar-100-python/train"
    obj = serial.load(path)
    X = obj['data']

    assert X.max() == 255.
    assert X.min() == 0.

    X = np.cast['float32'](X)
    y = None #not implemented yet

    view_converter = DefaultViewConverter((32,32,3))

    ddm = DenseDesignMatrix(X = X, y =y, view_converter = view_converter)

    assert not np.any(np.isnan(ddm.X))
    ddm.y_fine = np.asarray(obj['fine_labels'])
    ddm.y_coarse = np.asarray(obj['coarse_labels'])
    (train, valid) = ddm.split_dataset_holdout(split_prop=0.5)
    print train.shape
    print valid.shape

def test_split_nfold_datasets():
    #Load and create ddm from cifar100
    path = "/data/lisa/data/cifar100/cifar-100-python/train"
    obj = serial.load(path)
    X = obj['data']

    assert X.max() == 255.
    assert X.min() == 0.

    X = np.cast['float32'](X)
    y = None #not implemented yet

    view_converter = DefaultViewConverter((32,32,3))

    ddm = DenseDesignMatrix(X = X, y =y, view_converter = view_converter)

    assert not np.any(np.isnan(ddm.X))
    ddm.y_fine = np.asarray(obj['fine_labels'])
    ddm.y_coarse = np.asarray(obj['coarse_labels'])
    folds = ddm.split_dataset_nfolds(10)
    print folds[0].shape

#test_split_datasets()
#test_split_nfold_datasets()
