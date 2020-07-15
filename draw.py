import json
import sys
import math
import os
import multiprocessing
import time
import traceback

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

def main(argv):
  start_time = time.time()

  if len(argv) == 0:
    print('usage: {} render.json'.format(sys.argv[0]))
    return 1
  
  with open(argv[0]) as f:
    data = json.load(f)

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
