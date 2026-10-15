%define debug_package %{nil}

%global rvm_dir %{__rvmdir}
%global rvm_group rvm
%global rvm_version %{__rvmversion}
%global ruby_version %{__rubyversion}
%global bundler_version %{__bundlerversion}
%global rubygems_version %{__rubygemsversion}
%undefine __brp_mangle_shebangs
# libv8-node (the JS runtime of the webui) ships a prebuilt static V8. The
# post-install strip scripts unpack that archive and fail on it
%global __brp_strip_lto %{nil}
%global __brp_strip_static_archive %{nil}

%global __requires_exclude ^libMagick.*\\.so.*$

Name: redborder-rubyrvm
Version: %{__version}
Release: %{__release}%{?dist}
License: ASL 2.0
ExclusiveArch: x86_64
Summary: Rvm and ruby for redborder platform

Source0: rvm-%{rvm_version}.tar.gz
Source1: Gemfile_global
Source2: Gemfile_web
# The global bundle is locked: the gems uploaded to geminabox later do not change it
Source3: Gemfile_global.lock

BuildRequires: libyaml-devel libffi-devel autoconf automake libtool bison postgresql-devel git
BuildRequires: ImageMagick-devel
BuildRequires: gcc-c++ patch readline readline-devel zlib-devel openssl-devel procps-ng sqlite-devel ruby

Requires: sed grep tar gzip bzip2 make file dialog ImageMagick

Obsoletes: rvm <= %{rvm_version}

%description
Rvm with ruby, gem, and bundler, packaged as an rpm for redborder platform.
System level install. Versions: ruby-%{ruby_version} (gemsets global for the platform
scripts and web for the webui), bundler-%{bundler_version} and rubygems-%{rubygems_version}

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
chmod -x %{rvm_dir}/hooks/after_use_textmate || :

# Install ruby within rvm. It is built against the system openssl 3
%{rvm_dir}/bin/rvm --verify-downloads 2 --disable-binary install %{ruby_version} -C --with-openssl-dir=/usr

# Setup default ruby version
echo "
current=ruby-%{ruby_version}
default=ruby-%{ruby_version}
" > %{rvm_dir}/config/alias
%{rvm_dir}/bin/rvm all do rvm use %{ruby_version} --default

# Setup CFLAGS
export CFLAGS="-Wno-error=format-overflow"
%{rvm_dir}/bin/rvm %{ruby_version} do bundle config set build.zookeeper --with-cflags="-O2 -pipe -march=native -Wno-error=format-overflow"
%{rvm_dir}/bin/rvm %{ruby_version} do bundle config set without 'development test'

# Install global gems (ruby-%{ruby_version}@global): the platform scripts
%{rvm_dir}/bin/rvm %{ruby_version}@global do bundle install --gemfile=$RPM_SOURCE_DIR/Gemfile_global

# Install web gems (ruby-%{ruby_version}@web): the webui
%{rvm_dir}/bin/rvm %{ruby_version} do rvm gemset create web
%{rvm_dir}/bin/rvm %{ruby_version}@web do bundle install --gemfile=$RPM_SOURCE_DIR/Gemfile_web

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
cp $RPM_SOURCE_DIR/Gemfile_web.lock $RPM_BUILD_ROOT/var/www/rb-rails/Gemfile.lock

# Configure rvm files permissions
chgrp -R rvm $RPM_BUILD_ROOT%{rvm_dir}
chmod -R g+wxr $RPM_BUILD_ROOT%{rvm_dir}

# Fix slangs
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
chmod -x %{rvm_dir}/hooks/after_use_textmate || :
/bin/bash --login -c "rvm use %{ruby_version} --default" || :
/bin/bash --login -c "rvm gemset use global --default" || :

%files
%{rvm_dir}
/etc/rvmrc
/etc/profile.d/rvm.sh
/var/www/rb-rails/Gemfile.lock
%attr(0644, root, root) %{rvm_dir}/hooks/after_use_textmate

%changelog
* Wed Oct 14 2026 Miguel Negron <manegron@redborder.com> - 4.0.0-1
- Remove ruby 2.7.5: ruby 3.4.11 is the only ruby, with the gemsets global (platform scripts) and web (webui)

* Wed Oct 07 2026 Miguel Negron <manegron@redborder.com> - 3.0.0-1
- Add ruby 3.4.11 with the web gemset for the webui on Rails 8. Ruby 2.7.5 stays as default

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
