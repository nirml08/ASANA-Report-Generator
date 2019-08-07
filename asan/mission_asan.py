from asana import Client as cl
import pandas as pd
import collections


def report_creator():

	task_list,task_id_list,task_details_list,user_name,as_task_list,un_task_list=([] for i in range(6))
	task_actions,notes_lst=([] for i in range(2))
	assignee_dict={}
	tckt_report=([] for i in range(1))
	#authentication part
	act=cl.access_token("0/3e2def2173a11c8e674c8ee1a9fffbc0")
	#account user name
	uid=act.users.me()['id']
	#listing all tasks in given project
	task_list=act.tasks.find_all({'project':'1132860158190642'})
	
	for i in act.tasks.find_all({'project':'1132860158190642'}):
		task_id_list.append(i['id'])	
		user_name.append(i['name'][:(i['name'].find("["))])


	#checking for task assigneee


#filtering of task based on dates and times could be done in this section
	for tid in task_id_list:			#accessing every task id to ask task details
		task_details_list.append(act.tasks.find_by_id(tid))
		

	for task_detail in task_details_list:
		if type(task_detail['assignee']) == type({}):			#task_details refers to a single task
			assignee_dict.update({task_detail['assignee']['id']:[]})	

	for task_detail in task_details_list:
		
		if type(task_detail['assignee']) == type({}):			#task_details refers to a single task		
			notes=task_detail['notes']
			tmp_id=task_detail['assignee']['id']
			assigned_name=task_detail['assignee']['name']
			fltr1=":"
			fltr2="##"
			fltr3=">"
	
			indx1=(notes.find(fltr1))
			if indx1 == -1:
				tckt_source=("None")
			else:
				tckt_source=(notes[:indx1])

			
			indx2=(notes.find(fltr2))
			if indx2 == -1:
				tckt_action=(None)		
			else:
				tckt_action=(notes[(indx2+1):-1])
			

			indx3=(notes.find(fltr3))
			if indx3 == -1:
				tckt_bugno=(None)		
			else:
				tckt_bugno=(notes[indx3:indx2])

			tckt_issue=(notes[(notes.find(fltr1)):(notes.find(fltr2))])
			tckt_report=[tckt_source,tckt_action,tckt_bugno]			

			if tmp_id in assignee_dict.keys():
				tmp=assignee_dict[tmp_id]
				tmp.append(tckt_report)
			
		else:
			un_task_list.append(tid)
	fh=open('/home/nirml/Desktop/asan/repot.txt','w')
	for k in assignee_dict.keys():
		for itr in assignee_dict[k]:
			write_str='source :',itr[0],',issue :',itr[1]
			fh.write('\n')
			fh.writelines(str(write_str))
#writelines(L) for L = [str1, str2, str3] 
	fh.close()
	

	
for ids in assignee_dict.keys():
		data.update(collections.OrderedDict([("assigned",','),("TICKET",','),("source",','),("Created",',')]))
		df1=pd.DataFrame(data)
		print(df1)
		df.append(df1)
		for itr in range(len(assignee_id)):
			if assignee_id[itr] == ids:
				data.update(collections.OrderedDict([("assigned",','),("TICKET",issue[itr]),("source",source[itr]),("Created",time[itr])]))
				df2=pd.DataFrame(data)
				print(df2)
				df.append(df2)

















if __name__ == "__main__":
	report_creator()
