from pathlib import Path
import base64, html, json, shutil
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

ROOT=Path(__file__).resolve().parent
FONTDIR=ROOT/'fontes'
for n in ['Regular','Bold']:
    p=FONTDIR/f'LiberationSans-{n}.ttf'
    if not p.exists(): shutil.copy(f'/usr/share/fonts/truetype/liberation/LiberationSans-{n}.ttf',p)
    pdfmetrics.registerFont(TTFont('Planner'+n,str(p)))
W,H=148,210
C=canvas.Canvas(str(ROOT/'planner-diario-A5.pdf'),pagesize=(W*mm,H*mm),pageCompression=1)
C.setTitle('Planner diário — 01 e 02 de janeiro')
C.setAuthor('Recriação vetorial a partir de referência fornecida')
css=''.join("@font-face{font-family:Planner; font-weight:%s;src:url(data:font/ttf;base64,%s) format('truetype');}"%(weight,base64.b64encode((FONTDIR/f'LiberationSans-{name}.ttf').read_bytes()).decode()) for name,weight in [('Regular',400),('Bold',700)])

class Page:
 def __init__(self):
  self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="148mm" height="210mm" viewBox="0 0 148 210"><title>Planner diário A5</title><defs><style>{css}</style></defs>']
 def rect(self,x,y,w,h,fill='none',stroke='none',sw=.15,dash=None,rx=0):
  self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash} {dash}"' if dash else '')+'/>')
  C.saveState();C.setLineWidth(sw*mm)
  if fill!='none': C.setFillColor(fill)
  if stroke!='none': C.setStrokeColor(stroke)
  if dash:C.setDash(dash*mm,dash*mm)
  if rx:C.roundRect(x*mm,(H-y-h)*mm,w*mm,h*mm,rx*mm,fill=fill!='none',stroke=stroke!='none')
  else:C.rect(x*mm,(H-y-h)*mm,w*mm,h*mm,fill=fill!='none',stroke=stroke!='none')
  C.restoreState()
 def line(self,x,y,x2,y2,stroke='#bdbdbd',sw=.13):
  self.s.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"/>')
  C.setStrokeColor(stroke);C.setLineWidth(sw*mm);C.line(x*mm,(H-y)*mm,x2*mm,(H-y2)*mm)
 def circle(self,x,y,r,fill='none',stroke='none',sw=.13):
  self.s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
  if fill!='none': C.setFillColor(fill)
  if stroke!='none': C.setStrokeColor(stroke)
  C.setLineWidth(sw*mm);C.circle(x*mm,(H-y)*mm,r*mm,stroke=stroke!='none',fill=fill!='none')
 def text(self,x,y,txt,size=2.8,bold=False,fill='#222222',anchor='start'):
  self.s.append(f'<text x="{x}" y="{y}" font-family="Planner, Liberation Sans, Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}" text-anchor="{anchor}">{html.escape(txt)}</text>')
  C.setFont('Planner'+('Bold' if bold else 'Regular'),size*mm);C.setFillColor(fill)
  fn={'start':C.drawString,'middle':C.drawCentredString,'end':C.drawRightString}[anchor]
  fn(x*mm,(H-y)*mm,txt)
 def bar(self,x,y,w,label):
  self.rect(x,y,w,4.5,fill='#242424');self.text(x+w/2,y+3.25,label,2.85,True,'#ffffff','middle')
 def save(self,name): (ROOT/name).write_text(''.join(self.s)+'</svg>',encoding='utf-8');C.showPage()

for idx,(day,weekday,select,holiday) in enumerate([('01','SEXTA',4,'ANO NOVO'),('02','SÁBADO',5,'')]):
 p=Page();p.rect(0,0,W,H,fill='#ffffff')
 x=5.5 if idx==0 else 17.5
 full=125; gap=1; small=(full-2*gap)/3; main=2*small+gap; agenda=x+main+gap
 top=6; head=27.7
 p.bar(x+small+gap,top,small,'FOCO DE HOJE');p.bar(agenda,top,small,'HÁBITOS')
 p.rect(x+small+gap,top+4.5,5,16.2,fill='#f1f1f1')
 for k in range(3):
  yy=top+4.5+(k+1)*5.4
  p.line(x+small+gap,yy,x+main,yy);p.line(agenda,yy,agenda+small,yy)
  p.rect(agenda,yy-3.5,2.85,2.85,stroke='#b0b0b0',rx=.25)
 center=x+small/2
 p.text(center,12.8,f'{day} DE JANEIRO',4.2,anchor='middle')
 letters=['S','T','Q','Q','S','S','D']
 start=center-13
 for k,s in enumerate(letters):
  xx=start+k*4.333
  p.text(xx,16.8,s,1.95,fill='#777777',anchor='middle')
  if k<6:p.text(xx+2.16,16.65,'·',1.6,fill='#aaaaaa',anchor='middle')
  if k==select:p.circle(xx,16.05,1.42,stroke='#aaaaaa',sw=.12)
 p.text(center,22.5,weekday,4.2,anchor='middle')
 if holiday:p.text(center,25.2,holiday,1.9,fill='#777777',anchor='middle')
 p.bar(x,head,main,'DESENVOLVA 3 PRINCIPAIS PRIORIDADES')
 p.bar(agenda,head,small,'AGENDA')
 startY=head+4.5; row=5.055
 for k in range(34):
  yy=startY+k*row
  hour=6+k//2;minute='30' if k%2 else '00'
  if hour in (12,18) and minute=='00':p.rect(agenda,yy,small,row,fill='#eeeeee')
  p.text(agenda+.1,yy+3.25,f'{hour:02}:{minute}',1.95,fill='#666666')
  p.line(agenda,yy+row,agenda+small,yy+row)
 for k in range(3):
  yy=startY+k*24.4
  p.rect(x,yy,main,23.4,stroke='#888888',sw=.12,dash=.35)
  p.text(x+1,yy+2.6,f'{k+1:02}',1.95,fill='#666666')
 p.bar(x,105.8,main,'DIÁRIO / NOTAS')
 for k in range(9):p.line(x,115.35+k*5.05,x+main,115.35+k*5.05)
 p.bar(x,156.95,main,'ESPAÇO LIVRE')
 for r in range(8):
  for c in range(17):p.circle(x+2+c*4.95,166.7+r*4.95,.19,fill='#c3c3c3')
 p.save(f'planner-{day}-janeiro.svg')
C.save()
print(ROOT/'planner-diario-A5.pdf')
