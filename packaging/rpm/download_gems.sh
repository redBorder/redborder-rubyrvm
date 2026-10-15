#!/bin/bash

RVMVERSION=${RVMVERSION:="1.27.0"}
BUNDLERVERSION=${BUNDLERVERSION:="1.12.5"}
BUNDLEVERSION=${BUNDLEVERSION:="0.0.1"}
RUBYGEMSVERSION=${RUBYGEMSVERSION:="2.4.8"}
RUBYVERSION=${RUBYVERSION:="3.4.11"}

mkdir -p SOURCES

cp Gemfile* SOURCES

# Basic packages

[ ! -f SOURCES/rvm-${RVMVERSION}.tar.gz ] && wget --no-check-certificate https://github.com/rvm/rvm/archive/${RVMVERSION}.tar.gz -O SOURCES/rvm-${RVMVERSION}.tar.gz
# The rubies are published under pub/ruby/<major>.<minor>/. There is no .tar.bz2
# for ruby >= 3.4: rvm looks for the .tar.gz
[ ! -s SOURCES/ruby-${RUBYVERSION}.tar.gz ] && wget --no-check-certificate https://cache.ruby-lang.org/pub/ruby/${RUBYVERSION%.*}/ruby-${RUBYVERSION}.tar.gz -O SOURCES/ruby-${RUBYVERSION}.tar.gz
[ ! -f SOURCES/rubygems-${RUBYGEMSVERSION}.tar.gz ] && wget --no-check-certificate https://rubygems.org/rubygems/rubygems-${RUBYGEMSVERSION}.tgz -O SOURCES/rubygems-${RUBYGEMSVERSION}.tar.gz
[ ! -f SOURCES/bundle-${BUNDLEVERSION}.gem ] && wget --no-check-certificate https://rubygems.org/downloads/bundle-${BUNDLEVERSION}.gem -O SOURCES/bundle-${BUNDLEVERSION}.gem
[ ! -f SOURCES/bundler-${BUNDLERVERSION}.gem ] && wget --no-check-certificate https://rubygems.org/downloads/bundler-${BUNDLERVERSION}.gem -O SOURCES/bundler-${BUNDLERVERSION}.gem

exit 0
