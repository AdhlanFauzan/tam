#coding: utf-8
from django.conf import settings
import os
from django.template.loader import get_template
from django.template.context import Context
import StringIO
import xhtml2pdf.pisa as pisa
from django import http
import cgi
import copy
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import * #@UnusedWildImport
from reportlab.pdfgen import canvas
from reportlab.platypus import Image as FlowableImage
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4, portrait, landscape
from reportlab.lib import colors
from decimal import Decimal
from django.templatetags.l10n import localize

def render_with_pisa(template_src, context_dict):
	template = get_template(template_src)
	context = Context(context_dict)
	html = template.render(context)
	result = StringIO.StringIO()
	pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("utf-8")), dest=result,
						link_callback=fetch_resources)
	if not pdf.err:
		return http.HttpResponse(result.getvalue(), mimetype='application/pdf')
	return http.HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))

def fetch_resources(uri, rel):
	path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
	return path




def moneyfmt(value, places=2, curr='', sep='.', dp=',',
			 pos='', neg='-', trailneg=''):
	"""Convert Decimal to a money formatted string.
	
	places:  required number of places after the decimal point
	curr:	optional currency symbol before the sign (may be blank)
	sep:	 optional grouping separator (comma, period, space, or blank)
	dp:	  decimal point indicator (comma or period)
			 only specify as blank when places is zero
	pos:	 optional sign for positive numbers: '+', space or blank
	neg:	 optional sign for negative numbers: '-', '(', space or blank
	trailneg:optional trailing minus indicator:  '-', ')', space or blank
	
	>>> d = Decimal('-1234567.8901')
	>>> moneyfmt(d, curr='$')
	'-$1,234,567.89'
	>>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
	'1.234.568-'
	>>> moneyfmt(d, curr='$', neg='(', trailneg=')')
	'($1,234,567.89)'
	>>> moneyfmt(Decimal(123456789), sep=' ')
	'123 456 789.00'
	>>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
	'<0.02>'
	
	"""
	q = Decimal(10) ** -places	  # 2 places --> '0.01'
	sign, digits, exp = value.quantize(q).as_tuple()
	result = []
	digits = map(str, digits)
	build, next = result.append, digits.pop
	if sign:
		build(trailneg)
	for i in range(places):
		build(next() if digits else '0')
	build(dp)
	if not digits:
		build('0')
	i = 0
	while digits:
		build(next())
		i += 1
		if i == 3 and digits:
			i = 0
			build(sep)
	build(curr)
	build(neg if sign else pos)
	return ''.join(reversed(result))



def render_to_reportlab(context):
	fattura = context.get('fattura')
	test = False
	
	class NumberedCanvas(canvas.Canvas):
		def __init__(self, *args, **kwargs):
			canvas.Canvas.__init__(self, *args, **kwargs)
			self._saved_page_states = []
	
		def showPage(self):
			self._saved_page_states.append(dict(self.__dict__))
			self._startPage()
	
		def save(self):
			"""add page info to each page (page x of y)"""
			num_pages = len(self._saved_page_states)
			for state in self._saved_page_states:
				self.__dict__.update(state)
				self.draw_page_number(num_pages)
				canvas.Canvas.showPage(self)
			canvas.Canvas.save(self)
	
		def draw_page_number(self, page_count):
			self.setFont("Helvetica", 7)
			self.drawRightString(width/2, 1*cm,
				"Pagina %d di %d" % (self._pageNumber, page_count))

	def firstPageTemplate(canvas, doc):
		canvas.saveState()
		stondata_style = ParagraphStyle("IntestazioneStondata", fontName='Helvetica', fontSize=8, leading=10,
									 borderRadius=10, borderWidth=1, borderColor=colors.silver, borderPadding=15)
		title_style = ParagraphStyle("Titolo della fattura", fontName='Helvetica-Bold', fontSize=10, leading=10)
		a_style = ParagraphStyle("Titolo della fattura", fontName='Helvetica', fontSize=8, leading=10)

		# set PDF properties ***************
		canvas.setFont('Helvetica', 8)
		canvas.setAuthor(settings.LICENSE_OWNER)
		canvas.setCreator('TaM v.%s' % settings.TAM_VERSION)
		canvas._doc.info.producer = ('TaM invoices')
		canvas.setSubject(u"%s" % fattura.nome_fattura())
		descrittoreFattura = u"%s %s/%s" % (fattura.nome_fattura(), fattura.anno, fattura.progressivo)
		canvas.setTitle(descrittoreFattura)

		# Header ***************
		y = height - 4 * cm
		logo_x, logo_y = canvas.drawImage(logoImage_path, x=1 * cm, y=y, width=7 * cm, height=2.5 * cm)
		descrittore = Paragraph('<font size="12"><b>%s</b></font> del %s' % (descrittoreFattura, localize(fattura.data)),
								 a_style)
		descrittore.wrapOn(canvas, width / 2, 2 * cm)
		y -= descrittore.height + 8
		descrittore.drawOn(canvas, x=1 * cm, y=y)


		if fattura.note:
			note = Preformatted(fattura.note, a_style)
			note.wrapOn(canvas, width / 2, 10 * cm)
			y = y - note.height - 8
			note.drawOn(canvas, 1 * cm, y=y)
		left_y = y - 10


		fattura_da = canvas.beginText()
		fattura_da.setTextOrigin(width - 8 * cm, height - 2 * cm)
		fattura_da.textLines(fattura.emessa_da)
		canvas.drawText(fattura_da)

		fattura_a = Paragraph(fattura.emessa_a.replace('\n', '<br/>'), stondata_style)
		fattura_a.wrapOn(canvas, 6.5 * cm, 10 * cm)
		x, y = fattura_da.getCursor()

		spacerMittenteDestinatario = 1 * cm
		fattura_a.drawOn(canvas, x, y - fattura_a.height - spacerMittenteDestinatario)

		y -= fattura_a.height + fattura_a.style.borderPadding * 2 + spacerMittenteDestinatario
		right_y = y
		lower_y = min(left_y, right_y)

		y = lower_y
		if test:
			canvas.setLineWidth(4)
			p = canvas.beginPath()
			p.moveTo(0, y); p.lineTo(width, y)
			canvas.drawPath(p)

		doc.pageTemplate.frames = [
				Frame(1 * cm, 1.7 * cm, width - 2 * cm, y - (2 * cm), showBoundary=test), #x,y, width, height
			]

		canvas.restoreState()


	response = http.HttpResponse(mimetype='application/pdf')
	width, height = portrait(A4)

	doc = BaseDocTemplate(response,
							pagesize=portrait(A4),
							leftMargin=1.5 * cm,
							rightMargin=1.5 * cm,
							bottomMargin=1.5 * cm,
							showBoundary=test,
							pageTemplates=PageTemplate(onPage=firstPageTemplate),
						)

	logoImage_path = os.path.join(settings.MEDIA_ROOT, 'fatture/logo.jpg')

	styles = getSampleStyleSheet()
	normalStyle = copy.deepcopy(styles['Normal'])
	normalStyle.fontSize = 8
	normalStyle.fontName = 'Helvetica'
	righeFattura = [
					('Descrizione', 'Q.tà', 'Prezzo', 'IVA %', 'Importo'),
				]

	for riga in fattura.righe.all():
		righeFattura.append((
							Paragraph(riga.descrizione, normalStyle),
							Paragraph("%s" % riga.qta, normalStyle),
							moneyfmt(riga.prezzo), riga.iva, moneyfmt(riga.val_totale())
							))
	righeTotali = []
	righeTotali.append((
						'Imponibile', moneyfmt(fattura.val_imponibile())
						))
	righeTotali.append((
						'IVA', moneyfmt(fattura.val_iva())
						))
	righeTotali.append((
						'TOTALE', moneyfmt(fattura.val_totale())
						))
	righeStyle = TableStyle([
					('VALIGN', (0, 0), (-1, -1), 'TOP'),
					('ALIGN', (0, 0), (-1, -1), 'RIGHT'), 	# globalmente allineato a destra...
					('ALIGN', (0, 0), (1, -1), 'LEFT'), 	# tranne la prima colonna (con la descrizione)
					('GRID', (0, 1), (-1, -1), 0.1, colors.grey),
					('FACE', (0, 0), (-1, -1), 'Helvetica'),

					('FACE', (0, 0), (-1, 0), 'Helvetica-Bold'), 	# header
					('SIZE', (0, 0), (-1, -1), 8),

					#('SPAN', (0, -1), (3, -1)),	# anziché mettere lo span qui aggiungo in coda una tabella diversa
			])
	totaliStyle = TableStyle([
							('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
							('GRID', (-1, 0), (-1, -1), 0.1, colors.grey),

							('FACE', (0, 0), (-1, -1), 'Helvetica'), 	# header
							('FACE', (0, -1), (-1, -1), 'Helvetica-Bold'), 	# Totale
							('SIZE', (0, 0), (-1, -1), 8),

						])

	colWidths = ((width - 2 * cm) - (1.6 * 4) * cm,) + (1.6 * cm,) * 4
	story = [ Table(righeFattura, style=righeStyle, repeatRows=1, colWidths=colWidths) ]
	story.append(KeepTogether(Table(righeTotali, style=totaliStyle, colWidths=(width - 2 * cm - 1.6 * cm, 1.6 * cm))))
	story.append(Spacer(0, 2 * cm))
	note_finali = Paragraph("Si prega di effettuare il pagamento sul conto Corrente:<br/>" +
								"UNICREDIT BANCA SPA - Agenzia di Montegrotto Terme IBAN: IT94 x 02008 62680 000040451824<br/>" +
								"<font size='6'>Ai sensi dell'art. 13 del D.L. 196/2003 sulla tutela della privacy, vi informiamo di aver inserito i dati anagrafici e fiscali che ci avete fornito nei nostri archivi informatici.</font>"
								, normalStyle)
	note_finali.wrap(width - 4 * cm, 2 * cm)
	story.append(note_finali)

	doc.build(story, canvasmaker=NumberedCanvas)
	return response
