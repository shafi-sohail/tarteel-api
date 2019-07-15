#!/bin/sh

cd /tmp/
if [ "$(ls -A /tmp)" ]; then
    sudo rm -r *
fi
git clone https://github.com/AGWA/git-crypt.git /tmp/git-crypt
cd /tmp/git-crypt
make
make install
