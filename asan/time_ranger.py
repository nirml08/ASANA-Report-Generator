from datetime import datetime as td

def time_check(beg,end,mid):
	beg_t=td.strptime(beg, '%Y-%m-%d')
	#beg_t is the starting date od date range
	end_t=td.strptime(end, '%Y-%m-%d')
	#end_t refers to the end date of the date range
	mid_t=td.strptime(mid, '%Y-%m-%d')
	#mid_t is any date that lies between the above two
	if mid_t >= beg_t and mid_t <=end_t
		return True
	else:
		return False

