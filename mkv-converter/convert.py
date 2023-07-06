import logging
import os
import sys

from resources.mediaprocessor import MediaProcessor

class Converter:
    def __init__(self, 
                 settings, 
                 root_path, 
                 content_path, 
                 logger=None):
        self.root_path = root_path
        self.content_path = content_path
        self.settings = settings
        self.mp = MediaProcessor(settings)
        self.log = logger or logging.getLogger(__name__)

    def convert(self):
        if os.path.isfile(self.content_path):
            inputfile = self.content_path
            info = self.mp.isValidSource(inputfile)
            if info:
                self.log.info("Converting single file to mp4: %s." % inputfile)
                try:
                    output = self.mp.process(inputfile, reportProgress=True, info=info)
                    if not output:
                        self.log.error("No mp4 file generated for this single file torrent, aborting.")
                        sys.exit(1)
                    self.log.info("Successfully converted %s." % inputfile)
                    return True   
                except:
                    self.log.exception("Error converting file %s." % inputfile)
            else:
                self.log.info("File is not a valid source, aborting.")
                sys.exit(1)
        else:
            ignore = []
            self.log.info("Converting multiple files to mp4.")
            for r, d, files in os.walk(self.root_path):
                for file in files:
                    inputfile = os.path.join(r, file)
                    info = self.mp.isValidSource(inputfile)
                    if info and inputfile not in ignore:
                        self.log.info("Converting file %s." % inputfile)
                        try:
                            output = self.mp.process(inputfile, info=info)
                            if output and output.get('output'):
                                ignore.append(output.get('output'))
                                self.log.info("Successfully converted %s." % inputfile)
                            else:
                                self.log.error("No mp4 file generated for file %s."  % inputfile)
                        except:
                            self.log.exception("Error converting file %s." % inputfile)
                    else:
                        self.log.debug("Ignoring file %s." % inputfile)
            if len(ignore) < 1:
                self.log.error("No mp4 files generated for this mutliple file torrent, aborting.")
                sys.exit(1)
            return True
