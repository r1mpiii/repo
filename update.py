#!/usr/bin/env python3
"""Rebuilds Packages, Packages.gz, Packages.bz2 and Release from the debs/ folder.
Usage: python3 update.py   (needs only Python 3 + dpkg-deb; on GitHub Actions it is automatic)"""
import os, subprocess, hashlib, gzip, bz2, glob, time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
entries = []
for deb in sorted(glob.glob("debs/*.deb")):
    ctrl = subprocess.check_output(["dpkg-deb", "-f", deb]).decode("utf-8").strip("\n")
    data = open(deb, "rb").read()
    ctrl += f"\nFilename: {deb}\nSize: {len(data)}"
    ctrl += f"\nMD5sum: {hashlib.md5(data).hexdigest()}"
    ctrl += f"\nSHA1: {hashlib.sha1(data).hexdigest()}"
    ctrl += f"\nSHA256: {hashlib.sha256(data).hexdigest()}"
    entries.append(ctrl)
packages = ("\n\n".join(entries) + "\n\n").encode("utf-8")
open("Packages", "wb").write(packages)
open("Packages.gz", "wb").write(gzip.compress(packages, 9))
open("Packages.bz2", "wb").write(bz2.compress(packages, 9))

files = ["Packages", "Packages.gz", "Packages.bz2"]
def block(name, fn):
    return "".join(f" {fn(open(f,'rb').read()).hexdigest()} {os.path.getsize(f)} {f}\n" for f in files)
rel = open("Release.base", encoding="utf-8").read().rstrip("\n") + "\n"
rel += "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime()) + "\n"
rel += "MD5Sum:\n" + block("md5", hashlib.md5)
rel += "SHA256:\n" + block("sha256", hashlib.sha256)
open("Release", "w", encoding="utf-8").write(rel)
print(f"Done: {len(entries)} package(s)")
