%global solana_suffix mainnet

%global solana_user   solana-%{solana_suffix}
%global solana_group  solana-%{solana_suffix}
%global solana_home   %{_sharedstatedir}/solana/%{solana_suffix}/
%global solana_log    %{_localstatedir}/log/solana/%{solana_suffix}/
%global solana_etc    %{_sysconfdir}/solana/%{solana_suffix}/

%global rust_version 1.57.0

# Available CPUs and features: `llc -march=x86-64 -mattr=help`.
# x86-64-v3 (close to Haswell):
#   AVX, AVX2, BMI1, BMI2, F16C, FMA, LZCNT, MOVBE, XSAVE
%global validator_target_cpu x86-64-v3
# x86-64:
#   CMOV, CMPXCHG8B, FPU, FXSR, MMX, FXSR, SCE, SSE, SSE2
%global base_target_cpu x86-64

Name:       solana-%{solana_suffix}
Epoch:      1
# git f261a4d8545c59ed2768d9fb14f14bd4a7353e65
Version:    1.9.27
Release:    100%{?dist}
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

Patch3001: 0001-Update-rocksdb-to-0.18.0-release-23031.patch
Patch3002: rocksdb-dynamic-linking.patch

Patch4001: 0001-Add-watchtower-option-to-add-custom-string-into-noti.patch

ExclusiveArch:  %{rust_arches}

%global python python3
BuildRequires:  %{python}

BuildRequires:  rust-packaging
BuildRequires:  rustfmt = %{rust_version}
BuildRequires:  rust = %{rust_version}
BuildRequires:  rust-std-static = %{rust_version}
BuildRequires:  cargo = %{rust_version}
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
%patch3002 -p1

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
        --package solana-sdk \
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
rm target/release/libsolana_frozen_abi_macro.so target/release/libsolana_sdk_macro.so
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
/opt/solana/%{solana_suffix}/bin/deps/libsolana_sdk.so


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
* Wed Jun 01 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.27-100
- Update to 1.9.27

* Wed Jun 01 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.26-100
- Update to 1.9.26

* Sat May 28 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.25-100
- Update to 1.9.25

* Tue May 24 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.24-100
- Update to 1.9.24

* Tue May 24 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.23-100
- Update to 1.9.23

* Tue May 17 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.22-100
- Update to 1.9.22

* Tue May 10 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.21-100
- Update to 1.9.21

* Thu May 05 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.20-100
- Update to 1.9.20

* Wed May 04 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.19-100
- Update to 1.9.19

* Fri Apr 22 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.18-100
- Update to 1.9.18

* Tue Apr 19 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.17-100
- Update to 1.9.17

* Fri Apr 15 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.16-100
- Update to 1.9.16

* Sun Apr 10 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.15-100
- Update to 1.9.15

* Tue Mar 29 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.14-100
- Update to 1.9.14

* Fri Mar 11 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.12-100
- Update to 1.9.12

* Thu Mar 10 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.11-100
- Update to 1.9.11

* Wed Mar 09 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.10-100
- Update to 1.9.10

* Mon Mar 07 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.9-101
- Rebuild with newer rocksdb

* Sat Feb 26 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.9.9-100
- Update to 1.9.9

* Fri Feb 18 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.16-100
- Update to 1.8.16

* Mon Jan 24 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.14-102
- Create symlink to deps dir

* Sun Jan 23 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.14-101
- Create symlink to perf-libs dir, so validator will be able to locate optimized libs

* Sat Jan 22 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.14-100
- Update to 1.8.14

* Fri Jan 21 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.13-100
- Update to 1.8.13

* Sat Jan 8 2022 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.12-100
- Update to 1.8.12

* Tue Dec 14 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.11-100
- Update to 1.8.11

* Tue Dec 14 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.10-101
- Use rust 1.55.0 for this release (which is 1.8.5 really)

* Tue Dec 14 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.10-100
- Update to 1.8.10

* Sat Dec 11 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.9-100
- Update to 1.8.9

* Thu Dec 9 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.8-100
- Update to 1.8.8

* Sun Dec 5 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.7-101
- Add wrapper to run validator with jemalloc, prevents crash

* Sat Dec 4 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.7-100
- Update to 1.8.7

* Wed Dec 1 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.6-100
- Update to 1.8.6

* Thu Nov 18 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.5-100
- Update to 1.8.5

* Wed Nov 17 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.4-100
- Update to 1.8.4

* Wed Nov 10 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.3-100
- Update to 1.8.3

* Wed Nov 10 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.2-101
- Update patches

* Thu Nov 4 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.2-101
- Update patches

* Thu Oct 28 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.2-100
- Update to 1.8.2

* Wed Oct 27 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.8.1-100
- Update to 1.8.1

* Fri Oct 8 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.7.15-100
- Update to 1.7.15

* Thu Sep 30 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.7.14-100
- Update to 1.7.14

* Tue Sep 28 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.6.27-100
- Update to 1.6.27

* Sat Sep 18 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.6.26-100
- Update to 1.6.26

* Wed Sep 15 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.6.25-100
- Update to 1.6.25

* Tue Sep 14 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.6.24-100
- Update to 1.6.24

* Tue Sep 14 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.6.23-100
- Update to 1.6.23
- Keep log files for 14 days instead of 7

* Fri Aug 27 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.6.22-100
- Update to 1.6.22

* Fri Aug 20 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1:1.6.21-100
- Downgrade to 1.6.21 as recommended by developers

* Sat Aug 14 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.7.10-100
- Update to 1.7.10

* Sat Jul 24 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.20-100
- Update to 1.6.20

* Mon Jul 19 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.19-100
- Update to 1.6.19

* Sat Jul 17 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.18-100
- Update to 1.6.18

* Sat Jul 3 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.16-100
- Update to 1.6.16

* Fri Jul 2 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.15-100
- Update to 1.6.15

* Fri Jun 25 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.14-101
- Optimize performance-critical binaries for newer CPUs.

* Tue Jun 22 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.14-100
- Update to 1.6.14

* Thu Jun 17 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.13-100
- Update to 1.6.13

* Tue Jun 15 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.12-100
- Update to 1.6.12

* Fri Jun 4 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.11-100
- Update to 1.6.11

* Sat May 29 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.10-100
- Change package version to prevent /usr/lib/.build-id collision with
  build of the same Solana version for the Testnet.

* Fri May 28 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.10-1
- Update to 1.6.10

* Wed May 26 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.9-1
- Update to 1.6.9

* Sun May 09 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.6.7-1
- Update to 1.6.7

* Wed Apr 21 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.19-1
- Update to 1.5.19

* Fri Apr 02 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.18-1
- Update to 1.5.18

* Wed Mar 31 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.17-1
- Update to 1.5.17

* Sat Mar 20 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.16-1
- Initial packaging for Mainnet
