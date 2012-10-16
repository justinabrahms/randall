PLIST_FILENAME=com.justinlilly.randall.plist
PLIST_DEST=/Library/LaunchDaemons/$(PLIST_FILENAME)

all: randall.plist

randall.plist: base.m4 randall.plist.m4
	m4 $^ > $(PLIST_FILENAME)

install: randall.plist
	sudo cp $(PWD)/$(PLIST_FILENAME) /Library/LaunchDaemons/
	sudo chmod 0644 $(PLIST_DEST)
	sudo chown root $(PLIST_DEST)
	sudo chgrp wheel $(PLIST_DEST)
	sudo launchctl load $(PLIST_DEST)

clean:
	rm $(PWD)/$(PLIST_FILENAME)

stop:
	sudo launchctl unload $(PLIST_DEST)

start:
	sudo launchctl load $(PLIST_DEST)

restart:
	sudo launchctl unload $(PLIST_DEST)
	sudo launchctl load $(PLIST_DEST)

uninstall: stop
	sudo rm $(PLIST_DEST)
