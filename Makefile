all: rpm

rpm:
	$(MAKE) -C packaging/rpm

clean:
	rm -rf SOURCES pkgs
