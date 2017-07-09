#!/usr/bin/env bash
tmp="$(mktemp -d /tmp/gitpush.XXXXXX)"
cd "$tmp" || exit
git init --bare
cd ~/Documents || exit
git subtree split --prefix=odk/formgen -b formgen
git remote add tmp "$tmp"
git push tmp formgen:master
git branch -D formgen
git remote remove tmp
tmp2="$(mktemp -d /tmp/gitpush.XXXXXX)"
cd "$tmp2" || exit
git init
git remote add tmp "$tmp"
git pull tmp master
git remote add origin git@github.com:nilesr/formgen.git
git push origin master
cd ~||exit
rm -rf "$tmp" "$tmp2"
