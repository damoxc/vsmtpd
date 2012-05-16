#!/usr/bin/make -f

GOPATH = $(CURDIR)
CGO_LDFLAGS = "-L/usr/lib/python2.7 -lpython2.7"
CGO_CFLAGS = "-I/usr/include/python2.7 -fno-strict-aliasing -DNDEBUG -g -fwrapv -O2 -Wall -g -fstack-protector --param=ssp-buffer-size=4 -Wformat -Wformat-security -Werror=format-security"
GO_LDFLAGS = "-s"

.PHONY: vsmtpd vsmtpd-py

vsmtpd:
	GOPATH=$(GOPATH) go build -ldflags $(GO_LDFLAGS) vsmtpd

vsmtpd-py:
	GOPATH=$(GOPATH) CGO_LDFLAGS=$(CGO_LDFLAGS) CGO_CFLAGS=$(CGO_CFLAGS) go build -ldflags $(GO_LDFLAGS) vsmtpd-py
