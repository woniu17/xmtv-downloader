#!/usr/bin/env python

import ConfigParser
import commands

host_dict = {}
film_dict = {}
cf_file = 'config.ini'
cf = None
def read_config():
    global host_dict
    global film_list
    global cf_file
    global cf
    cf = ConfigParser.ConfigParser()
    cf.read(cf_file)

    #host dict
    host_dict = cf._sections['hosts']
    #print host_dict

    #film dict
    s = cf.sections()
    film_list = filter(lambda ss: ss.startswith('film-'), s)
    #print film_list
    for f in film_list:
        film = cf._sections[f]
        if film['download'] == 'no':
            film_dict[f] = film
        '''
        print film['name']
        print film['count']
        print film['vedio-001-url']
        '''
def download_video(video_url, video_dir):
    #print 'video_url:', video_url
    #print 'video_dir:', video_dir
    video_url = video_url[:-5]
    #create video dir
    cmd = 'mkdir -p %s' % (video_dir,)
    status, output = commands.getstatusoutput(cmd)
    #print status, output
    #download video
    for i in xrange(50):
        video_url_i = '%s%d.mp4' % (video_url, (i+1))
        video_name = video_url_i[(video_url_i.rfind('/') + 1):]
        #cmd = 'wget %s -O %s/%s' % (video_url_i, video_dir, video_name)
        cmd = 'wget %s?wsiphost=local -O %s/%s' % (video_url_i, video_dir, video_name)
        status, output = commands.getstatusoutput(cmd)
        #print status, output
        print cmd
        #log
        if output.find('100%') < 0:
            cmd = 'echo "\tfail to download video %s into %s\n%s" >> download.log'\
            % (video_name, video_dir, output)
            print cmd
            commands.getstatusoutput(cmd)
            cmd = 'rm -rf %s/%s' % (video_dir, video_name)
            print cmd
            commands.getstatusoutput(cmd)
            break
        #succssful
        cmd = 'echo "\tdownload video %s into %s" >> download.log'\
            % (video_name, video_dir)
        commands.getstatusoutput(cmd)
        print cmd

def download_film(film):
    film_dir = film['name']
    video_count = int(film['video-count'])
    #print 'film_dir:', film_dir
    #print 'video_count:', video_count

    #log
    cmd = 'echo "download film %s into %s, video count:%s" >> download.log'\
        % (film['name'], film_dir, video_count)
    print cmd
    status, output = commands.getstatusoutput(cmd)
    #print status, output

    for vc in xrange(video_count):
        key = 'video-%03d-url' % (vc + 1)
        video_url = film[key]
        video_dir = '%s/%03d' % (film_dir, vc + 1)
        download_video(video_url, video_dir)

if __name__ == '__main__':
    read_config()
    #print film_dict
    for fid, film in film_dict.items():
        download_film(film)
        cf.set(fid, 'download', 'yes')
        cf.write(open(cf_file, 'w'))
