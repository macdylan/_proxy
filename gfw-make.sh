#!/bin/sh

# FckGFW
#
# Created by Dylan on 3/14/10.
# Copyright 2010 ~. All rights reserved.


if [ -z "$1" ]; then
    echo "usage: gfw-make.sh domain"
    exit
fi

DIRNAME=$(cd $(dirname "$0"); pwd)
GFWLIST="$DIRNAME/gfw.list"
EXIST=`grep "$1" "$GFWLIST" | wc -l | sed 's/ //g'`
if [ "$EXIST" == 0 ]; then
    echo $1 >> "$GFWLIST"
    `$DIRNAME/make.py`
else
    echo "Domain '$1' exist."
fi

