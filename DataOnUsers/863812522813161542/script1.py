from ast import literal_eval

with open("test.txt","r") as text:
	string_list = (text.readlines()[0])
	a = [i.split('.')[-1] for i in literal_eval(string_list)]

	for x in a:
		print(x.split(":")[0])



		
