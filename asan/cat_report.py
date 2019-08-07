'''creates a repeort of all tickets in a projects and groups them by according to
assignee and sorts according to due dat'''


import asana as asn
import json
from asana import Client as cl
import pandas as pd
import collections
import datetime
from datetime import datetime as dt




def asana_report(flag,till):

	act=cl.access_token("0/3e2def2173a11c8e674c8ee1a9fffbc0")
	uid=act.users.me()['id']
	#act.workspaces.find_all()
	#listing all projects in specified workspace
	#proj=act.projects.find_all({'workspace': '1116235306467540'})

	#selecting a particular project
	#listing all task present in project which are required for creating report
	lst,tsk_id_lst,tsk_id_lst_old,tsk_details,sections,issue_details,user_name,users,nots,serial=([] for i in range(10))
	actions,issue,assigned,bug_no,due_date=([] for i in range(5))
	source=[]
	date=[]
	time=[]
	inst_res=[]
	assignee_dict={}
	cmnt_add_lst=[]
	assignee_id=[]
	unassigned=[]
	task_assignee_id=[]

	tsk_lst=act.tasks.find_all({'project':'1133269201315620'})
	#fetching all tasks present in project
	for l in tsk_lst:
		lst.append(l)
	#saving all task to a list.

	for i in lst:
		tsk_id_lst_old.append(i['id'])

	
	
	for t in tsk_id_lst_old:
		tmp=act.tasks.find_by_id(t)
		tckt_date=tmp['created_at'][:10]				#checks if the ticket is within the given range
		if check_range(till,tckt_date):
			tsk_id_lst.append(t)
			users.append(tmp['name'])				#name of the issuer
		else:
			pass
	if len(tsk_id_lst) == 0:
		print("No tickets present from given date")
		exit()

	print("There are currently",len(tsk_id_lst),"tickets for give sate range")
	for nm in users:
		st="["
		ind=(nm.find(st))
		user_name.append(nm[:ind])
	
		
			
	for tsk_id in tsk_id_lst:
		tmp=act.tasks.find_by_id(tsk_id)
		tsk_details.append(tmp)

		
		
	#print(act.tasks.find_by_id('1132860158190652'))#['assignee']['name'])
	for el in tsk_details:
		for ky in el.keys():
			if ky == 'memberships':		#looking for membership in task details
				for it in (el[ky]):
					sections.append(it['section']['name'])
			if ky == 'notes':
				nots.append(el[ky])
			if ky == 'assignee':
				if el['assignee'] != None:
					asign=el[ky]
					assigned.append(el[ky]['name'])
				else:
					assigned.append('None')
			if ky == "created_at":
				time.append(el[ky][:10])
			if ky == 'due_on':
				due_date.append(el[ky])

	print(len(inst_res),len(time),len(bug_no),len(issue),len(actions))
	
				
	for i in nots:
		#print("[note]",i)
		st0=":"						#indicates source from notes
		ind0=(i.find(st0))
		if ind0 == -1:
			source.append("None")
		else:
			
			source.append(i[:ind0])


		st="##"						#indicates actions taken from notes
		ind=(i.find(st))
		if ind == -1:
			actions.append(None)		#extracting actions
		else:
			actions.append(i[(ind+1):-1])
		
		st2=">"						#indicates bug no from notes
		ind2=(i.find(st2))

		if ind2 == -1:
			inst_res.append("YES")
			bug_no.append("NONE")
		else:
			inst_res.append("NONE")
			bug_no.append(i[(ind2+1):ind])			#clip strng from > till #"
		
		issue.append(i[(ind0+1):ind2])				#clip from start to bug no 
		#actions.append(i[(ind+1):-1])		#clip bug no to actions taken	

	
	#print(cmnt_lst)
	
	#print(len(inst_res),len(time),len(bug_no),len(issue),len(actions),len(source),len(assigned),len(user_name))


	for task_detail in tsk_details:
		if type(task_detail['assignee']) == type({}):			#task_details refers to a single task
			assignee_dict.update({task_detail['assignee']['id']:task_detail['assignee']['name']})
			assignee_id.append(task_detail['assignee']['id'])
		else:
			unassigned.append(task_detail['id'])
	#print(tsk_details[2])
	
	df=pd.DataFrame()
	print(assignee_id)
	for k in assignee_dict.keys():
		data={'ASSIGN':[assignee_dict.get(k)],'ISSUE':[''],'SOURCE':[''],'INSTANT RESOLVED':[''],'CREATED AT':['']}
		ndf1=pd.DataFrame(data,index=(i for i in range(1,2)))
		df=df.append(ndf1)
		df_issue,df_created,df_inst_res,df_source=([] for i in range(4))
		for l in range(0,len(assignee_id)):
			if k == assignee_id[l]:
				#create list for data
				df_issue.append(issue[l])
				df_source.append(source[l])
				df_inst_res.append(inst_res[l])
				df_created.append(time[l])
		data={'ASSIGN':'','ISSUE':df_issue,'SOURCE':df_source,'INSTANT RESOLVED':df_inst_res,'CREATED AT':df_created}
		ndf2=pd.DataFrame(data,index=(i for i in range(0,len(df_source))))
		df=df.append(ndf2)
		
	#data=collections.OrderedDict([("CREATED_AT",time),("MEMBER",assigned),("SOURCE",source),("SERIAL",serial),("USER NAME",user_name),("ISSUE DETAILS",issue),("ACTION",actions),("INSTANT RESOLVE",inst_res),("Production Tracker No.",bug_no)])
		
	#df=pd.DataFrame(data)

	df.to_csv(r'/home/nirml/Desktop/asan/report3.csv',encoding='utf-8')
	print("\n creating report of past 10 days at asan/report3.csv ")


def check_range(till,tckt_date):
	from datetime import datetime as dt

	till_obj=till
	frm_obj=till_obj-datetime.timedelta(days=10)
	
	tckt_obj=dt.strptime(tckt_date, '%Y-%m-%d')
	if tckt_obj.date() >= frm_obj and tckt_obj.date() <= till_obj:
		return True
	else:
		return False




if __name__=="__main__":
	print('#'*20,'ASANA REPORT GENERTAOR','#'*20)	
	till=datetime.date.today()
	flag=1				#includes all the comments on a ticket in report
	print('#'*20, 'Generating Report OF Last Ten Days', '#'*20)
	asana_report(flag,till)



