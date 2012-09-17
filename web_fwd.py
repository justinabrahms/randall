#!/usr/bin/env python
from flask import Flask, redirect, request, render_template
import os
import re

class PrivateUrls(object):
    def __init__(self):
        self._app = Flask("PrivateUrls")
        self._mappings = {}
        self.refresh()

    def refresh(self):
        """Loads all mappings from /etc/hosts"""
        reg = re.compile(r'127.0.0.1\s+(\w+).*=>\s+(.*[^ ])\s+$')
        with open('/etc/hosts', 'r') as hosts_file:
            for line in hosts_file.readlines():
                result = re.search(reg, line)
                if result:
                    short_name, url = result.groups()
                    self._mappings[short_name] = url

    def flush(self):
        """Flushes mappings to /etc/hosts file"""
        # find all things that contain =>, remove them, build them from the
        # internal map, then repersist. Save old as backup.
        pass

    def add_mapping(self, short_name, url):
        self._mappings[short_name] = url
        self.flush()

    def redirection_handler(self):
        """Serves the redirecting http server."""
        if request.host in self._mappings:
            return redirect(self._mappings[request.host])
        # We were directly navigated to.
        return render_template("index.html", program=self.__class__.__name__)

    def admin(self):
        pass

    def serve(self):
        print self._mappings
        self._app.add_url_rule('/', view_func=self.redirection_handler)
        self._app.run(port=80, debug=True)


if __name__ == '__main__':
    # ensure you've run this as sudo.
    pp = PrivateUrls()
    pp.serve()
