#!/home/teroot/miniconda3/envs/jupyter/bin/python3
import subprocess
import yaml
import pandas as pd
import re
import yodl
import os

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
        self.count['author'] = self.parse(output, 'Last Changed Author')

    def parse_date(self, string):
        time_ = string.split(' ')[1]
        m = re.search('\((\w+),(\s\w+\s\w+\s\w+)', string)
        if m:
            wod = m.group(1)
            date = m.group(2).split(' ')
        dateString = wod + ', ' + date[1] + ' ' + date[2] + ' ' + date[3]
        return dateString, time_

    def parse(self, output, pattern):
        match = re.search(b'(?<=' + bytes(pattern,'utf-8') + b': ).*$', output, re.MULTILINE)
        if match:
            res = match.group()
            return res.decode('utf-8')
        else:
            print ('No match')

class svn_status():
    def __init__(self, each_dir):
        cmd = "svn status {}".format(each_dir)
        output, err = run_cmd(cmd)

        self.unv_pattern = re.compile(r'^\?.*$', re.MULTILINE)

        self.count = {}
        self.parse(output)


    def parse(self, output):
        # output = str(output)
        output = output.decode('utf-8')
        print(type(output))
        self.count['unversioned'] = len(re.findall(r'^\?.*$', output, re.MULTILINE))
        self.count['modified'] = len(re.findall(r'^M.*$', output, re.MULTILINE))
        self.count['added'] = len(re.findall(r'^A.*$', output, re.MULTILINE))
        self.count['deleted_svn'] = len(re.findall(r'^D.*$', output, re.MULTILINE))
        self.count['deleted_rm'] = len(re.findall(r'^!.*$', output, re.MULTILINE))
        if len(output) == 0:
            self.count['repo_state'] = 'clean'
        else:
            self.count['repo_state'] = 'dirty'
        print(self.count['unversioned'])

def parse_mod_name(path):
    split = path.split('/')
    if len(split[-1]) != 0:
        name = split[-1]
    else:
        name = split[-2]
    return name

def main():
    with open('./test.yml', 'r') as stream:
        try:
            dirs = yaml.load(stream, yodl.OrderedDictYAMLLoader)
            data = []
            for key, module in dirs['modules'].items():
                row = {}
                row['path'] = module['path']
                row['name'] = parse_mod_name(row['path'])
                row['owner'] = module['owner']

                info = svn_info(module['path'])
                for each_key, each_val in info.count.items():
                    row[each_key] = each_val

                status = svn_status(module['path'])
                for each_key, each_val in status.count.items():
                    row[each_key] = each_val

                data.append(row)
            df = pd.DataFrame(data)
            df.to_csv("repo_status.csv")
        except yaml.YAMLError as exc:
            print(exc)

if __name__ == '__main__':
    main()
