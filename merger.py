#!/usr/bin/env python
#MP4Box -cat part1.mp4 -cat part2.mp4 -new joinedfile.mp4

import ConfigParser
import commands
import os

film_dict = {}
cf_file = 'config.ini'
cf = None
def read_config():
    global film_list
    global cf_file
    global cf
    cf = ConfigParser.ConfigParser()
    cf.read(cf_file)

    #film dict
    s = cf.sections()
    film_list = filter(lambda ss: ss.startswith('film-'), s)
    #print film_list
    for f in film_list:
        film = cf._sections[f]
        if film['download'] == 'yes' and film['merge'] == 'no':
            film_dict[f] = film
        '''
        print film['name']
        print film['count']
        print film['vedio-001-url']
        '''
def merge_video(video_url, video_dir, video_name):
    print 'video_url:', video_url
    print 'video_dir:', video_dir
    print 'video_name:', video_name
    video_url = video_url[:-5]
    #merge video
    #concat = 'concat:1.ts|2.ts'
    count = 1
    for i in xrange(50):
        video_url_i = '%s%d.mp4' % (video_url, (i+1))
        video_name_i = video_url_i[(video_url_i.rfind('/') + 1):]
        path = '%s/%s' % (video_dir, video_name_i)
        if os.path.isfile(path):
            cmd = 'ffmpeg -y -i %s -vcodec copy -acodec copy -vbsf h264_mp4toannexb %s/%d.ts' % (path, video_dir, (i+1))
            print cmd
            commands.getstatusoutput(cmd)
            count += 1
        else :
            break
    #we assume that there is always more than one ts
    final_ts = '%s/1.ts' % (video_dir)
    i = 2
    while i <= count:
        append_ts = '%s/%d.ts' % (video_dir, i)
        concat = 'concat:%s|%s' % (final_ts, append_ts)
        path = '%s/%s' % (video_dir, video_name)
        cmd = 'ffmpeg -y -i "%s" -acodec copy -vcodec copy -absf aac_adtstoasc %s' % (concat, path)
        print cmd
        commands.getstatusoutput(cmd)
        #turn mp4 to ts
        cmd = 'ffmpeg -y -i %s -vcodec copy -acodec copy -vbsf h264_mp4toannexb %s/final.ts' % (path, video_dir,)
        print cmd
        commands.getstatusoutput(cmd)
        final_ts = '%s/final.ts' % (video_dir)
        i += 1
    cmd = 'mv %s %s/..' % (path, video_dir)
    print cmd
    commands.getstatusoutput(cmd)
    #rm *.ts
    cmd = 'rm -rf %s/*.ts' % (video_dir)
    print cmd
    commands.getstatusoutput(cmd)

def merge_film(film):
    film_dir = film['name']
    video_count = int(film['video-count'])
    #print 'film_dir:', film_dir
    #print 'video_count:', video_count

    #log
    cmd = 'echo "merge film %s into %s, video count:%s" >> merge.log'\
        % (film['name'], film_dir, video_count)
    print cmd
    status, output = commands.getstatusoutput(cmd)
    #print status, output

    for vc in xrange(video_count):
        key = 'video-%03d-url' % (vc + 1)
        video_url = film[key]
        video_dir = '%s/%03d' % (film_dir, vc + 1)
        video_name = '%s-%03d.mp4' % (film['name'], vc+1)
        merge_video(video_url, video_dir, video_name)

if __name__ == '__main__':
    read_config()
    for fid, film in film_dict.items():
        merge_film(film)
        cf.set(fid, 'merge', 'yes')
        cf.write(open(cf_file, 'w'))
