%define debug_package %{nil}
%global rvm_dir /usr/lib/rvm
%global rvm_group rvm
%global rvm_version %{__rvmversion}
%global ruby_version %{__rubyversion}
%global bundler_version %{__bundlerversion}
%global rubygems_version %{__rubygemsversion}

Name: redborder-rubyrvm
Version: %{__version}
Release: %{__release}%{?dist}
License: ASL 2.0
BuildArch: x86_64
Source0: rvm-%{rvm_version}.tar.gz
Source1: bundler-1.12.5.gem
Source2: bundle-0.0.1.gem
Source3: chef-12.0.3.gem
Source4: Gemfile_global
Source5: Gemfile_web
Source6: chef-zero-3.2.1.gem
Source7: prettyprint-0.0.1.gem
Source8: ruby-2.2.4.tar.bz2
Source9: mimemagic-0.3.0.gem
Source10: redborder-consul-connector-0.0.3.gem

BuildRequires: libyaml-devel libffi-devel autoconf automake libtool bison postgresql-devel ImageMagick-devel = 6.7.8.9 git
BuildRequires: gcc-c++ patch readline readline-devel zlib-devel openssl-devel procps-ng sqlite-devel ruby
Requires: sed grep tar gzip bzip2 make file dialog
Obsoletes: rvm
Summary: Rvm and ruby for redborder platform

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

%{rvm_dir}/bin/rvm --verify-downloads 2 --disable-binary install %{ruby_version}

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
%{rvm_dir}/bin/rvm %{ruby_version}@global do gem install %{rvm_dir}/archives/chef-zero*.gem --no-ri
%{rvm_dir}/bin/rvm %{ruby_version}@global do gem install %{rvm_dir}/archives/chef-*.gem --no-ri
%{rvm_dir}/bin/rvm %{ruby_version}@global do gem install %{rvm_dir}/archives/prettyprint-*.gem --no-ri
%{rvm_dir}/bin/rvm %{ruby_version}@global do gem install %{rvm_dir}/archives/redborder-consul-connector-*.gem --no-ri
%{rvm_dir}/bin/rvm %{ruby_version}@web do gem install %{rvm_dir}/archives/mimemagic-*.gem --no-ri

%{rvm_dir}/bin/rvm %{ruby_version}@global do bundle install --gemfile=$RPM_SOURCE_DIR/Gemfile_global
%{rvm_dir}/bin/rvm %{ruby_version}@web do bundle install --gemfile=$RPM_SOURCE_DIR/Gemfile_web

# Remove downloaded gems and files after compilation
rm -rf %{rvm_dir}/src/*
rm -rf %{rvm_dir}/log/*
rm -rf %{rvm_dir}/archives/*

%install
rm -rf $RPM_BUILD_ROOT/*
mkdir -p $RPM_BUILD_ROOT/%{rvm_dir}
mkdir -p $RPM_BUILD_ROOT/etc
mkdir -p $RPM_BUILD_ROOT/etc/profile.d
mkdir -p $RPM_BUILD_ROOT/var/www/rb-rails

cp -rf %{rvm_dir}/* $RPM_BUILD_ROOT/%{rvm_dir}/
cp /etc/profile.d/rvm.sh $RPM_BUILD_ROOT/etc/profile.d/rvm.sh
cp /etc/rvmrc $RPM_BUILD_ROOT/etc/rvmrc
#cp $RPM_SOURCE_DIR/Gemfile_web.lock $RPM_BUILD_ROOT/var/www/rb-rails/Gemfile.lock

chgrp -R rvm $RPM_BUILD_ROOT/%{rvm_dir}
chmod -R g+wxr $RPM_BUILD_ROOT/%{rvm_dir}

# clean unicorn and /usr/local references
ruby -p -i -e 'gsub(%r{#!.*/this/will/be/overwritten/or/wrapped/anyways/do/not/worry/ruby}, "#!/usr/bin/ruby")' \
  $RPM_BUILD_ROOT/%{rvm_dir}/gems/ruby-%{ruby_version}@web/gems/unicorn*/bin/unicorn* &>/dev/null || :
for f in $(grep -l -r "#\!\s*/usr/local/bin/ruby" $RPM_BUILD_ROOT/%{rvm_dir}); do
        ruby -p -i -e 'gsub(%r{#!.*/usr/local/bin/ruby}, "#!/usr/bin/ruby")' $f &>/dev/null || :
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
#/var/www/rb-rails/Gemfile.lock

%changelog
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
