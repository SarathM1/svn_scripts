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
        self.count['revision_num'] =self.parse(output, 'Revision')
        self.count['date'] =self.parse(output, 'Last Changed Date')
        self.count['author'] =self.parse(output, 'Last Changed Author')

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
        print output, '\n'
        self.count['unversioned'] = len(re.findall(r'^\?.*$', output, re.MULTILINE))
        self.count['modified'] = len(re.findall(r'^M.*$', output, re.MULTILINE))
        self.count['deleted'] = len(re.findall(r'^D.*$', output, re.MULTILINE))

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
            print "Data: \n", df
        except yaml.YAMLError as exc:
            print(exc)

if __name__ == '__main__':
    main()
