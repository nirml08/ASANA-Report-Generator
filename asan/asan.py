'''this script scrapes the asana data and formats the data into a report format which contains the details about the tickets such as its assignee
source,state within a given date range'''



import asana as asn
import json
from asana import Client as cl
import pandas as pd
import collections
from datetime import datetime as td
import asancfg as cfg




def asana_report(flag,frm,till):

	act=cl.access_token(cfg.access_token)
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
	story_lst=[]
	story_dict={}
	cmnt_add_lst=[]
	cmnt_lst=[]

	tsk_lst=act.tasks.find_all({'project':cfg.project_id})
	#fetching all tasks present in project
	for l in tsk_lst:
		lst.append(l)
	#saving all task to a list.

	for i in lst:
		tsk_id_lst_old.append(i['id'])

	
	
	for t in tsk_id_lst_old:
		tmp=act.tasks.find_by_id(t)
		tckt_date=tmp['created_at'][:10]
		tckt_obj=td.strptime(tckt_date, '%Y-%m-%d')
		if check_range(frm,till,tckt_obj):
			tsk_id_lst.append(t)
			users.append(tmp['name'])
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
		stry=(act.stories.find_by_task(tsk_id))
		comment=''
		for sto in stry:
			story_lst.append(sto)
		for each_story in story_lst:
			#print(type(each_story))
			if each_story.values()[0] == 'comment_added':
				c=''
				#print(type(cmnt_add_lst))
				#if each_story['created_by']['id'] == uid:
				#cmnt_add_lst.append((each_story['text']))
				if flag==0:									#extracts only comments made by assignee for the ticket
					if each_story['created_by']['id'] == tmp['assignee']['id']:
						c=each_story['text']
						creation_time=each_story['created_at']
						by=each_story['created_by']['name']
				else:
					c=each_story['text']
					creation_time=each_story['created_at']
					by=each_story['created_by']['name']
				#for itr in c:
				comment=comment+c+'\n '+by+' : '+creation_time#+itr
				comment=comment+"\n"
		cmnt_lst.append(comment)
		story_lst=[]
		cmnt_add_lst=[]	
	proj_name=tmp['projects'][0]['name']
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
			if ky == 'due_at':
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

	#for i in range(len(tsk_id_lst)):
		#serial.append(i)
	print("\n creating report of project "+proj_name+" for past 10 days at asan/report.csv ")
	
	data=collections.OrderedDict([("CREATED_AT",time),("MEMBER",assigned),("SOURCE",source),("TICKET NAME",user_name),("ISSUE DETAILS",issue),("ACTION",actions),("STAGE",sections),("COMMENT",cmnt_lst),("INSTANT RESOLVE",inst_res),("Production Tracker No.",bug_no)])
		
	#data=collections.OrderedDict({"USER NAME":user_name,"ISSUE DETAILS":issue,"ACTION":actions,"COMMENT":cmnt_lst,"MEMBER":assigned,"Production Tracker 		No.":bug_no,"SOURCE":source,"DATE":time,"INSTANT RESOLVE":inst_res})

	df=pd.DataFrame(data)
	
	df.to_csv(r'/home/nirml/Desktop/asan/report.csv',encoding='utf-8')
	print('\nReport creation completed...')	


def check_range(frm_obj,till_obj,tckt_obj):
	from datetime import datetime as dt
	#frm_obj=dt.strptime(frm, '%Y-%m-%d')
	#till_obj=dt.strptime(till, '%Y-%m-%d')
	#tckt_obj=dt.strptime(tckt_date, '%Y-%m-%d')
	if tckt_obj >= frm_obj and tckt_obj <= till_obj:
		return True
	else:
		return False




if __name__=="__main__":
	print '#'*15,'ASANA REPORT GENERTAOR','#'*15
	print("\n ###Please enter yoyr choice :")
	print("\n ###Enter 1 to include all comments on an issue in the report:")
	print("\n ###Enter 0 to include only comments by assignee  wise:")
	flag = input(">>>")
	print("From :")
	frm=input("Format yyyy-mm-dd")
	print("Till :")
	till=input('Format yyyy-mm-dd')
	if till == '.':
		till_obj=td.today()
	else:
		till_obj=td.strptime(till, '%Y-%m-%d')
	frm_obj=td.strptime(frm, '%Y-%m-%d')
	asana_report(flag,frm_obj,till_obj)
	
		

			






