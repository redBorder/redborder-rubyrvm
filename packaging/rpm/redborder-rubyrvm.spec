%define debug_package %{nil}

%global rvm_dir %{__rvmdir}
%global rvm_group rvm
%global rvm_version %{__rvmversion}
%global ruby_version %{__rubyversion}
%global bundler_version %{__bundlerversion}
%global rubygems_version %{__rubygemsversion}
#global __brp_mangle_shebangs_exclude_from test.ru|generate-darwin-source-and-headers.py|csvORG2dat.py 
#global __brp_mangle_shebangs_exclude_from %{__rvmdir}
%undefine __brp_mangle_shebangs

Name: redborder-rubyrvm
Version: %{__version}
Release: %{__release}%{?dist}
License: ASL 2.0
ExclusiveArch: x86_64
Summary: Rvm and ruby for redborder platform

Source0: rvm-%{rvm_version}.tar.gz
Source1: bundler-1.12.5.gem
Source2: bundle-0.0.1.gem
#Source3: chef-12.0.3.gem
Source3: chef-17.10.0.gem
Source4: Gemfile_global
Source5: Gemfile_web
#Source6: chef-zero-3.2.1.gem
Source6: chef-zero-15.0.11.gem
Source7: prettyprint-0.0.1.gem
Source8: ruby-2.2.4.tar.bz2
Source9: mimemagic-0.3.0.gem
Source10: redborder-consul-connector-0.0.6.gem
Source11: ilo-sdk-1.3.1.gem
Source12: aerospike-2.0.0.gem
Source13: ruby-druid-0.1.8.gem
Source14: audited-activerecord-4.0.0.gem
Source15: audited-4.0.0.gem
Source16: devise_ldap_authenticatable-0.8.1.gem

BuildRequires: libyaml-devel libffi-devel autoconf automake libtool bison postgresql-devel git
%if 0%{?rhel} < 9
BuildRequires: ImageMagick-devel = 6.7.8.9
%endif
%if 0%{?rhel} >= 9
BuildRequires: ImageMagick-devel
%endif
BuildRequires: gcc-c++ patch readline readline-devel zlib-devel openssl-devel procps-ng sqlite-devel
Requires: sed grep tar gzip bzip2 make file dialog chef

Obsoletes: rvm <= %{rvm_version}

%description
Rvm with ruby, gem, and bundler, packaged as an rpm for redborder platform.
System level install. Versions: ruby-%{ruby_version}, bundler-%{bundler_version} and
rubygems-%{rubygems_version}

%prep
%setup -q -n rvm-%{rvm_version}

%build
rvm_path="%{rvm_dir}" \
  rvm_man_path="%{_mandir}" \
  ./install --auto-dotfiles &>/dev/null

echo "" > %{rvm_dir}/gemsets/default.gems
echo "" > %{rvm_dir}/gemsets/global.gems

echo "
umask u=rwx,g=rwx,o=rx
rvm_path="%{rvm_dir}"
rvm_archives_path=%{rvm_dir}/archives
rvm_autolibs_flag=read-fail
" > /etc/rvmrc

cp -rf $RPM_SOURCE_DIR/* %{rvm_dir}/archives/
chgrp -R rvm %{rvm_dir}
chmod -R g+wxr %{rvm_dir}

%if 0%{?rhel} < 9
%{rvm_dir}/bin/rvm --verify-downloads 2 --disable-binary install %{ruby_version}
%endif

%if 0%{?rhel} >= 9
%{rvm_dir}/bin/rvm pkg install openssl
%{rvm_dir}/bin/rvm --verify-downloads 2 --disable-binary install %{ruby_version} -C --with-openssl-dir=%{rvm_dir}/usr
%endif 

echo "
current=ruby-%{ruby_version}
default=ruby-%{ruby_version}
" > %{rvm_dir}/config/alias

%{rvm_dir}/bin/rvm all do rvm use %{ruby_version} --default

%{rvm_dir}/bin/rvm all do ruby --version

# Create web gemset
%{rvm_dir}/bin/rvm all do rvm gemset create web

# install bundle gem
%{rvm_dir}/bin/rvm %{ruby_version}@global do gem install %{rvm_dir}/archives/bundler-*.gem
%{rvm_dir}/bin/rvm %{ruby_version}@global do gem install %{rvm_dir}/archives/bundle-*.gem
%{rvm_dir}/bin/rvm %{ruby_version}@global do gem install %{rvm_dir}/archives/chef-zero*.gem --no-doc
%{rvm_dir}/bin/rvm %{ruby_version}@global do gem install %{rvm_dir}/archives/chef-*.gem --no-doc
%{rvm_dir}/bin/rvm %{ruby_version}@global do gem install %{rvm_dir}/archives/prettyprint-*.gem --no-doc
%{rvm_dir}/bin/rvm %{ruby_version}@global do gem install %{rvm_dir}/archives/redborder-consul-connector-*.gem --no-doc
%{rvm_dir}/bin/rvm %{ruby_version}@global do gem install %{rvm_dir}/archives/ilo-*.gem --no-doc
%{rvm_dir}/bin/rvm %{ruby_version}@web do gem install %{rvm_dir}/archives/mimemagic-*.gem --no-doc

%if 0%{rhel} >= 9
export CFLAGS="-Wno-error=format-overflow"
%{rvm_dir}/bin/rvm %{ruby_version}@global do bundle config build.zookeeper --with-cflags="-O2 -pipe -march=native -Wno-error=format-overflow"
%{rvm_dir}/bin/rvm %{ruby_version}@web do bundle config build.zookeeper --with-cflags="-O2 -pipe -march=native -Wno-error=format-overflow"
%endif

%{rvm_dir}/bin/rvm %{ruby_version}@global do bundle install --gemfile=$RPM_SOURCE_DIR/Gemfile_global
#{rvm_dir}/bin/rvm %{ruby_version}@web do bundle install --gemfile=$RPM_SOURCE_DIR/Gemfile_web

#{rvm_dir}/bin/rvm %{ruby_version}@web do gem install %{rvm_dir}/archives/aerospike-*.gem --no-doc
#{rvm_dir}/bin/rvm %{ruby_version}@web do gem install %{rvm_dir}/archives/ruby-druid-*.gem --no-doc
#{rvm_dir}/bin/rvm %{ruby_version}@web do gem install %{rvm_dir}/archives/audited-*.gem --no-doc
#{rvm_dir}/bin/rvm %{ruby_version}@web do gem install %{rvm_dir}/archives/audited-activerecord-*.gem --no-doc
#{rvm_dir}/bin/rvm %{ruby_version}@web do gem install %{rvm_dir}/archives/devise_ldap_authenticatable-*.gem --no-doc

# Remove downloaded gems and files after compilation
rm -rf %{rvm_dir}/src/*
rm -rf %{rvm_dir}/log/*
rm -rf %{rvm_dir}/archives/*

%install
rm -rf $RPM_BUILD_ROOT/*
mkdir -p $RPM_BUILD_ROOT%{rvm_dir}
mkdir -p $RPM_BUILD_ROOT/etc
mkdir -p $RPM_BUILD_ROOT/etc/profile.d
mkdir -p $RPM_BUILD_ROOT/var/www/rb-rails

cp -rf %{rvm_dir}/* $RPM_BUILD_ROOT%{rvm_dir}/
cp /etc/profile.d/rvm.sh $RPM_BUILD_ROOT/etc/profile.d/rvm.sh
cp /etc/rvmrc $RPM_BUILD_ROOT/etc/rvmrc
#cp $RPM_SOURCE_DIR/Gemfile_web.lock $RPM_BUILD_ROOT/var/www/rb-rails/Gemfile.lock

chgrp -R rvm $RPM_BUILD_ROOT%{rvm_dir}
chmod -R g+wxr $RPM_BUILD_ROOT%{rvm_dir}

# clean unicorn and /usr/local references
for f in $(grep -l -r "#\!\s*/this/will/be/overwritten/or/wrapped/anyways/do/not/worry/ruby" $RPM_BUILD_ROOT%{rvm_dir}); do
  sed -i 's@#\!\s*/this/will/be/overwritten/or/wrapped/anyways/do/not/worry/ruby@#!/usr/bin/ruby@' "$f" || :
done

for f in $(grep -l -r "#\!\s*/usr/local/bin/ruby" $RPM_BUILD_ROOT%{rvm_dir}); do
  sed -i 's@#\!\s*/usr/local/bin/ruby@#!/usr/bin/ruby@' "$f" ||:
done

for f in $(grep -l -r "#\!\s*/usr/local/bin/macruby" $RPM_BUILD_ROOT%{rvm_dir}); do
  sed -i 's@#\!\s*/usr/local/bin/macruby@#!/usr/bin/ruby@' "$f" || :
done

for f in $(grep -l -r "#\!\s*/bin/perl" $RPM_BUILD_ROOT%{rvm_dir}); do
  sed -i 's@#\!\s*/bin/perl@#!/usr/bin/perl@' "$f" || :
done

%clean

%pre
getent group rvm >/dev/null || groupadd -r rvm

%post
/bin/bash --login -c "rvm use %{ruby_version} --default" || :
/bin/bash --login -c "rvm gemset use global --default" || :

%files
%{rvm_dir}
/etc/rvmrc
/etc/profile.d/rvm.sh

%changelog
* Thu Feb 09 2023 Luis Blanco <ljblanco@redborder.com> - 0.1.12-1
- Fixing broken dependencies for the web

* Wed Jan 27 2021 Miguel Negron <manegron@redborder.com> - 0.0.5-1
- Fixing broken dependencies

* Wed Jan 27 2021 Miguel Negron <manegron@redborder.com> - 0.0.4-1
- Fixing broken dependencies

* Mon Jan 25 2021 Miguel Negron <manegron@redborder.com> - 0.0.3-1
- Add ImageMagick specific version as requirement

* Tue Nov 22 2016 Juan J. Prieto <jjprieto@redborder.com> - 0.0.2-1
- Integrate all fix and latest gems. Also fix changelog in spec.

* Fri Nov 18 2016 Juan J. Prieto <jjprieto@redborder.com> - 0.0.1-1
- First commit and version
