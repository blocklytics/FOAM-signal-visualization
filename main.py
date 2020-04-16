"""
Access the module from the command line.
Miha Lotric, April 2020
"""


import argparse

from signal_visualizer.visualizer import visual_from_signal


parser = argparse.ArgumentParser()
parser.add_argument('signal_id', type=int)
parser.add_argument('--save', nargs='?', const='default')
parser.add_argument('--show', action='store_true')
args = parser.parse_args()
save_as_ = f'./media/output/signals/{args.signal_id}.png' if args.save == 'default' else args.save

visual_from_signal(args.signal_id, show=args.show, save_as=save_as_)
