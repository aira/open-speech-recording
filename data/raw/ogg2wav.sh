#!/usr/bin/env bash

OLDPWD="$PWD"

if [ -d "$1" ] ; then
    cd $1 ;
fi

for f in *.ogg ; do
	if [ -f "${f/%ogg/wav}" ] ; then
		echo "Skipping ogg2wav ${f}" ;
	else
		ffmpeg -i "$f" "${f/%ogg/wav}" ;
	fi
done

cd "$OLDPWD" ;
