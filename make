#!/usr/bin/env python3
import sys
sys.path.append(".")
import utils, argparse, subprocess
parser = argparse.ArgumentParser("lmao")
parser.add_argument('app', metavar='app', help='appname')          
parser.add_argument('--push', action='store_true')
parser.add_argument('--syntax', action='store_true')
parser.add_argument('--quiet', action='store_true')
args = parser.parse_args()
app = args.app
push = args.push
do_syntax_check = args.syntax
quiet = args.quiet
utils.make(app, push, do_syntax_check, quiet)
subprocess.call(["make", "clean"])
