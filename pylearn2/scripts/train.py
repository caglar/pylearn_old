#!/bin/env python
"""
Script implementing the logic for training pylearn2 models.

This is intended to be a "driver" for most training experiments. A user
specifies an object hierarchy in a configuration file using a dictionary-like
syntax and this script takes care of the rest.

For example configuration files that are consumable by this script, see

    pylearn2/scripts/train_example
    pylearn2/scripts/autoencoder_example
"""
# Standard library imports
import argparse
import datetime
import gc
import os
import warnings

# Third-party imports
import numpy as np

# Local imports
import pylearn2.config.yaml_parse
from pylearn2.utils import serial
from pylearn2.utils import environ
from pylearn2.monitor import Monitor
from pylearn2.train import Train


class FeatureDump(object):
    def __init__(self, encoder, dataset, path, batch_size=None, topo=False):
        self.encoder = encoder
        self.dataset = dataset
        self.path = path
        self.batch_size = batch_size
        self.topo = topo

    def main_loop(self):
        if self.batch_size is None:
            if self.topo:
                data = self.dataset.get_topological_view()
            else:
                data = self.dataset.get_design_matrix()
            output = self.encoder.perform(data)
        else:
            myiterator = self.dataset.iterator(mode='sequential',
                                               batch_size=self.batch_size,
                                               topo=self.topo)
            chunks = []
            for data in myiterator:
                chunks.append(self.encoder.perform(data))
            output = np.concatenate(chunks)
        np.save(self.path, output)


def make_argument_parser():
    parser = argparse.ArgumentParser(
        description="Launch an experiment from a YAML configuration file.",
        epilog='\n'.join(__doc__.strip().split('\n')[1:]).strip(),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('config', action='store',
                        choices=None,
                        help='A YAML configuration file specifying the '
                             'training procedure')
    return parser


if __name__ == "__main__":
    parser = make_argument_parser()
    args = parser.parse_args()
    train_obj = serial.load_train_file(args.config)
    try:
        iter(train_obj)
        iterable = True
    except TypeError as e:
        iterable = False
    if iterable:
        for number, subobj in enumerate(iter(train_obj)):
            # Publish a variable indicating the training phase.
            phase_variable = 'PYLEARN2_TRAIN_PHASE'
            phase_value = 'phase%d' % (number + 1)
            os.environ[phase_variable] = phase_value
            os.putenv(phase_variable, phase_value)

            # Execute this training phase.
            subobj.main_loop()

            # Clean up, in case there's a lot of memory used that's
            # necessary for the next phase.
            del subobj
            gc.collect()
    else:
        train_obj.main_loop()
