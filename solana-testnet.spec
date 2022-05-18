%global solana_suffix testnet

%global solana_user   solana-%{solana_suffix}
%global solana_group  solana-%{solana_suffix}
%global solana_home   %{_sharedstatedir}/solana/%{solana_suffix}/
%global solana_log    %{_localstatedir}/log/solana/%{solana_suffix}/
%global solana_etc    %{_sysconfdir}/solana/%{solana_suffix}/

# Available CPUs and features: `llc -march=x86-64 -mattr=help`.
# x86-64-v3 (close to Haswell):
#   AVX, AVX2, BMI1, BMI2, F16C, FMA, LZCNT, MOVBE, XSAVE
%global validator_target_cpu x86-64-v3
# x86-64:
#   CMOV, CMPXCHG8B, FPU, FXSR, MMX, FXSR, SCE, SSE, SSE2
%global base_target_cpu x86-64

Name:       solana-%{solana_suffix}
Epoch:      0
# git 12a12b919a9a3a365b696ed624cf6fae3f312ea4
Version:    1.10.16
Release:    1%{?dist}
Summary:    Solana blockchain software (%{solana_suffix} version)

License:    Apache-2.0
URL:        https://github.com/solana-labs/solana/
Source0:    https://github.com/solana-labs/solana/archive/v%{version}/solana-%{version}.tar.gz

# Contains solana-$VERSION/vendor/*.
#     $ cargo vendor
#     $ mkdir solana-X.Y.Z
#     $ mv vendor solana-X.Y.Z/
#     $ tar vcJf solana-X.Y.Z.cargo-vendor.tar.xz solana-X.Y.Z
Source1:    solana-%{version}.cargo-vendor.tar.xz
Source2:    config.toml

Source3:    activate
Source4:    solana-validator.service
Source5:    solana-validator
Source6:    solana-sys-tuner.service
Source7:    solana-watchtower.service
Source8:    solana-watchtower
Source9:    solana-validator.logrotate
Source10:   jemalloc-wrapper
Source11:   0001-Use-different-socket-path-for-sys-tuner-built-for-te.patch

Source100:  filter-cargo-checksum

Patch1001: 0001-Enable-debug-info-in-release-profile.patch
Patch1002: 0002-Enable-LTO.patch

Patch2001: 0003-Replace-bundled-C-C-libraries-with-system-provided.patch

Patch3001: rocksdb-dynamic-linking.patch

Patch4001: 0001-Add-watchtower-option-to-add-custom-string-into-noti.patch

ExclusiveArch:  %{rust_arches}

%global python python3
BuildRequires:  %{python}

BuildRequires:  findutils
BuildRequires:  rust-packaging
BuildRequires:  rustfmt
BuildRequires:  rust = 1.59.0
BuildRequires:  systemd-rpm-macros
BuildRequires:  gcc
BuildRequires:  clang
BuildRequires:  make
BuildRequires:  pkgconf-pkg-config
BuildRequires:  protobuf-compiler
BuildRequires:  openssl-devel
BuildRequires:  zlib-ng-devel
BuildRequires:  bzip2-devel
BuildRequires:  lz4-devel
BuildRequires:  hidapi-devel
BuildRequires:  jemalloc-devel
BuildRequires:  rocksdb-devel >= 6.28.0
BuildRequires:  libzstd-devel

# libudev-devel
BuildRequires:  systemd-devel


%description
Web-Scale Blockchain for fast, secure, scalable, decentralized apps and marketplaces.
Version for %{solana_suffix}.


%package common
Summary: Solana common files (%{solana_suffix} version)


%description common
Solana common files (%{solana_suffix} version).


%package cli
Summary: Solana RPC CLI (%{solana_suffix} version)
Requires: %{name}-common = %{epoch}:%{version}-%{release}


%description cli
Solana RPC CLI (%{solana_suffix} version).


%package utils
Summary: Solana local utilities (%{solana_suffix} version)
Requires: %{name}-common = %{epoch}:%{version}-%{release}


%description utils
Solana local utilities (%{solana_suffix} version).


%package deps
Summary: Solana dependency libraries (%{solana_suffix} version)


%description deps
Solana dependency libraries (%{solana_suffix} version).


%package daemons
Summary: Solana daemons (%{solana_suffix} version)
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: %{name}-cli = %{epoch}:%{version}-%{release}
Requires: %{name}-utils = %{epoch}:%{version}-%{release}
Requires: %{name}-deps = %{epoch}:%{version}-%{release}
Requires: solana-perf-libs-%{solana_suffix}
Requires: logrotate
Requires: zstd
Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd


%description daemons
Solana daemons (%{solana_suffix} version).


%package bpf-utils
Summary: Solana BPF utilities (%{solana_suffix} version)
Requires: %{name}-common = %{epoch}:%{version}-%{release}


%description bpf-utils
Solana BPF utilities (%{solana_suffix} version).


%package tests
Summary: Solana tests and benchmarks (%{solana_suffix} version)
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: %{name}-deps = %{epoch}:%{version}-%{release}
Requires: solana-perf-libs-%{solana_suffix}


%description tests
Solana tests and benchmarks (%{solana_suffix} version).


%prep
%autosetup -N -b0 -n solana-%{version}
%autosetup -N -b1 -n solana-%{version}

sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE11} \
        | patch -p1

%patch1001 -p1
cp Cargo.toml Cargo.toml.no-lto
%patch1002 -p1

%patch2001 -p1

%patch3001 -p1

%patch4001 -p1

# Remove bundled C/C++ source code.
rm -r vendor/bzip2-sys/bzip2-*
%{python} %{SOURCE100} vendor/bzip2-sys '^bzip2-.*'
rm -r vendor/hidapi/etc/hidapi
%{python} %{SOURCE100} vendor/hidapi '^etc/hidapi/.*'
rm -r vendor/tikv-jemalloc-sys/jemalloc
%{python} %{SOURCE100} vendor/tikv-jemalloc-sys '^jemalloc/.*'
rm -r vendor/librocksdb-sys/lz4
rm -r vendor/librocksdb-sys/rocksdb
rm -r vendor/librocksdb-sys/snappy
mkdir vendor/librocksdb-sys/rocksdb
touch vendor/librocksdb-sys/rocksdb/AUTHORS
%{python} %{SOURCE100} vendor/librocksdb-sys \
        '^lz4/.*' \
        '^rocksdb/.*' \
        '^snappy/.*'
rm -r vendor/zstd-sys/zstd
%{python} %{SOURCE100} vendor/zstd-sys '^zstd/.*'
rm -r vendor/libz-sys/src/zlib
rm -r vendor/libz-sys/src/zlib-ng
%{python} %{SOURCE100} vendor/libz-sys \
        '^src/zlib/.*' \
        '^src/zlib-ng/.*'
rm -r vendor/prost-build/third-party
%{python} %{SOURCE100} vendor/prost-build \
        '^third-party/.*'

mkdir .cargo
cp %{SOURCE2} .cargo/

# Fix Fedora's shebang mangling errors:
#     *** ERROR: ./usr/src/debug/solana-testnet-1.10.0-1.fc35.x86_64/vendor/ascii/src/ascii_char.rs has shebang which doesn't start with '/' ([cfg_attr(rustfmt, rustfmt_skip)])
find . -type f -name "*.rs" -exec chmod 0644 "{}" ";"


%build
export JEMALLOC_OVERRIDE=%{_libdir}/libjemalloc.so
export ROCKSDB_INCLUDE_DIR=%{_includedir}
export ROCKSDB_LIB_DIR=%{_libdir}
export LZ4_INCLUDE_DIR=%{_includedir}
export LZ4_LIB_DIR=%{_libdir}

# First, build binaries optimized for newer CPUs.
export RUSTFLAGS='-C target-cpu=%{validator_target_cpu}'
%{__cargo} build %{?_smp_mflags} -Z avoid-dev-deps --frozen --release \
        --package solana-validator \
        --package solana-accounts-bench \
        --package solana-banking-bench \
        --package solana-bench-streamer \
        --package solana-merkle-root-bench \
        --package solana-poh-bench \
        --package solana-program:%{version}

mv target/release ./release.newer-cpus
%{__cargo} clean

# Second, build binaries optimized for generic baseline CPU.
cp Cargo.toml.no-lto Cargo.toml
export RUSTFLAGS='-C target-cpu=%{base_target_cpu}'
%{__cargo} build %{?_smp_mflags} -Z avoid-dev-deps --frozen --release

sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE3} \
        >activate
sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE4} \
        >solana-validator.service
sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE5} \
        >solana-validator
sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE6} \
        >solana-sys-tuner.service
sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE7} \
        >solana-watchtower.service
sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE8} \
        >solana-watchtower
sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE9} \
        >solana-validator.logrotate
sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE10} \
        >jemalloc-wrapper
chmod a+x jemalloc-wrapper

./target/release/solana completion --shell bash >solana.bash-completion


%install
mkdir -p %{buildroot}/opt/solana/%{solana_suffix}/bin/deps
mkdir -p %{buildroot}/opt/solana/%{solana_suffix}/bin/perf-libs
mkdir -p %{buildroot}/opt/solana/%{solana_suffix}/libexec
mkdir -p %{buildroot}/%{_unitdir}
mkdir -p %{buildroot}%{solana_home}
mkdir -p %{buildroot}%{solana_log}
mkdir -p %{buildroot}%{solana_etc}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d

ln -s ../bin/deps \
        %{buildroot}/opt/solana/%{solana_suffix}/libexec/deps
ln -s ../bin/perf-libs \
        %{buildroot}/opt/solana/%{solana_suffix}/libexec/perf-libs

mv activate \
        %{buildroot}/opt/solana/%{solana_suffix}/
mv solana-validator.service \
        %{buildroot}/%{_unitdir}/solana-validator-%{solana_suffix}.service
mv solana-validator \
        %{buildroot}%{_sysconfdir}/sysconfig/solana-validator-%{solana_suffix}
mv solana-sys-tuner.service \
        %{buildroot}/%{_unitdir}/solana-sys-tuner-%{solana_suffix}.service
mv solana-watchtower.service \
        %{buildroot}/%{_unitdir}/solana-watchtower-%{solana_suffix}.service
mv solana-watchtower \
        %{buildroot}%{_sysconfdir}/sysconfig/solana-watchtower-%{solana_suffix}
mv solana-validator.logrotate \
        %{buildroot}%{_sysconfdir}/logrotate.d/solana-validator-%{solana_suffix}

cp jemalloc-wrapper \
        %{buildroot}/opt/solana/%{solana_suffix}/bin/solana-ledger-tool
cp jemalloc-wrapper \
        %{buildroot}/opt/solana/%{solana_suffix}/bin/solana-validator

# Use binaries optimized for newer CPUs for running validator and local benchmarks.
mv release.newer-cpus/*.so target/release/
mv release.newer-cpus/solana-validator target/release/
mv release.newer-cpus/solana-accounts-bench target/release/
mv release.newer-cpus/solana-banking-bench target/release/
mv release.newer-cpus/solana-bench-streamer target/release/
mv release.newer-cpus/solana-merkle-root-bench target/release/
mv release.newer-cpus/solana-poh-bench target/release/
mv release.newer-cpus/solana-test-validator target/release/

find target/release -mindepth 1 -maxdepth 1 -type d -exec rm -r "{}" \;
rm target/release/*.d
rm target/release/*.rlib
# Excluded because we do not need installers.
rm target/release/solana-install target/release/solana-install-init target/release/solana-ledger-udev
# Excluded. 
# TODO: Why? Official binary release does not contain these, only libsolana_*_program.so installed.
rm \
        target/release/libsolana_frozen_abi_macro.so \
        target/release/libsolana_sdk_macro.so \
        target/release/libsolana_sdk.so \
        target/release/libsolana_zk_token_sdk.so
rm target/release/gen-syscall-list

mv target/release/*.so \
        %{buildroot}/opt/solana/%{solana_suffix}/bin/deps/
mv target/release/solana-validator \
        %{buildroot}/opt/solana/%{solana_suffix}/libexec/
mv target/release/solana-ledger-tool \
        %{buildroot}/opt/solana/%{solana_suffix}/libexec/
mv target/release/* \
        %{buildroot}/opt/solana/%{solana_suffix}/bin/

mv solana.bash-completion %{buildroot}/opt/solana/%{solana_suffix}/bin/solana.bash-completion


%files common
%dir /opt/solana
%dir /opt/solana/%{solana_suffix}
%dir /opt/solana/%{solana_suffix}/bin
%dir /opt/solana/%{solana_suffix}/bin/deps
%dir /opt/solana/%{solana_suffix}/bin/perf-libs
%dir /opt/solana/%{solana_suffix}/libexec
/opt/solana/%{solana_suffix}/activate
/opt/solana/%{solana_suffix}/libexec/deps
/opt/solana/%{solana_suffix}/libexec/perf-libs


%files cli
%dir /opt/solana
%dir /opt/solana/%{solana_suffix}
%dir /opt/solana/%{solana_suffix}/bin
/opt/solana/%{solana_suffix}/bin/solana
/opt/solana/%{solana_suffix}/bin/solana-gossip
/opt/solana/%{solana_suffix}/bin/solana-ip-address
/opt/solana/%{solana_suffix}/bin/solana-stake-accounts
/opt/solana/%{solana_suffix}/bin/solana-tokens
/opt/solana/%{solana_suffix}/bin/solana.bash-completion


%files utils
%dir /opt/solana
%dir /opt/solana/%{solana_suffix}
%dir /opt/solana/%{solana_suffix}/bin
%dir /opt/solana/%{solana_suffix}/libexec
/opt/solana/%{solana_suffix}/bin/solana-keygen
/opt/solana/%{solana_suffix}/bin/solana-log-analyzer
/opt/solana/%{solana_suffix}/bin/solana-ledger-tool
/opt/solana/%{solana_suffix}/bin/solana-genesis
/opt/solana/%{solana_suffix}/bin/solana-store-tool
/opt/solana/%{solana_suffix}/bin/solana-upload-perf
/opt/solana/%{solana_suffix}/bin/solana-net-shaper
/opt/solana/%{solana_suffix}/libexec/solana-ledger-tool


%files deps
%dir /opt/solana
%dir /opt/solana/%{solana_suffix}
%dir /opt/solana/%{solana_suffix}/bin
%dir /opt/solana/%{solana_suffix}/bin/deps
/opt/solana/%{solana_suffix}/bin/deps/libsolana_program.so


%files daemons
%dir /opt/solana
%dir /opt/solana/%{solana_suffix}
%dir /opt/solana/%{solana_suffix}/bin
%dir /opt/solana/%{solana_suffix}/libexec
/opt/solana/%{solana_suffix}/bin/solana-faucet
/opt/solana/%{solana_suffix}/bin/solana-ip-address-server
/opt/solana/%{solana_suffix}/bin/solana-replica-node
/opt/solana/%{solana_suffix}/bin/solana-sys-tuner
/opt/solana/%{solana_suffix}/bin/solana-validator
/opt/solana/%{solana_suffix}/bin/solana-watchtower
/opt/solana/%{solana_suffix}/libexec/solana-validator

%{_unitdir}/solana-validator-%{solana_suffix}.service
%{_unitdir}/solana-sys-tuner-%{solana_suffix}.service
%{_unitdir}/solana-watchtower-%{solana_suffix}.service
%attr(0640,root,%{solana_group}) %config(noreplace) %{_sysconfdir}/sysconfig/solana-validator-%{solana_suffix}
%attr(0640,root,%{solana_group}) %config(noreplace) %{_sysconfdir}/sysconfig/solana-watchtower-%{solana_suffix}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/solana-validator-%{solana_suffix}

%attr(0755,root,root) %dir %{_sysconfdir}/solana
%attr(0750,root,%{solana_group}) %dir %{solana_etc}

%attr(0755,root,root) %dir %{_sharedstatedir}/solana
%attr(0750,%{solana_user},%{solana_group}) %dir %{solana_home}

%attr(0755,root,root) %dir %{_localstatedir}/log/solana
%attr(0750,%{solana_user},%{solana_group}) %dir %{solana_log}


%files bpf-utils
%dir /opt/solana
%dir /opt/solana/%{solana_suffix}
%dir /opt/solana/%{solana_suffix}/bin
/opt/solana/%{solana_suffix}/bin/cargo-build-bpf
/opt/solana/%{solana_suffix}/bin/cargo-test-bpf
/opt/solana/%{solana_suffix}/bin/rbpf-cli


%files tests
%dir /opt/solana
%dir /opt/solana/%{solana_suffix}
%dir /opt/solana/%{solana_suffix}/bin
/opt/solana/%{solana_suffix}/bin/solana-accounts-bench
/opt/solana/%{solana_suffix}/bin/solana-accounts-cluster-bench
/opt/solana/%{solana_suffix}/bin/solana-banking-bench
/opt/solana/%{solana_suffix}/bin/solana-bench-streamer
/opt/solana/%{solana_suffix}/bin/solana-bench-tps
/opt/solana/%{solana_suffix}/bin/solana-dos
/opt/solana/%{solana_suffix}/bin/solana-merkle-root-bench
/opt/solana/%{solana_suffix}/bin/solana-poh-bench
/opt/solana/%{solana_suffix}/bin/solana-test-validator
/opt/solana/%{solana_suffix}/bin/solana-transaction-dos


%pre daemons
# TODO: Separate user for each daemon.
getent group %{solana_group} >/dev/null || groupadd -r %{solana_group}
getent passwd %{solana_user} >/dev/null || \
        useradd -r -s /sbin/nologin -d %{solana_home} -M \
        -c 'Solana (%{solana_suffix})' -g %{solana_group} %{solana_user}
exit 0


%post daemons
%systemd_post solana-validator-%{solana_suffix}.service
%systemd_post solana-sys-tuner-%{solana_suffix}.service
%systemd_post solana-watchtower-%{solana_suffix}.service


%preun daemons
%systemd_preun solana-validator-%{solana_suffix}.service
%systemd_preun solana-sys-tuner-%{solana_suffix}.service
%systemd_preun solana-watchtower-%{solana_suffix}.service


%postun daemons
%systemd_postun solana-validator-%{solana_suffix}.service
%systemd_postun_with_restart solana-sys-tuner-%{solana_suffix}.service
%systemd_postun_with_restart solana-watchtower-%{solana_suffix}.service


%changelog
* Wed May 18 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.16-1
- Update to 1.10.16

* Tue May 17 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.15-1
- Update to 1.10.15

* Tue May 17 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.14-1
- Update to 1.10.14

* Tue May 10 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.13-1
- Update to 1.10.13

* Thu May 05 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.12-1
- Update to 1.10.12

* Thu Apr 28 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.11-1
- Update to 1.10.11

* Tue Apr 26 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.10-1
- Update to 1.10.10

* Tue Apr 19 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.9-1
- Update to 1.10.9

* Thu Apr 14 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.8-1
- Update to 1.10.8

* Sun Apr 10 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.7-1
- Update to 1.10.7

* Tue Mar 29 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.5-1
- Update to 1.10.5

* Sat Mar 19 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.3-1
- Update to 1.10.3

* Tue Mar 15 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.2-1
- Update to 1.10.2

* Fri Mar 11 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.1-1
- Update to 1.10.1

* Thu Mar 03 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.0-1
- Update to 1.10.0

* Thu Feb 24 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.9-1
- Update to 1.9.9

* Sun Feb 20 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.8-1
- Update to 1.9.8

* Thu Feb 17 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.7-1
- Update to 1.9.7

* Sat Feb 12 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.6-1
- Update to 1.9.6

* Mon Jan 24 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.5-3
- Create symlink to deps dir

* Sun Jan 23 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.5-2
- Create symlink to perf-libs dir, so validator will be able to locate optimized libs

* Sat Jan 22 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.5-1
- Update to 1.9.5

* Wed Jan 19 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.4-2
- Make sure that sys-tuner start before validator

* Sun Jan 8 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.4-1
- Update to 1.9.4

* Thu Jan 6 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.3-1
- Update to 1.9.3

* Tue Jan 4 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.2-2
- Add jemalloc wrapper for solana-ledger-tool

* Wed Dec 22 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.2-1
- Update to 1.9.2

* Thu Dec 16 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.1-1
- Update to 1.9.1

* Sun Dec 12 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.0-1
- Update to 1.9.0

* Sat Dec 11 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.9-1
- Update to 1.8.9

* Thu Dec 9 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.8-1
- Update to 1.8.8

* Sun Dec 5 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.7-2
- Add wrapper to run validator with jemalloc, prevents crash

* Sat Dec 4 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.7-1
- Update to 1.8.7

* Wed Dec 1 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.6-1
- Update to 1.8.6

* Thu Nov 18 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.5-1
- Update to 1.8.5

* Wed Nov 17 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.4-1
- Update to 1.8.4

* Wed Nov 10 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.3-1
- Update to 1.8.3

* Wed Nov 10 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.2-4
- Update patches

* Wed Nov 3 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.2-4
- Update patches

* Tue Nov 2 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.2-3
- Update patches

* Sun Oct 31 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.2-2
- Update patches

* Thu Oct 28 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.2-1
- Update to 1.8.2

* Wed Oct 27 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.1-2
- Update patches
- Optimize solana-accountsdb-plugin-postgres for newer CPUs

* Tue Oct 26 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.1-1
- Update to 1.8.1

* Thu Oct 7 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.8.0-1
- Update to 1.8.0

* Thu Sep 30 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.14-1
- Update to 1.7.14

* Wed Sep 29 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.13-1
- Update to 1.7.13

* Thu Sep 23 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.12-3
- Rebuild on f35 with newer rocksdb
- Improve "activate" script

* Tue Sep 21 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.12-2
- Keep log files for 14 days instead of 7

* Thu Sep 16 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.12-1
- Update to 1.7.12

* Sat Aug 28 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.11-1
- Update to 1.7.11

* Thu Aug 12 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.10-2
- Fix bash-completion in activation script

* Thu Aug 12 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.10-1
- Update to 1.7.10

* Sun Aug 1 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.9-1
- Update to 1.7.9

* Sat Jul 24 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.8-2
- Backport patches for https://github.com/solana-labs/solana/issues/18177

* Sat Jul 24 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.8-1
- Update to 1.7.8

* Sat Jul 17 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.6-1
- Update to 1.7.6

* Fri Jul 2 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.4-1
- Update to 1.7.4

* Fri Jun 25 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.3-2
- Optimize performance-critical binaries for newer CPUs.

* Wed Jun 23 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.3-1
- Update to 1.7.3

* Thu Jun 17 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.2-1
- Update to 1.7.2

* Tue Jun 8 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.1-1
- Update to 1.7.1

* Wed Jun 2 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.0-1
- Update to 1.7.0

* Wed May 26 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.10-1
- Update to 1.6.10

* Sat May 15 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.9-1
- Update to 1.6.9

* Sun May 09 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.8-1
- Update to 1.6.8

* Wed May 05 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.7-1
- Update to 1.6.7

* Mon Apr 19 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.6-1
- Update to 1.6.6

* Wed Apr 14 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.5-1
- Update to 1.6.5

* Mon Apr 05 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.4-1
- Update to 1.6.4

* Fri Apr 02 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.3-1
- Update to 1.6.3

* Wed Mar 31 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.2-1
- Update to 1.6.2

* Thu Mar 18 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.1-1
- Update to 1.6.1

* Mon Mar 15 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.0-1
- Update to 1.6.0

* Sun Mar 14 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.14-2
- Support logging into files

* Tue Mar 09 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.14-1
- Update to 1.5.14

* Thu Mar 04 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.13-1
- Update to 1.5.13

* Wed Mar 03 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.12-1
- Update to 1.5.12

* Sat Feb 27 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.11-1
- Update to 1.5.11

* Thu Feb 25 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.10-1
- Update to 1.5.10
- Do not restart solana-validator on upgrade

* Wed Feb 24 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.8-3
- Unbundle zstd
- Enable optimizations for newer CPUs

* Thu Feb 18 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.8-2
- Replace bundled C/C++ libraries with system provided
- Enable LTO and debug info in release profile
- Add directories

* Wed Feb 17 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.8-1
- Update to 1.5.8

* Sat Feb 13 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.7-1
- Initial packaging
