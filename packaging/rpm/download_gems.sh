#!/bin/bash

RVMVERSION=${RVMVERSION:="1.27.0"}
BUNDLERVERSION=${BUNDLERVERSION:="1.12.5"}
BUNDLEVERSION=${BUNDLEVERSION:="0.0.1"}
RUBYGEMSVERSION=${RUBYGEMSVERSION:="2.4.8"}
RUBYVERSION=${RUBYVERSION:="2.2.4"}

mkdir -p SOURCES

cp Gemfile* SOURCES

# Patch chef-zero gem
if [ ! -f SOURCES/chef-zero-3.2.1.gem ]; then
	wget --no-check-certificate https://rubygems.org/downloads/chef-zero-3.2.1.gem -O SOURCES/chef-zero-3.2.1.gem
	pushd SOURCES &>/dev/null
	gem unpack ./chef-zero-3.2.1.gem --target=tmp
	gem spec ./chef-zero-3.2.1.gem --ruby > tmp/chef-zero-3.2.1/chef-zero-3.2.1.gemspec
	# Patch chef gem for rack gem version
	pushd tmp &>/dev/null
	patch -p1 <../../../../resources/chef-zero_rack_conflict.patch
	popd &>/dev/null
	pushd tmp/chef-zero-3.2.1 &>/dev/null
	gem build chef-zero-3.2.1.gemspec
	popd &>/dev/null
	rm -f chef-zero-3.2.1.gem
	mv tmp/chef-zero-3.2.1/chef-zero-3.2.1.gem  .
	popd &>/dev/null
fi

# Patch chef gem
if [ ! -f SOURCES/chef-12.0.3.gem ]; then
	wget --no-check-certificate https://rubygems.org/downloads/chef-12.0.3.gem -O SOURCES/chef-12.0.3.gem
	pushd SOURCES &>/dev/null
	gem unpack ./chef-12.0.3.gem --target=tmp
  # Patch chef gem - data_bag_item bug
	pushd tmp &>/dev/null
	patch -p1 <../../../../resources/data_bag_item.patch
	popd &>/dev/null &>/dev/null
	gem spec ./chef-12.0.3.gem --ruby > tmp/chef-12.0.3/chef-12.0.3.gemspec
	# Patch chef gem for rack gem version
	pushd tmp &>/dev/null
	patch -p1 <../../../../resources/chef_rack_conflict.patch
	popd &>/dev/null
	pushd tmp/chef-12.0.3 &>/dev/null
	gem build chef-12.0.3.gemspec
	popd &>/dev/null
	rm -f chef-12.0.3.gem
	mv tmp/chef-12.0.3/chef-12.0.3.gem .
	popd &>/dev/null
fi

# Basic packages

[ ! -f SOURCES/rvm-${RVMVERSION}.tar.gz ] && wget --no-check-certificate https://github.com/rvm/rvm/archive/${RVMVERSION}.tar.gz -O SOURCES/rvm-${RVMVERSION}.tar.gz
[ ! -f SOURCES/ruby-${RUBYVERSION}.tar.bz2 ] && wget --no-check-certificate https://ftp.ruby-lang.org/pub/ruby/2.2/ruby-${RUBYVERSION}.tar.bz2 -O SOURCES/ruby-${RUBYVERSION}.tar.bz2
[ ! -f SOURCES/rubygems-${RUBYGEMSVERSION}.tar.gz ] && wget --no-check-certificate https://rubygems.org/rubygems/rubygems-${RUBYGEMSVERSION}.tgz -O SOURCES/rubygems-${RUBYGEMSVERSION}.tar.gz
[ ! -f SOURCES/bundle-${BUNDLEVERSION}.gem ] && wget --no-check-certificate https://rubygems.org/downloads/bundle-${BUNDLEVERSION}.gem -O SOURCES/bundle-${BUNDLEVERSION}.gem
[ ! -f SOURCES/bundler-${BUNDLERVERSION}.gem ] && wget --no-check-certificate https://rubygems.org/downloads/bundler-${BUNDLERVERSION}.gem -O SOURCES/bundler-${BUNDLERVERSION}.gem

exit 0
