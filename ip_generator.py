from numpy.random import randint, random
from netaddr import IPNetwork, IPAddress
from pprint import pprint as pp
import numpy as np
from datetime import datetime, timedelta

MAX_VAL = 255**4

class IPGenerator:

    def set_excludes(self, excludes):
        self._excludes = sorted(excludes)
        self._build_valid_blocks()

    def __get_start_end(self, block):
        return block[0].value,block[-1].value


    def _build_valid_blocks(self):
        ex_start_stop = [ self.__get_start_end(e) for e in self._excludes ]
        valid = [[0,0,0]]
        i = 0
        while i< len(ex_start_stop):
            s,e = ex_start_stop[i]
            # print(i,s,e)
            if i+1 < len(ex_start_stop):
                ns,ne = ex_start_stop[i+1]
                if ns <= e:
                    # If the next end is greater than the curren end, just use next
                    # end as the current. This will create a new superblock
                    if ne >e:
                        e = ne
                    # Either we've created a new super block, or the next block is
                    # contained within this current block. In either case we can
                    # safely remove the next block
                    del ex_start_stop[i+1]
            valid[-1][1] = s
            valid[-1][2] = s - valid[-1][0]
            if valid[-1][2] == 0:
                del valid[-1]
            valid.append([e+1,0,0])
            i += 1

        # Final block should end with the max value allowed.
        valid[-1][1] = MAX_VAL
        valid[-1][2] = MAX_VAL - valid[-1][0]

        # Normalize the weights
        total = sum([e[-1] for e in valid])
        for i in range(len(valid)):
            valid[i].append(valid[i][-1]/total)

        self.valid_ranges = valid

    def __assert_valid(self, guess):
        return any([guess >=s and guess<e for s,e,l,w in self.valid_ranges])

    def check_valid_ips(self, ips):
        return [ ip for ip in ips if any([ip.value >=s and ip.value<e for s,e,l,w in self.valid_ranges]) ]
        

    def random_number_test(self, N=100000):
        for i in range(N):
            assert self.__assert_valid(valid, generate_random_value())

    def generate_random_value(self):
        rnd = random()
        for s,e,l,w in self.valid_ranges:
            if rnd<w:
                return randint(s,e)
            rnd -= w
        print(rnd)
        raise ValueError

    def generate_ip(self):
        return IPAddress(self.generate_random_value())

    def benchmark_speed(self, N=100000):
        d0 = datetime.now()
        for i in range(N):
            assert self.__assert_valid(self.generate_random_value())
        dt = (datetime.now() - d0).total_seconds()
        print('Performing generate at a rate of {:.2f}/second'.format(N/dt))

if __name__ == '__main__':
    with open('exclude.list', 'r') as f:
        excludes = [ IPNetwork(l.strip().rstrip()) for l in f.readlines() ]
    excludes.append(IPNetwork('0.0.0.0/16'))
    ipgen = IPGenerator()
    ipgen.set_excludes(excludes)
    # valid = build_valid_blocks(excludes)

    # random_number_test(valid)
    ipgen.benchmark_speed()
