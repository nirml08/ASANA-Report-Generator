import asana
import pandas as pd
import configparser
from datetime import datetime as td
import time

config = configparser.ConfigParser()
config.read("/home/nirml/Desktop/debug/config.ini")
at = config.get("Users", "security_token")
ws = config.get("Users", "workspacename")
pro = config.get("Users", "projectname")

# at=input("Enter your AccessToken: ")
client = asana.Client.basic_auth(at)
workspaces = client.workspaces.find_all({"opt_fields": "is_organization, name"})
# ws=input("Enter your workspacename: ")
workspace = next(workspace for workspace in workspaces if workspace['name'] == ws)
projects = client.projects.find_by_workspace(workspace['id'])
# pro=input("Enter your projectname: ")
project = next(project for project in projects if project['name'] == pro)

print("\n ........................... Creating Report .............................\n")

tasks = client.tasks.find_by_project(project['id'], {"opt_fields": "name, \
            projects, workspace, id, due_on, created_at, modified_at, completed, \
            completed_at, assignee, assignee_status, parent, notes"})
task_list = []
for task in tasks:
    if (task == ''):
        break
    assignee = task['assignee']['id'] if task['assignee'] is not None else ''
    created_at = task['created_at'][0:10] if \
        task['created_at'] is not None else None
    modified_at = task['modified_at'][0:10] if \
        task['modified_at'] is not None else None
    completed_at = task['completed_at'][0:10] if \
        task['completed_at'] is not None else None
    rec = [task['name'], project['name'], task['due_on'], td.strptime(created_at, '%Y-%m-%d'), \
           modified_at, task['completed'], completed_at, assignee, \
           task['assignee_status'], task['parent'], task['notes'], task['id']]
    rec = ['' if s is None else s for s in rec]
    task_list.append(rec)
df = pd.DataFrame(task_list)
k = []
for i in df[7]:
    if (i == ""):
        k.append(i)
    else:
        us = client.users.find_by_id(i)
        k.append(us['name'])
kdf = pd.DataFrame(k)
df[7] = kdf
complt_stage_dt = []
t_com = []
ch_i = config.get("Users", "reporttype")  # choice for the report type
if (ch_i == 'all'):

    for l in df[11]:
        l = str(l)
        path = "/tasks/" + l + "/stories"  # df[11] contains task_ids
        story = client.request(method="get", path=path)
        comment = ""
        stage_dt = 0
        count = 0
        for i in story:
            if (i['resource_subtype'] == "comment_added"):
                comment = comment + "\n" + i['created_by']['name'] + " : " + i['created_at'][0:10] + ' ' \
                          + i['created_at'][11:16] + "\n" + i['text']

            if (i['resource_subtype'] == "section_changed"):
                text = i['text']
                indx = text.find('to')
                sect = text[indx + 3:]
                if sect == "Done":
                    count += 1
                    stage_dt = (i['created_at'][0:10])
        complt_stage_dt.append(stage_dt)  # here true stage_dt means it was moved to the final section
        t_com.append(comment)  # all the comment details are added to list
    pass
elif (ch_i == 'assignee'):
    t_com = []
    c = 0
    for l in df[11]:
        c = c + 1
        cp = 0
        for k in df[7]:  # df[7] col contains assignee names
            cp = cp + 1
            if (c == cp):
                break

        l = str(l)
        path = "/tasks/" + l + "/stories"
        story = client.request(method="get", path=path)
        comment = ""
        for i in story:
            if (i['resource_subtype'] == "comment_added" and i['created_by']['name'] == k):
                comment = comment + "\n " + i['created_by']['name'] + " " + i['created_at'][0:10] + ' : ' + "\n" + i[
                    'text']
        t_com.append(str(comment))

t_c = pd.DataFrame(t_com)
# df=pd.concat([df,t_c],axis=1)
df.insert(11, 'Comment', t_c)

df.columns = ['TaskName', 'ProjectName', 'Task_due_on', 'Created_at', 'Modified_at', 'Task_completed', 'completed_at',
              'assigne', 'assigne_status', 'task_parent', 'Notes', 'Comment', 'Task_id']

section_list = []
for t in df['Task_id']:
    mm = client.tasks.find_by_id(t)
    for i in mm['memberships']:

        if (i['section']['name'] != ''):
            section_list.append(i['section']['name']) if i['section']['name'] != 'Template' else section_list.append('NA')
            break
df.insert(1, 'Section_name', pd.DataFrame(section_list))
due_date = []  # due_date is list of strings not date
priority=[]
for i in range(0, len(df['Task_due_on'])):
    if complt_stage_dt[i] != 0:  # here 0 points that the task has never been moved to final section
        if (df['Task_due_on'][i] != '') and (
                td.strptime(complt_stage_dt[i], '%Y-%m-%d') <= td.strptime(df['Task_due_on'][i], '%Y-%m-%d')):
            due_date.append("Completed within due date")
        else:
            due_date.append("Completed over due date")
        continue
    else:
        if (df['Task_due_on'][i] != ''):
            i = td.strptime(df['Task_due_on'][i], '%Y-%m-%d')
            priority.append(int((td.today()-i).days))
            if (td.today() >= i):
                due_date.append("Due date crossed")
            else:
                due_date.append("With in due date")
        else:
            due_date.append("Due Not Set")
            priority.append('Due Not set')
due_date = pd.DataFrame(due_date)
df.insert(2, 'Due_date_status', due_date)
complt_stage = pd.DataFrame(complt_stage_dt)
df.insert(3, 'Done_section_dt', complt_stage)
prio=pd.DataFrame(priority)
df.insert(16,'Priority',prio)


def check(row):
    if (row['Done_section_dt'] != 0 and row['Created_at'] != ''):
        rsd = td.strptime(row['Done_section_dt'], '%Y-%m-%d')  # rsd is the date on which task was sent to done section
        return str((rsd - row['Created_at']).days)+str(' days')
    else:
        return 'NA'
def check_again(row):
    if (row['Done_section_dt'] != 0 and row['Task_due_on'] != ''):
        dd = td.strptime(row['Done_section_dt'], '%Y-%m-%d')  # rsd is the date on which task was sent to done section
        dud=td.strptime(row['Task_due_on'], '%Y-%m-%d')
        return (dud-dd).days
    else:
        return 'NA'

##def priority():
    #if (row['Task_due_on'] != 0 and row['Created_at'] != ''):
        #dud = td.strptime(row['Task_due_on'], '%Y-%m-%d')

# df['completed_at - Task_due_on'] = df.apply(lambda row : check(row), axis = 1)
df['Ticket Elapse time'] = df.apply(lambda row: check(row), axis=1)
df['Completion points'] = df.apply(lambda row: check_again(row), axis=1)
df=df.drop(['Task_id'],axis=1)
# print(df['completed_at - Task_due_on'])
beg_t = config.get("Users", "start_time")
end_t = config.get("Users", "end_time")
report_file = config.get("Users", "file_path")
if (beg_t != "" and end_t != ""):
    beg_t = td.strptime(beg_t, '%Y-%m-%d')
    end_t = td.strptime(end_t, '%Y-%m-%d')
    df = df[(df['Created_at'] >= beg_t) & (df['Created_at'] <= end_t)]

df.to_csv(report_file, encoding='utf-8')

print("\n .............................Done.............................. \n")

# df.to_csv("asana_slack_report.csv")
