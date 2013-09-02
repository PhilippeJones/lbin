#!/bin/sh
if [ -f /Developer ]; then
	echo "Deleting the /Developer directory"
	sudo rm -fr /Developer
fi
if [ -f /Library/Developer ]; then
	echo "Deleting the /Library/Developer directory"
	sudo rm -fr /Library/Developer
fi
cd ~/Library
if [ -f Developer ]; then
	echo "Deleting the ~/Library/Developer directory"
	rm -fr Developer
fi
echo "Deleting any preferences, caches, etc."
find . -name "com.apple.dt.*" -exec rm -fr {} \;
find . -name "com.apple.Xcode*" -exec rm -fr {} \;

