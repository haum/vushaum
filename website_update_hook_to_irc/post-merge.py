#!/usr/bin/env python

"""
Script to be uses as a git hook (post-merge) to retrieve every new articles of git repository haum/website_content
(files in articles/*.rst)
Then call the famous bot Haumbotox to send messages to Twaum

Installation :
--------------
- Change variable "haumbotox_cmd" to point to vushaum_repo/clirc/clirc
- ln -s <THIS SCRIPT.PY> <PATH_TO_HAUM_WEBSITE/.git/hook/post-merge

"""

import subprocess
import logging
import re
import time

# settings
log_level = logging.DEBUG  # can be changed to logging.DEBUG
logfile = r"/tmp/website_post_merge_log.log"
log_to_file = False
log_to_console = True

website_root_url = "http://www.haum.org/{slug}.html"  # will be used to generate urls ending with 'article/*.rst
twaum_msg = "@tweet {summary} ({url})"  # Change here the IRC message sent for each new articles

summary_max_len = 100  # summary will be truncated to this value and '...' will be appended

git_cmd = "git diff-tree --no-commit-id --name-status -r HEAD -- articles/*rst | grep A | cut -f 2"
haumbotox_cmd = '/PATH/TO/VUSHAUM/REPOSITORY/clirc/clirc {params}'
haumbotox_cmd = '/home/rebrec/projets/haum/vushaum/clirc/clirc {params}'

def _get_tag_value(tag, line):
    return line.split(':',2)[2].strip()

def send_cmd_to_haumbotox(summary, url):
    irc_msg = twaum_msg.format(summary=summary, url=url)
    logger.debug("Prepared IRC msg : %s " % irc_msg)
    cmd = haumbotox_cmd.format(params=re.escape(irc_msg))
    logger.debug("Prepared Shell Command to launch haumbotox msg : %s " % cmd)
    cmd_output = subprocess.check_output(cmd, shell=True)
    #logger.debug("Command result : \n%s " % cmd_output)



def get_article_infos(filename):
    if filename[-3::].lower() == 'rst':
        logger.debug("Good Extension for %s" % filename)
        infos = dict()

        for line in open(filename,'r').readlines()[0:15]: # not useful to read more than 15 lines
            if ':summary:' in line:
                infos['summary'] = _get_tag_value('summary',line)
                infos['summary'] = infos['summary'][0:summary_max_len+1] + '...'
                logger.debug('\t summary %s ' % infos['summary'])
            elif ':slug:' in line:
                infos['url'] = website_root_url.format(slug=_get_tag_value('slug',line))
                logger.debug('\t url %s ' % infos['url'])
        return infos
    else:
        logger.debug("Bad Extension for %s" % filename)
        return None



if __name__ == '__main__':
    #### Log initialization
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    # create a file handler
    if log_to_file:
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
    # same for console handler (stdout)
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

    #### Code Starts Here
    logger.info('***************** Start *****************')
    cmd_output = subprocess.check_output(git_cmd, shell=True)
    logger.debug('result of git "%s" gives : \n %s' %(git_cmd,cmd_output))
    new_files = cmd_output.split('\n')
    for filename in new_files:
        if len(filename) > 0:
            infos = get_article_infos(filename)
            if infos:
                logger.info('New File %s (%s) ==> %s' % (filename, infos['url'], infos['summary']))
                send_cmd_to_haumbotox(**infos)
                time.sleep(2)

