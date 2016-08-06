
import subprocess
import codecs
import sys
import re
import io
import time
import json
from os import listdir
import os.path


api_key = '149-9813263d3c764afad44eeebcb61a4cd8'


def api_get_request(url) -> str:
    res = subprocess.check_output(
        ['curl',
         '--compressed',
         '-L',
         '-H', 'Expect:',
         '-H', 'X-API-Key: %s' % api_key,
         url ])
    time.sleep(2)
    return res.decode('utf-8')


def send_solution(id, fname) -> str:
    print('Sending %s...' % fname)
    res = subprocess.check_output(
        ['curl',
         '--compressed',
         '-L',
         "-X", "POST",
         '-H', 'Expect:',
         '-H', 'X-API-Key: %s' % api_key,
         '-F', 'problem_id=%d' % id,
         '-F', 'solution_spec=@%s' % fname,
         'http://2016sv.icfpcontest.org/api/solution/submit' ])
    time.sleep(2)
    return json.loads(res.decode('utf-8'))


def send_problem(timestamp, fname) -> str:
    res = subprocess.check_output(
        ['curl',
         '--compressed',
         '-L',
         "-X", "POST",
         '-H', 'Expect:',
         '-H', 'X-API-Key: %s' % api_key,
         '-F', 'solution_spec=@%s' % fname,
         '-F', 'publish_time=%d' % timestamp,
         'http://2016sv.icfpcontest.org/api/problem/submit' ])
    time.sleep(2)
    return json.loads(res.decode('utf-8'))


def get_hello() -> json:
    print('Hello, world...')
    res = api_get_request('http://2016sv.icfpcontest.org/api/hello')
    return json.loads(res)


def get_json_blob(hash) -> json:
    print('Getting blob %s...' % hash)
    res = api_get_request('http://2016sv.icfpcontest.org/api/blob/%s' % hash)
    return json.loads(res)


def get_blob(hash) -> json:
    print('Getting blob %s...' % hash)
    res = api_get_request('http://2016sv.icfpcontest.org/api/blob/%s' % hash)
    return res


def get_snapshot_list() -> json:
    print('Getting snapshot list...')
    res = api_get_request('http://2016sv.icfpcontest.org/api/snapshot/list')
    return json.loads(res)


def get_latest_snapshot() -> json:
    print('Getting latest snapshot...')
    l = get_snapshot_list()['snapshots'][-1]
    return get_json_blob(l['snapshot_hash'])


def get_latest_problems() -> json:
    print('Getting latest problems...')
    s = get_latest_snapshot()
    return s['problems']


def write_latest_problem_specs() -> json:
    print('Writing latest problem specs...')
    pr = get_latest_problems()
    hash = { p['problem_id'] : p['problem_spec_hash'] for p in pr }
    idxs = [p['problem_id'] for p in pr]
    
    def fname(idx):
        return '../data/problems/%s.in' % idx
    
    idxs = [p for p in idxs if not os.path.isfile(fname(p))]
    idxs.sort()
    n = len(idxs)
    for i, p in enumerate(idxs):
        print('')
        print('Getting problem %d (%d to go)...' % (p, n-i))
        spec = get_blob(hash[p])
        with io.open(fname(p), 'w') as f:
            f.write(spec)


problem_name_rx = re.compile('(?P<id>[0-9]+).in$')

def parse_problem_fname(fname):
    m = re.match(problem_name_rx, fname)
    if m is None:
        return None
    else:
        return { 'fname': '../data/problems/' + fname,
                 'id': int(m.group('id')) }


def filter_problems(lowIndex, highIndex):
    files = [ parse_problem_fname(f) for f in listdir("../data/problems") ]
    files = filter(None, files)

    def is_requested(f):
        return ((f['id'] >= lowIndex) and (f['id'] <= highIndex))

    files = [ f for f in files if is_requested(f) ]
    files.sort(key = lambda f: f['id'])
    return files


solution_name_rx = re.compile('solution_'
                              '(?P<set_id>[0-9]+)_'
                              r'(?P<tag>[a-z0-9\-]+)_'
                              '(?P<version>[0-9]+).out$')

def parse_solution_fname(fname):
    m = re.match(solution_name_rx, fname)
    if m is None:
        return None
    else:
        return { 'fname': '../data/solutions/' + fname,
                 'set_id': int(m.group('set_id')),
                 'tag': '%s_%s' % (m.group('tag'), m.group('version')) }


def filter_solutions(tag):
    files = [ parse_solution_fname(f) for f in listdir("../data/solutions") ]
    files = filter(None, files)
    files = [ f for f in files if (tag == None or f['tag'] == tag) ]
    files.sort(key = lambda f: f['set_id'])
    return files

def send_solution_logged(id, fname):
    response = send_solution(id, fname)
    if response is None:
        print('There was no response!')
        return None
    print(response)

    response_fname = fname + '.response'
    print(response_fname)
    with io.open(response_fname, 'wt') as f:
        f.write(json.dumps(response))
    return response

def send_all_solutions(tag):
    filtered = filter_solutions(tag)
    for f in filtered:
        send_solution_logged(f['set_id'], f['fname'])


def solve_problem(executable, p, iters = None):
    print('Solving problem %s with %s...' % (p['id'], executable))
    try:
        if iters is None:
            sol = subprocess.check_output([executable, "-in", p['fname']])
        else:
            sol = subprocess.check_output([executable, "-in", p['fname'],
                                           "-iterations", iters])
        print('ok')
        return sol.decode('utf-8')

    except subprocess.CalledProcessError as ex: # error code <> 0
        print("-------- Error --------")
        print(ex)
        return None
