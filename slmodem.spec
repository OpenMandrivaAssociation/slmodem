# I love OpenSource :-(

%define name slmodem
%define version 2.9.11
%define snapshot 20070813
%define mdkrelease 0.%{snapshot}.3
%define release %mkrel %{mdkrelease}
%define url http://www.smlink.com/main/down
#	    http://linmodems.technion.ac.il/packages/smartlink/
%define moduleversion %{version}-%{release}

Summary:	slmodem utility
Name:		%{name}
Version:	%{version}
Release:	%{release}
Source0:	%{name}-%{version}-%{snapshot}.tar.gz
Source1:	slmodem.nodes
Source2:	slmodem.perms
Patch0:		%{name}-2.9.9-dkms.patch
Patch1:		slmodem-2.9.11-20070813-mdkize.patch
Patch2:		slmodem-2.9.11-alsa-period-size.patch
Patch3:		slmodem-2.9.11-SA_SHIRQ.patch
License:	SmartLink
Group:		System/Kernel and hardware
BuildRoot:	%{_tmppath}/%{name}-buildroot
Url:		%{url}
Prefix:		%{_prefix}
Requires:	drakxtools >= 9.2-8mdk
Requires(post):	udev >= 114-7mdv2008.0
BuildRequires:	libalsa-devel
ExclusiveArch:	%{ix86}

%description
slmodem driver utility.

%package -n dkms-%{name}
Summary:	slmodem module
Group:		System/Kernel and hardware
Requires:	drakxtools >= 9.2-8mdk
Requires(post):	dkms
Requires(preun):	dkms

%description -n dkms-%{name}
slmodem module Linux driver.

%prep
%setup -q -n %{name}-%{version}-%{snapshot}
%patch0 -p1 -b .dkms
%patch1 -p1 -b .mdkize
%patch2 -p1 -b .periodsize
%patch3 -p0 -b .SA_SHIRQ

%build
%make -C modem SUPPORT_ALSA=1

%install
rm -rf $RPM_BUILD_ROOT

# utils 
mkdir -p $RPM_BUILD_ROOT/%{_sbindir}
install -m755 modem/slmodemd modem/modem_test $RPM_BUILD_ROOT/%{_sbindir}
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig $RPM_BUILD_ROOT/%{_sysconfdir}/rc.d/init.d
install -m644 scripts/suse/slmodemd.conf $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/slmodemd
install -m755 scripts/mandrake/slmodemd $RPM_BUILD_ROOT/%{_sysconfdir}/rc.d/init.d/
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/udev/devices.d/
install -m644 %{SOURCE1} $RPM_BUILD_ROOT/%{_sysconfdir}/udev/devices.d/
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/security/console.perms.d/
install -m644 %{SOURCE2} $RPM_BUILD_ROOT/%{_sysconfdir}/security/console.perms.d/

# driver source
mkdir -p $RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{moduleversion}
cp -r * $RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{moduleversion}
rm -rf $RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{moduleversion}/{patches,scripts}
cat > $RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{moduleversion}/dkms.conf <<EOF
PACKAGE_NAME=%{name}
PACKAGE_VERSION=%{moduleversion}

DEST_MODULE_LOCATION[0]=/kernel/drivers/char
DEST_MODULE_LOCATION[1]=/kernel/drivers/char
BUILT_MODULE_NAME[0]=slamr
BUILT_MODULE_LOCATION[0]=drivers
BUILT_MODULE_NAME[1]=slusb
BUILT_MODULE_LOCATION[1]=drivers
MAKE[0]="make KERNEL_DIR=\${kernel_source_dir} drivers"
CLEAN="make clean"

AUTOINSTALL=yes
EOF

%post
%_post_service slmodemd
/sbin/create_static_dev_nodes /dev %{_sysconfdir}/udev/devices.d/slmodem.nodes
echo "Relaunch drakconnect to configure your slmodem cards"

%preun
%_preun_service slmodemd

%post -n dkms-%{name}
set -x
/usr/sbin/dkms --rpm_safe_upgrade add -m %name -v %moduleversion
/usr/sbin/dkms --rpm_safe_upgrade build -m %name -v %moduleversion
/usr/sbin/dkms --rpm_safe_upgrade install -m %name -v %moduleversion

%preun -n dkms-%{name}
set -x
/usr/sbin/dkms --rpm_safe_upgrade remove -m %name -v %version --all

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc COPYING Changes README
%{_sbindir}/*
%config(noreplace) %{_sysconfdir}/sysconfig/slmodemd
%{_sysconfdir}/rc.d/init.d/slmodemd
%{_sysconfdir}/udev/devices.d/slmodem.nodes
%{_sysconfdir}/security/console.perms.d/slmodem.perms

%files -n dkms-%{name}
%defattr(-,root,root)
%doc %{_docdir}/%{name}/*
%{_usr}/src/%{name}-%{moduleversion}


