import binascii
import sys
import time
import urllib.request

def isValidSignature(file, signature):
    start = time.perf_counter()
    try:
        response = urllib.request.urlopen('http://localhost:9000/test?file=' + file + '&signature=' + signature)
        end = time.perf_counter()
        if response.status != 200:
            raise Exception('unexpected status ' + str(response.status))
        return (True, end - start)
    except urllib.error.HTTPError as e:
        end = time.perf_counter()
        if e.code != 500:
            raise
        return (False, end - start)

def guessNextByte(file, knownBytes):
    suffixlen = 20 - len(knownBytes)
    expectedDuration = 0.05 * len(knownBytes) + 0.01
    start = time.perf_counter()

    def print_info(i):
        end = time.perf_counter()
        print('Made {0} requests in {1:.2f}s; rps = {2:.2f}, max rps = {3:.2f}'.format(i, end - start, i / (end - start), 1 / expectedDuration))

    for i in range(256):
        suffix = bytes([i]) + (b'\x00' * (suffixlen - 1))
        signature = knownBytes + suffix
        _, duration = isValidSignature(file, binascii.hexlify(signature).decode('ascii'))
        if duration > expectedDuration + 0.04:
            print_info(i)
            return knownBytes + bytes([i])

    raise Exception('unexpected')

if __name__ == '__main__':
    file = sys.argv[1]
    knownBytes = b''
    knownBytes = guessNextByte(file, knownBytes)
    print(binascii.hexlify(knownBytes))
