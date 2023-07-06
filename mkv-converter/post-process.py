#!/usr/bin/env python3

import os
import re
import sys
import shutil

from enum import Enum

from move import Copier
from convert import Converter

from resources.log import getLogger
from resources.readsettings import ReadSettings

def getBehaviour():
    return

log = getLogger("qBittorrentPostProcess")

log.info("qBittorrent post processing started.")
log.info("#Args: %R %F %N %I RootPath, ContentPath , TorrentName, InfoHash")
log.info(str(sys.argv))

if len(sys.argv) != 5:
    log.error("Incorrect number of command line parameters present (should be 5), are you launching this from qBittorrent?")
    log.error("Length is %s" % str(len(sys.argv)))
    sys.exit(1)

try:
    #settings = ReadSettings()
    root_path = str(sys.argv[1])
    content_path = str(sys.argv[2])
    name = sys.argv[3]
    torrent_hash = sys.argv[4]

    log.info("#Arg: Root Path: %s" % root_path)
    log.info("#Arg: Content Path: %s" % content_path)
    log.info("#Arg: Torrent hash: %s" % torrent_hash)
    log.info("#Arg: Torrent name: %s" % name)

    # Import python-qbittorrent
    try:
        from qbittorrent import Client
    except ImportError:
        log.exception("Python module PYTHON-QBITTORRENT is required. Install with 'pip install python-qbittorrent' then try again.")
        sys.exit(1)

    settings = ReadSettings()
    # Perform post-processing
    log.info("Performing post-processing")

    delete_dir = False
    settings.delete = False

    # The output directory is set automatically: go up one location from the root path and create a directory there as [name]    
    output_folder = 'processed'
    settings.output_dir = os.path.abspath(os.path.join(root_path, '..', output_folder, ("%s" % (re.sub(settings.regex, '_', name)))))
    if not os.path.exists(settings.output_dir):
        try:
            os.makedirs(settings.output_dir)
        except:
            log.exception("Unable to make output directory %s." % settings.output_dir)
 
    # The output behaviour is determined by the extension of the file
    #   - .mp4: copy this file to the final location and delete original file
    #   - .mkv: convert and copy this file to the processed location, copy the processed file to the final location and delete the processed file
    #   - .$other: do nothing

    # There are two processing cases: single file and multiple files
    converter = Converter(settings, 
                          root_path,
                          content_path)
    converted = converter.convert()
    if converted:
        copy_from_path = settings.output_dir
    else:
        copy_from_path = content_path

    copier = Copier(settings, copy_from_path)
    copier.copy()

    if os.path.exists(copy_from_path):
        if os.path.isfile(copy_from_path):
            try:
                os.remove(copy_from_path)
                log.info("Successfully removed file: %s." % copy_from_path)
            except:
                log.exception("Unable to delete file: %s." % copy_from_path)
        else:
            try:
                shutil.rmtree(copy_from_path) 
                log.info("Successfully removed directory: %s." % copy_from_path)
            except:
                    log.exception("Unable to delete directory: %s" % copy_from_path)
    log.info("Finished: post-processing completed successfuly.")
except:
    log.exception("Unexpected exception.")
    sys.exit(1)
