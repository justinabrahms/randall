import socket
import logging

logger = logging.getLogger(__name__)

class DNSQuery:
    """Initially from
    http://code.activestate.com/recipes/491264-mini-fake-dns-server/"""

    domains_to_track = [] # list of short urls
    fallback_dns = ["8.8.8.8", "8.8.4.4"] # list of ips for fallback dns.

    def __init__(self, data):
        self.data=data
        self.domain=''
        query_type = (ord(data[2]) >> 3) & 15   # Opcode bits
        if query_type == 0:                     # Standard query
            print 'standard query'

            ini=12
            lon=ord(data[ini])
            while lon != 0:
                self.domain+=data[ini+1:ini+lon+1]+'.'
                ini+=lon+1
                lon=ord(data[ini])
            print 'domain is: %s' % self.domain

    def response(self, ip):
        packet=''
        print "Domain we got was %s" % self.domain
        if self.domain and self.domain == 'm':
            logger.debug("Intercepting request for %s.", self.domain)
            packet+=self.data[:2] + "\x81\x80"
            packet+=self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'   # Questions and Answers Counts
            packet+=self.data[12:]                                         # Original Domain Name Question
            packet+='\xc0\x0c'                                             # Pointer to domain name
            packet+='\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'             # Response type, ttl and resource data length -> 4 bytes
            packet+=str.join('',map(lambda x: chr(int(x)), ip.split('.'))) # 4bytes of IP
        else:
            logger.debug("Proxying request for %s to real dns server.", self.domain)
            # proxy back to a "real" DNS server.
            upstream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            upstream.connect((self.fallback_dns[0], 53))
            upstream.sendall(self.data)
            # @@@ Why 1024? Why not 512 or 2084?
            # @@@ Is it okay to set it to packet here?
            packet = upstream.recv(1024)

        return packet

if __name__ == '__main__':
    # @@@ flags for ip to respond with.
    ip='127.0.0.1'
    print 'pyminifakeDNS:: dom.query. 60 IN A %s' % ip

    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.bind(('127.0.0.1',53))

    try:
        while 1:
            data, addr = udps.recvfrom(1024)
            p=DNSQuery(data)
            udps.sendto(p.response(ip), addr)
            print 'Response: %s -> %s' % (p.domain, ip)
    except KeyboardInterrupt:
        print 'Finished'
        udps.close()
