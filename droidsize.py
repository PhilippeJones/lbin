#!/usr/bin/python
import sys
from getopt import getopt, GetoptError
import os.path
from subprocess import Popen, PIPE
import shutil

def usage():
    print "droidsize.py - Android Image Sizing Utility"
    print ""
    print "This tool will resize an image to the smaller Android sizes"
    print "and place them in the respective resource folder."
    print ""
    print "This defaults to the same imagefile name the image size to xxhdpi,"
    print "and the drawable to mdpi."
    print ""
    print "  Usages:"
    print "    droidsize.py [-h, --help]"
    print "    droidsize.py [options] imagefile resroot"
    print ""
    print "  Options:"
    print "    -v, --verbose"
    print "    -s, --size xxhdpi|xhdpi|hdpi|mdpi"
    print "    -n, --name filename"

def main(argv):
    if len(argv) == 0:
        usage()
        sys.exit(2)
    
    try:
        opts, args = getopt(argv, "hvs:n:", ["help", "verbose", "size=", "name="])
    except GetoptError:
        usage()
        sys.exit(2)

    verbose = False
    size = "xxhdpi"
    name = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-s", "--size"):
            size = arg
        elif opt in ("-n", "--name"):
            name = arg
    
    if len(args) < 2:
        usage()
        sys.exit(2)
    
    source = args[0]
    resources = args[1]
    
    if name is None:
        name = source.split("/")[-1]
    
    densities = {}
    if size == "mdpi":
        densities["mdpi"] = 1.0
    elif size == "hdpi":
        densities["mdpi"] = 1.0
        densities["hdpi"] = 1.5
    elif size == "xhdpi":
        densities["mdpi"] = 1.0
        densities["hdpi"] = 1.5
        densities["xhdpi"] = 2.0
    elif size == "xxhdpi":
        densities["mdpi"] = 1.0
        densities["hdpi"] = 1.5
        densities["xhdpi"] = 2.0
        densities["xxhdpi"] = 3.0
    else:
        print "%s is not a valid size, must be one of mdpi, hdpi, xhdpi, xxhdpi." % (size)
        print ""
        usage()
        sys.exit(2)
    
    if not os.path.isfile(source):
        print "%s is not a file or does not exist." % (source)
        print ""
        usage()
        sys.exit(2)
    
    if not os.path.isdir(resources):
        print "%s is not a directory or does not exist." % (resources)
        print ""
        usage()
        sys.exit(2)

    source_response = Popen("sips -g pixelWidth -g pixelHeight %s" % (source), shell=True, stdout=PIPE)
    source_width = None
    source_height = None
    for line in source_response.stdout:
        if "pixelWidth" in line:
            source_width = int(line.split(": ", 1)[1].strip())
        if "pixelHeight" in line:
            source_height = int(line.split(": ", 1)[1].strip())

    if verbose:
        print "Source %s (%s, %s) %s" % (source, source_width, source_height, size)
    
    for density, scale in densities.iteritems():
        drawable_path = "%s/drawable-%s" % (resources, density);
        if not os.path.isdir(drawable_path):
            if verbose:
                print "Creating directory %s" % (drawable_path)
            os.makedirs(drawable_path)
        
        file_path = "%s/%s" % (drawable_path, name)
        if density == size:
            if verbose:
                print "Copying %s to %s" % (source, file_path)
            shutil.copyfile(source, file_path)
        else:
            factor = scale / densities[size]
            width = int(float(source_width) * factor)
            height = int(float(source_height) * factor)
            if verbose:
                print "Resizing %s to %s (%s, %s)" % (source, file_path, width, height)
            resize_response = Popen("sips -z %s %s %s --out %s" % (height, width, source, file_path), shell=True, stderr=PIPE, stdout=PIPE)
            output, errors = resize_response.communicate()
            if resize_response.returncode:
                print "Could not resize %s to %s" % (source, file_path)
                print errors
                sys.exit(2)
    
    sys.exit(0)
    
if __name__ == "__main__":
    main(sys.argv[1:])
