import os

dir = './LA FILES/'

res = open('index.html', 'w')
res.write("<script>const copyToClipboard = str => {const el = document.createElement('textarea');el.value = str;el.setAttribute('readonly', '');el.style.position = 'absolute';el.style.left = '-9999px';document.body.appendChild(el);el.select();document.execCommand('copy');document.body.removeChild(el);};</script>\n")
cont = 1
for filename in os.listdir(dir):
	file = open('./LA FILES/'+filename)
	res.write('\n\n<br><br>'+filename+'<br>\n')
	for line in file:
		tab = 0
		an = ''
		for ch in line:
			if ch != '#':
				if tab == 1:
					an += ch	
				if ch == '\t':
					tab += 1	
		if an != '':
			res.write(str(cont) + ' - <a target="_BLANK" href="https://www.ncbi.nlm.nih.gov/Structure/cdd/wrpsb.cgi?INPUT_TYPE=live&SEQUENCE='+an.strip()+'&mode=full">'+an.strip()+'</a> - ')
			res.write('<button onClick="copyToClipboard(\''+an.strip()+'\')">Copy</button><br>\n')
			cont += 1