#!/usr/bin/env bash

OLDPWD="$PWD"

if [ -d "$1" ] ; then
    DATADIR="$1"
else
    DATADIR="$HOME/src/open-speech-recording/data/raw"
fi

cd "$DATADIR"

scp -p cpu:open-speech-recording/data/*.ogg "$DATADIR/"

set -e

for f in *.ogg ; do
	if [ -f "${f/%ogg/wav}" ] ; then
		echo "Skipping ogg2wav ${f}" ;
	else
		ffmpeg -i "$f" "${f/%ogg/wav}" ;
        ssh cpu "rm -f *.ogg ~/open-speech-recording/data/$f"
	fi
done

for f in *.wav ; do
    audio --play "$f" ; 
    read  -n 1 -p "Delete File? [n]": ans ;

    if [ "$ans" == "y" ] ; then
        echo "DELETING" ;
        rm -f "$f" ;
        rm -f "${f/%wav/ogg}" ;
    fi
done

cd "$OLDPWD"
