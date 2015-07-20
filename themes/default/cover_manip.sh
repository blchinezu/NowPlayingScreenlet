#!/bin/bash

# by Bruce Lee
#
#  When this script is executed the cover image is already copied to its
# location. So you just modify what you want about the cover and then leave it
# under the same name and extension. After the script finishes, the cover is
# loaded by the screenlet.
#
#  This makes possible the creation of very nice themes but it will direct the
# 'Open cover with viewer' and 'Open cover location' actions to this modified
# cover, not the original one

here=`echo $0 | sed -e 's/\/'$(basename $0)'$//'`
if [ "$here" = "`basename $0`" ]; then here="`pwd`"; fi
cd $here

# resize
convert -resize 244x246\! "cover.png" "newcover.png"
mv "newcover.png" "cover.png"
# extract alpha mask from image
convert "cover.png" -alpha extract "mask2.png"
# multiply the alpha masks
convert "mask2.png" "mask.png" -compose Over -composite "maskfinal.png"
mv "maskfinal.png" "mask2.png"
# apply the final alpha mask
convert "cover.png" "mask2.png" -alpha Off -compose Copy_Opacity -composite "newcover.png"
mv "newcover.png" "cover.png"

# clean
rm -f mask2.png

