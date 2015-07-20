#!/bin/bash

here=`echo $0 | sed -e 's/\/'$(basename $0)'$//'`
if [ "$here" = "`basename $0`" ]; then here="`pwd`"; fi
cd $here

convert -resize 291x246\! "cover.png" "newcover.png"
mv "newcover.png" "cover.png"
convert "cover.png" "mask.png" -alpha Off -compose Copy_Opacity -composite "newcover.png"
mv "newcover.png" "cover.png"

