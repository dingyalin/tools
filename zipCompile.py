# encoding=utf-8

import os
import sys
import zipfile


if __name__ == "__main__":
    zip_file_name = sys.argv[1]
    zip_file_path = sys.argv[2]
    print zip_file_name, zip_file_path
    
    destZip = zipfile.ZipFile(zip_file_name, "w", compression=zipfile.ZIP_DEFLATED)

    for dirpath, dirs, files in os.walk(zip_file_path):
        zipdirpath = (dirpath + "\\").replace(zip_file_path + "\\", "").replace("\\", "/")
        print "zipdirpath=" + zipdirpath
        
       
        for filename in files:
            sourcefile = dirpath + "\\" + filename
            targetfile = (zipdirpath + filename if zipdirpath != "" else filename) 
            
            destZip.write(sourcefile, targetfile)
            
            #print "%s-->%s" % (sourcefile, targetfile)
        
            
            
        if len(files) == 0:
            destZip.writestr(zipdirpath, "")
            #print zipdirpath + "/"
       
        
    destZip.close()
