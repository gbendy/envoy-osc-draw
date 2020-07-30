import json
import sys
import math
import os
import multiprocessing
import time
import traceback
import argparse

from sequence import Sequence


def run(args):
  try:
    data,first,last = args
    Sequence(data).render(first, last)
  except KeyboardInterrupt:
    return
  except Exception as e:
    print(traceback.format_exc())
    return    

def get_argparser():
  parser = argparse.ArgumentParser()
  parser.add_argument('--clean', '-c', action='store_true', help='Delete old pngs')
  parser.add_argument('json', nargs='?', help='The render.json file to read')
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
    if not options.json:
      return 0

  if not options.json:
    print("No render.json supplied")
    print(parser.format_usage())
    return 1

  with open(options.json) as f:
    data = json.load(f)

  if options.single_process:
    pool_size = 1
  else:
    pool_size = os.cpu_count()*2

  frames = data['frames']
  if frames < pool_size:
    pool_size = frames;
    count = 1
  else:
    count = math.floor(frames / pool_size) + 1
  jobs = []
  for f in range(0, pool_size):
    start = f*count
    end = start + count
    jobs.append([data,start,end if end < frames else frames ])

  if pool_size == 1:
    run(jobs[0])
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
