from flask import Flask, render_template, send_file
import proxy
app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/menu')
def menu():
	return render_template('menu.html')

@app.route('/temp/<opcion>')
def tempHum(opcion):
	p = proxy.PROXY()
	h = None
	t = None
	if opcion == 'th':
		(t, h) = p.leerTemHume()
	elif opcion =='t':
		t = p.leerTem()
	elif opcion =='h':
		h = p.leerHume()
	p.close()

	tableTemp = None
	tableHum = None

	if (t != None):
		tableTemp = '<table><tr>'
		count = 0
		while count < 100:
			if (count<(t+40)*100/120):
				tableTemp += '<td style="background-color:#ff6666">&nbsp;</td>'
			else:
				tableTemp += '<td>&nbsp;</td>'
			count = count+1

		tableTemp += '</tr></table>'

	if (h != None):
		tableHum = '<table><tr>'

		count = 0
		while count < 100:
			if (count<(h)):
				tableHum += '<td style="background-color:#4c0000">&nbsp;</td>'
			else:
				tableHum += '<td>&nbsp;</td>'
			count = count+1

		tableHum += '</tr></table>'
	

	templateData = {
		'temp' : t,
		'hum' : h,
		'tableTemp': tableTemp,
		'tableHum': tableHum
	}
	return render_template('temperatura.html', **templateData)

@app.route('/img/<opcion>')
def raspImg(opcion):
	return send_file('templates/img/'+opcion, mimetype='img/png')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)