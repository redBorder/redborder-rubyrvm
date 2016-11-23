#!/bin/bash

RVM_VERSION=${RVM_VERSION:="1.27.0"}
BUNDLER_VERSION=${BUNDLER_VERSION:="1.12.5"}
RUBYGEMS_VERSION=${RUBYGEMS_VERSION:="2.4.8"}
RUBY_VERSION=${RUBY_VERSION:="2.2.4"}

mkdir -p SOURCES

# knife-acl and chef gem
[ ! -f SOURCES/knife-acl-1.0.3.gem ] && wget --no-check-certificate https://rubygems.org/downloads/knife-acl-1.0.3.gem -O SOURCES/knife-acl-1.0.3.gem
if [ ! -f SOURCES/chef-12.0.3.gem ]; then
	wget --no-check-certificate https://rubygems.org/downloads/chef-12.0.3.gem -O SOURCES/chef-12.0.3.gem
	# Patch chef gem
	pushd SOURCES &>/dev/null
	gem unpack ./chef-12.0.3.gem --target=tmp
	pushd tmp &>/dev/null
	patch -p1 <../../../../resources/data_bag_item.patch
	popd &>/dev/null &>/dev/null
	gem spec ./chef-12.0.3.gem --ruby > tmp/chef-12.0.3/chef-12.0.3.gemspec
	pushd tmp/chef-12.0.3 &>/dev/null
	gem build chef-12.0.3.gemspec
	popd &>/dev/null
	rm -f chef-12.0.3.gem
	mv tmp/chef-12.0.3/chef-12.0.3.gem .
	popd &>/dev/null
fi

# Basic packages
[ ! -f SOURCES/rvm-${RVM_VERSION}.tar.gz ] && wget --no-check-certificate https://github.com/rvm/rvm/archive/${RVM_VERSION}.tar.gz -O SOURCES/rvm-${RVM_VERSION}.tar.gz
[ ! -f SOURCES/ruby-${RUBY_VERSION}.tar.bz2 ] && wget --no-check-certificate https://ftp.ruby-lang.org/pub/ruby/2.2/ruby-${RUBY_VERSION}.tar.bz2 -O SOURCES/ruby-${RUBY_VERSION}.tar.bz2
[ ! -f SOURCES/rubygems-${RUBYGEMS_VERSION}.tar.gz ] && wget --no-check-certificate https://rubygems.org/rubygems/rubygems-${RUBYGEMS_VERSION}.tgz -O SOURCES/rubygems-${RUBYGEMS_VERSION}.tar.gz

for vgem in $(cat list_rubygems.txt | grep -v "^#"); do
	[ ! -f SOURCES/${vgem} ] && wget --no-check-certificate https://rubygems.org/downloads/${vgem} -O SOURCES/${vgem}
done
