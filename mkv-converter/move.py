import logging
import os
import re
import shutil

MOVIES_LOCATION = "/mnt/pi-movies/Movies"
TV_LOCATION = "/mnt/pi-media/Media/TV"

#TEST_STRING = 

class Copier:
    def __init__(self, settings, content_path, logger=None):
        self.log = logger or logging.getLogger(__name__)
        self.content_path = content_path
        self.settings = settings


    def extract_title_and_year(self, file):
        pattern = r'^(.*?)(\d{4})'
        match = re.search(pattern, file)
        return match.group(1).title(), match.group(2)
    
    def extract_tv_info(self, file):
        pattern = r'^(.+?)[\.]?([sS]\d{2}[eE]\d{2})'
        match = re.search(pattern, file)
        tv_show = match.group(1)
        tv_show = re.sub(r'[^a-zA-Z0-9\s]', ' ', tv_show)
        tv_show = re.sub(r'\s+', ' ', tv_show).strip()
        tv_show = tv_show.title()
        episode_code = match.group(2)
        return tv_show, episode_code[1:3], episode_code[4:6]

    def rename_folder_and_file(self, inputfile):
        root, file = os.path.split(inputfile)
        filename, ext = os.path.splitext(file)
        if ext != '.mp4':
            return '', ''
        # Determine if TV Show episode or Film
        pattern = r'\b[sS]\d{2}[eE]\d{2}\b'
        match = re.search(pattern, filename)
        if match:
            tv_show, season, episode = self.extract_tv_info(filename)
            season_string = 'Season ' + str(int(season))
            folder = os.path.join(TV_LOCATION, tv_show, season_string)
            file = tv_show + ' s' + season + 'e' + episode + ext
            return folder, file
        else:
            title, year = self.extract_title_and_year(filename)
            title = re.sub(r'[^a-zA-Z0-9\s]', ' ', title)
            title = re.sub(r'\s+', ' ', title).strip()
            movie_folder = title + ' (' + year + ')'
            folder = os.path.join(MOVIES_LOCATION, movie_folder)
            file = title + ext
            return folder, file

    def copy(self):
        if os.path.isfile(self.content_path):
            inputfile = self.content_path
            self.log.info("Copying single file: %s" % inputfile)
            folder, output_file = self.rename_folder_and_file(inputfile)
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder)
                except:
                    self.log.exception("Unable to make output directory %s." % folder)
            if folder != '' and output_file != '':
                destination_path = os.path.join(folder, output_file)
                self.log.info("Copying file %s to %s" % (inputfile, destination_path))
                shutil.copy(inputfile, destination_path)
                
        else:
            self.log.info("Copying files from folder: %s" % self.content_path)
            for root, dirs, files in os.walk(self.content_path):
                for file in files:
                    inputfile = os.path.join(root, file)
                    print(f'Inputfile: {inputfile}')
                    folder, output_file = self.rename_folder_and_file(inputfile)
                    if not os.path.exists(folder):
                        try:
                            os.makedirs(folder)
                        except:
                            self.log.exception("Unable to make output directory %s." % folder)
                    if folder != '' and output_file != '':
                        destination_path = os.path.join(folder, output_file)
                        self.log.info("Copying file %s to %s" % (inputfile, destination_path))
                        shutil.copy(inputfile, destination_path)              
                        