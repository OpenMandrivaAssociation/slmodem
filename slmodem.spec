# I love OpenSource :-(

%define name slmodem
%define version 2.9.11
%define snapshot 20060727
%define mdkrelease 0.%{snapshot}.3
%define release %mkrel %{mdkrelease}
%define url http://www.smlink.com/main/down
#	    http://linmodems.technion.ac.il/packages/smartlink/

Summary:	slmodem utility.
Name:		%{name}
Version:	%{version}
Release:	%{release}
Source0:	%{name}-%{version}-%{snapshot}.tar.bz2
Patch0:		%{name}-2.9.9-dkms.patch
Patch1:		%{name}-2.9.10-mdkize.patch
License:	SmartLink
Group:		System/Kernel and hardware
BuildRoot:	%{_tmppath}/%{name}-buildroot
Url:		%{url}
Prefix:		%{_prefix}
Requires:	drakxtools >= 9.2-8mdk
BuildRequires:	libalsa-devel
ExclusiveArch:	%{ix86}

%description
slmodem driver utility.

%package -n dkms-%{name}
Summary:	slmodem module.
Group:		System/Kernel and hardware
Requires:	dkms, drakxtools >= 9.2-8mdk

%description -n dkms-%{name}
slmodem module Linux driver.

%prep
%setup
%patch0 -p1 -b .dkms
%patch1 -p1 -b .mdkize

%build
%make -C modem SUPPORT_ALSA=1

%install
rm -rf $RPM_BUILD_ROOT
cd $RPM_BUILD_DIR/%{name}-%{version}

# utils 
mkdir -p $RPM_BUILD_ROOT/%{_sbindir}
install -m755 modem/slmodemd modem/modem_test $RPM_BUILD_ROOT/%{_sbindir}
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig $RPM_BUILD_ROOT/%{_sysconfdir}/rc.d/init.d
install -m644 scripts/suse/slmodemd.conf $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/slmodemd
install -m755 scripts/mandrake/slmodemd $RPM_BUILD_ROOT/%{_sysconfdir}/rc.d/init.d/

# driver source
mkdir -p $RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{version}
cp -r * $RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{version}
rm -rf $RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{version}/{patches,scripts}
cat > $RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{version}/dkms.conf <<EOF
PACKAGE_NAME=%{name}
PACKAGE_VERSION=%{version}

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
for conf in /etc/modules /etc/modprobe.preload ; do
	if [[ -f $conf ]];then
		grep -q '^slamr$' $conf || echo slamr >> $conf
	fi
done
# prevent slamr loading
/sbin/modprobe slamr >/dev/null 2>&1 || :
/sbin/modprobe slusb >/dev/null 2>&1 || :
echo "Relaunch drakconnect to configure your slmodem cards"

%preun
%_preun_service slmodemd
if [[ $1 = "0" ]];then
for conf in /etc/modules /etc/modprobe.preload ; do
	if [[ -f $conf ]];then
		if grep -q slamr $conf;then
			grep -v '^slamr$' $conf > /tmp/modules.tmp.$$ && \
			mv /tmp/modules.tmp.$$ $conf
		fi
	fi
done
fi

%post -n dkms-%{name}
set -x
/usr/sbin/dkms --rpm_safe_upgrade add -m %name -v %version
/usr/sbin/dkms --rpm_safe_upgrade build -m %name -v %version
/usr/sbin/dkms --rpm_safe_upgrade install -m %name -v %version

%preun -n dkms-%{name}
set -x
/usr/sbin/dkms --rpm_safe_upgrade remove -m %name -v %version --all

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc COPYING Changes README
%{_sbindir}/*
%{_sysconfdir}/sysconfig/slmodemd
%{_sysconfdir}/rc.d/init.d/slmodemd

%files -n dkms-%{name}
%defattr(-,root,root)
%doc %{_docdir}/%{name}-%{version}/*
%dir %{_usr}/src/%{name}-%{version}
%{_usr}/src/%{name}-%{version}/*


