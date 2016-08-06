
import subprocess
import codecs
import sys
import re
import io
import time
import json
from os import listdir


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
    for p in get_latest_problems():
        spec = get_blob(p['problem_spec_hash'])
        fname = '../data/problems/%s.in' % p['problem_id']
        with open(fname, 'w') as f:
            f.write(spec)


solution_name_rx = re.compile('solution_'
                              '(?P<set_id>[0-9]+)_'
                              r'(?P<tag>[a-z0-9\-]+)_'
                              '(?P<version>[0-9]+).out')

def parse_solution_fname(fname):
    m = re.match(solution_name_rx, fname)
    return { 'fname': '../data/solutions/' + fname,
             'set_id': int(m.group('set_id')),
             'tag': '%s_%s' % (m.group('tag'), m.group('version')) }


def filter_solutions(tag):
    files = [ parse_solution_fname(f) for f in listdir("../data/solutions") ]
    files = [ f for f in files if (tag == None or f['tag'] == tag) ]
    files.sort(key = lambda f: f['set_id'])
    return files


def send_all_solutions(tag):
    filtered = filter_solutions(tag)
    for f in filtered:
        response = send_solution(f['set_id'], f['fname'])
        if response is None:
            return
        print(response)
