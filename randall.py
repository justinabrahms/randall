#!/usr/bin/env python

from flask import Flask, redirect, request, render_template, flash, url_for
import os
import re
import shutil

class Randall(object):
    def __init__(self):
        self._app = Flask("PrivateUrls")
        self._app.secret_key = os.urandom(32)
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
        to_write = []
        shutil.copy('/etc/hosts', '/etc/hosts.bak')
        with open('/etc/hosts', 'r+') as hosts_file:
            for line in hosts_file.readlines():
                # preserve things that aren't ours
                if '# =>' not in line:
                    to_write.append(line)
            for key, value in self._mappings.iteritems():
                to_write.append("127.0.0.1\t%s # => %s\n" % (key, value))
            hosts_file.seek(0)
            hosts_file.truncate(0)
            hosts_file.writelines(to_write)

    def add_mapping(self, short_name, url):
        self._mappings[short_name] = url
        self.flush()

    def remove_mapping(self, short_name):
        del self._mappings[short_name]
        self.flush()

    def redirection_handler(self):
        """Serves the redirecting http server."""
        if request.host in self._mappings:
            return redirect(self._mappings[request.host])
        # We were directly navigated to.
        return render_template("index.html",
                               css=url_for('static', filename='randall.css'),
                               remembered=self._mappings)

    def new_url_handler(self):
        short_name = request.form['short_name']
        url = request.form['url']
        # TODO: validate url looks like a real one.
        self.add_mapping(short_name, url)
        flash("Added mapping for %s" % short_name)
        return redirect('/')

    def forget_url_handler(self):
        short_name = request.form['short_name']
        self.remove_mapping(short_name)
        flash("Removed mapping for %s" % short_name)
        return redirect('/')

    def serve(self):
        self._app.add_url_rule('/', view_func=self.redirection_handler)
        self._app.add_url_rule('/', view_func=self.new_url_handler, methods=("POST",))
        self._app.add_url_rule('/delete', view_func=self.forget_url_handler, methods=("POST",))
        # TODO: Pass in flag for if debug or not.
        self._app.run(port=80)

if __name__ == '__main__':
    # TODO: ensure this is run with sudo privs.
    s = Randall()
    s.serve()
