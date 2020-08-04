import json
import sys
import math
import os
import multiprocessing
import time
import traceback
import argparse
from importlib import import_module

from sequence import Sequence

def import_data(path):
  try:
    mod = import_module(path)
    return mod.render
  except ModuleNotFoundError as e:
    print("Could not import python module:", path)
  except AttributeError as e:
    print(f"Module {path} does not contain a render object.")
  return None


def run(args, data=None):
  try:
    path,first,last = args
    if not data:
      data = import_data(path)
    Sequence(data).render(first, last)
  except KeyboardInterrupt:
    return
  except Exception as e:
    print(traceback.format_exc())
    return    

def get_argparser():
  parser = argparse.ArgumentParser()
  parser.add_argument('--clean', '-c', action='store_true', help='Delete old pngs')
  parser.add_argument('--python', '-p', type=str, help='The path of the python render object to render')
  parser.add_argument('--single-process', '-s', action='store_true', help='Run without parallelism - good for debugging')
  return parser

def main(argv):
  parser = get_argparser()
  options = parser.parse_args()

  start_time = time.time()

  if options.clean:
    print ("Cleaning old pngs...", end="")
    os.system("rm *.png")
    print (" Done")
    if not options.python:
      return 0

  if options.python:
    data = import_data(options.python)
    if data is None:
      return 1

  if options.single_process:
    pool_size = 1
  else:
    pool_size = os.cpu_count()*2

  frames = data['frames']
  if frames < pool_size:
    pool_size = frames;
    count = 1
  elif frames % pool_size == 0:
    count = frames // pool_size
  else:
    count = frames // pool_size + 1
  jobs = []
  for f in range(0, pool_size):
    start = f*count
    end = start + count
    jobs.append([options.python,start,end if end < frames else frames ])

  if pool_size == 1:
    run(jobs[0], data=data)
  else:
    pool = multiprocessing.Pool(pool_size)
    try:
      pool.map(run, jobs)
      pool.close()
      pool.join()
    except KeyboardInterrupt:
      # Allow ^C to interrupt from any thread.
      print("Caught KeyboardInterrupt, terminating workers")
      pool.terminate()

   #Sequence(data).render()
  print("--- {} seconds ---" .format(time.time() - start_time))

if '__main__' == __name__:
  sys.exit(main(sys.argv[1:]))
