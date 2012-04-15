# This Makefile is just a cheatsheet to remind me of some commonly used
# commands. I'm generally executing these on OSX with up-to-date Gnu binaries
# foremost on the PATH, or on Ubuntu, or on WindowsXP/7 with Cygwin binaries
# foremost on the PATH.


NAME=genesis


test:
	python -m unittest discover $(NAME)/tests
.PHONY: test

tags:
	ctags -R --languages=python .
.PHONY: tags

clean:
	rm -rf build dist MANIFEST
	find . -name '*.py[oc]' -exec rm {} \;
.PHONY: clean

sdist: clean
	python setup.py sdist --formats=zip,gztar
.PHONY: sdist

register: clean
	python setup.py sdist --formats=zip,gztar register 
.PHONY: register
 
upload: clean
	python setup.py sdist --formats=zip,gztar register upload
.PHONY: upload

