#!/usr/bin/env python3
#
# Netzint AD-Edit Pw Hash for linuxmuster.net 7.x
#
# v0.0.3 / 06.03.2020 - andreas.till@netzint.de
# v0.0.4 / 09.01.2023 - lukas.spitznagel@netzint.de

import subprocess
import argparse

def getSambaDomain():
    with open("/var/lib/linuxmuster/setup.ini") as f:
        for line in f.readlines():
            if "basedn" in line:
                return line.split("=")[1].strip()
    return "DC=linuxmuster,DC=lan"

def getDNs():
    dns=subprocess.check_output("ldbsearch --url=/var/lib/samba/private/sam.ldb -b " + getSambaDomain() + " | grep ^dn | awk '{ print $2 }'", shell=True)
    dnArray=dns.decode().split("\n")
    return dnArray

def getDN(host):
    for dn in getDNs():
        if host.lower() in dn.lower():
            return dn
    return None

def updateUnicodePwd(dn, password):
    print("Updating host %s with password %s" % (dn, password))
    modify = "dn: " + dn + "\nchangetype: modify\nreplace: unicodePwd\nunicodePwd:: " + password
    returnMessage=subprocess.check_output("echo  \'"  + modify + "\' | ldbmodify --url=/var/lib/samba/private/sam.ldb --nosync --verbose --controls=relax:0 --controls=local_oid:1.3.6.1.4.1.7165.4.3.7:0 --controls=local_oid:1.3.6.1.4.1.7165.4.3.12:0; ls", shell=True)

def updateSupplementalCredentials(dn, supplementalCredentials):
    print("Updating supplementalCredentials for host %s!" % dn)
    modify = "dn: " + dn + "\nchangetype: modify\nreplace: supplementalCredentials\nsupplementalCredentials:: " + supplementalCredentials
    returnMessage=subprocess.check_output("echo  \'"  + modify + "\' | ldbmodify --url=/var/lib/samba/private/sam.ldb --nosync --verbose --controls=relax:0 --controls=local_oid:1.3.6.1.4.1.7165.4.3.7:0 --controls=local_oid:1.3.6.1.4.1.7165.4.3.12:0; ls", shell=True)

def updateFromMACCT(dn, macct):
    print("Updating host %s with new macct-File!" % dn)
    modify = macct.replace("@@dn@@", dn)
    returnMessage=subprocess.check_output("echo  \'"  + modify + "\' | ldbmodify --url=/var/lib/samba/private/sam.ldb --nosync --verbose --controls=relax:0 --controls=local_oid:1.3.6.1.4.1.7165.4.3.7:0 --controls=local_oid:1.3.6.1.4.1.7165.4.3.12:0; ls", shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set machine password to ad object')
    parser.add_argument('-H', '--host', required = True, help='hostname')
    parser.add_argument('-p', '--password', required = False, help='paassword string')
    parser.add_argument('-s', '--supplementalCredentials', required = False, help='supplementalCredentials path')
    parser.add_argument('-m', '--macct', required = False, help='Path to macct file')
    args = parser.parse_args()

    dn = getDN(args.host)
    if dn is not None:
        if args.macct:
            with open(args.macct) as f:
                updateFromMACCT(dn, f.read())
        if args.password:
            updateUnicodePwd(dn, args.password)
        if args.supplementalCredentials:
            with open(args.supplementalCredentials) as f:
                updateSupplementalCredentials(dn, f.read())
    else:
        print("Host %s not found!" % dn)
