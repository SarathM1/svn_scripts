#!/usr/bin/python
import subprocess
import yaml
import pandas as pd
import re
import yodl

def run_cmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    return output, err

class svn_info():
    def __init__(self, each_dir):
        self.count = {}
        cmd = "svn info {}".format(each_dir)
        output, err = run_cmd(cmd)
        self.count['revision_num'] = self.parse(output, 'Revision')
        temp = self.parse(output, 'Last Changed Date')
        self.count['date_commit'],self.count['time_commit'] = self.parse_date(temp)
        self.count['author'] =self.parse(output, 'Last Changed Author')

    def parse_date(self, string):
        time_ = string.split(' ')[1]
        m = re.search('\((\w+),(\s\w+\s\w+\s\w+)', string)
        if m:
            wod = m.group(1)
            date = m.group(2).split(' ')
        dateString = wod + ', ' + date[1] + ' ' + date[2] + ' ' + date[3]
        return dateString, time_

    def parse(self, output, pattern):
        match = re.search('(?<=' + pattern + ': ).*$', output, re.MULTILINE)
        if match:
            res = match.group()
            return res
        else:
            print 'No match'

class svn_status():
    def __init__(self, each_dir):
        cmd = "svn status {}".format(each_dir)
        output, err = run_cmd(cmd)

        self.unv_pattern = re.compile(r'^\?.*$', re.MULTILINE)

        self.count = {}
        self.parse(output)


    def parse(self, output):
        self.count['unversioned'] = len(re.findall(r'^\?.*$', output, re.MULTILINE))
        self.count['modified'] = len(re.findall(r'^M.*$', output, re.MULTILINE))
        self.count['added'] = len(re.findall(r'^A.*$', output, re.MULTILINE))
        self.count['deleted_svn'] = len(re.findall(r'^D.*$', output, re.MULTILINE))
        self.count['deleted_rm'] = len(re.findall(r'^!.*$', output, re.MULTILINE))
        if len(output) == 0:
            self.count['repo_state'] = 'clean'
        else:
            self.count['repo_state'] = 'dirty'

def main():
    with open('./test.yml', 'r') as stream:
        try:
            # dirs = yaml.load(stream)
            dirs = yaml.load(stream, yodl.OrderedDictYAMLLoader)
            data = []
            # for each_dir in dirs:
            for key, module in dirs['modules'].iteritems():
                row = {}
                row['path'] = module['path']
                row['owner'] = module['owner']

                info = svn_info(module['path'])
                for each_key, each_val in info.count.iteritems():
                    row[each_key] = each_val

                status = svn_status(module['path'])
                for each_key, each_val in status.count.iteritems():
                    row[each_key] = each_val

                data.append(row)
            df = pd.DataFrame(data)
            df.to_csv("repo_status.csv")
            # print "Data: \n", df
        except yaml.YAMLError as exc:
            print(exc)

if __name__ == '__main__':
    main()
