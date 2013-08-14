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
    print "    -s, --size xxhdpi|xhdpi|hdpi|mdpi|ldpi"
    print "    -n, --name filename"
    print "    -d, --drawable xxhdpi|xhdpi|hdpi|mdpi|ldpi"

def main(argv):
    if len(argv) == 0:
        usage()
        sys.exit(2)
    
    try:
        opts, args = getopt(argv, "hvs:n:d:", ["help", "verbose", "size=", "name=", "drawable="])
    except GetoptError:
        usage()
        sys.exit(2)

    verbose = False
    size = "xxhdpi"
    name = None
    drawable = "mdpi"

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
        elif opt in ("-d", "--drawable"):
            drawable = arg
    
    if len(args) < 2:
        usage()
        sys.exit(2)
    
    source = args[0]
    resources = args[1]
    
    if name is None:
        name = source.split("/")[-1]
    
    densities = {}
    if size == "ldpi":
        densities["ldpi"] = 0.75
    elif size == "mdpi":
        densities["ldpi"] = 0.75
        densities["mdpi"] = 1.0
    elif size == "hdpi":
        densities["ldpi"] = 0.75
        densities["mdpi"] = 1.0
        densities["hdpi"] = 1.5
    elif size == "xhdpi":
        densities["ldpi"] = 0.75
        densities["mdpi"] = 1.0
        densities["hdpi"] = 1.5
        densities["xhdpi"] = 2.0
    elif size == "xxhdpi":
        densities["ldpi"] = 0.75
        densities["mdpi"] = 1.0
        densities["hdpi"] = 1.5
        densities["xhdpi"] = 2.0
        densities["xxhdpi"] = 3.0
    else:
        print "%s is not a valid size, must be one of ldpi, mdpi, hdpi, xhdpi, xxhdpi." % (size)
        print ""
        usage()
        sys.exit(2)
    
    if densities[drawable] is None:
        print "%s is not a valid drawable, must be one of ldpi, mdpi, hdpi, xhdpi, xxhdpi." % (drawable)
        print ""
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
    
    drawable_path = "%s/drawable" % (resources);
    if not os.path.isdir(drawable_path):
        if verbose:
            print "Creating directory %s" % (drawable_path)
        os.makedirs(drawable_path)
    drawable_source_path = "%s/drawable-%s/%s" % (resources, drawable, name)
    drawable_file_path = "%s/%s" % (drawable_path, name)
    if verbose:
        print "Copying %s to %s" % (drawable_source_path, drawable_file_path)
    shutil.copyfile(drawable_source_path, drawable_file_path)
    
    sys.exit(0)
    
if __name__ == "__main__":
    main(sys.argv[1:])
