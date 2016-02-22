#!/usr/bin/python
"""  MathQuiz.py | 2001-03-21     | Don Taylor
                   2004 Version 3 | Andrew Mathas

     Convert an XML quiz description file to an HTML file
     using CSS and JavaScript.

     See quiz.dtd for the DTD and mathquizXml.py for the
     Python object structure reflecting the DTD.

     27 Jan 03
     Swapped the position of the progress strip with
     the main text.  Added support for <meta> and <link>
     tags coming from the tex4ht conversion.
"""

VERSION   = 'MathQuiz 4.3'

# -----------------------------------------------------
import sys, os, mathquizXml


# -----------------------------------------------------
# Load local configuration files and set system variables
# -----------------------------------------------------
import mathquizConfig
MathQuizURL = mathquizConfig.MathQuizURL
Images = MathQuizURL + 'Images/'

# -----------------------------------------------------
alphabet = " abcdefghijklmnopqrstuvwxyz"

TIMED = 0
if TIMED:
  import time
 
def main():

  dispatch = {
    'html'    : html,
    'xml'     : xml,
    'tex'     : tex,
    'text'    : text,
    }

  def fail(lst):
    print 'Usage: %s <xml-file> <target>' % sys.argv[0]
    print 'where <target> is one of:',
    for k in lst.keys(): print k,
    sys.exit(1)

  if len(sys.argv) < 2:
    fail(dispatch)

  try:
    f = open(sys.argv[1])
  except IOError,e:
    print >> sys.stderr, e
    sys.exit(1)

  if len(sys.argv) > 2:
    target = sys.argv[2]
  else:
    target = 'html'

  if TIMED: start = time.clock()
  quiz = mathquizXml.DocumentTree(f)
  if TIMED: print >> sys.stderr, 'Parse time:',time.clock()-start
  f.close()
  try:
    fn = dispatch[target]
  except KeyError:
    fail(dispatch)
  if TIMED: start = time.clock()
  fn(quiz)
  if TIMED: print >> sys.stderr,'Processing time:', time.clock()-start

# -----------------------------------------------------
# End of main()
# -----------------------------------------------------
def text(doc):
  print doc


# -----------------------------------------------------
#  Visitor classes 
# -----------------------------------------------------
# A visitor class must define the following interface
#
#  forQuiz
#  forQuestion
#  forChoice
#  forAnswer
#  forItem
#
#  mathquizXml.nodeVisitor is an adaptor class with default
#  methods that do nothing except pass on the visitor
#  to their children
#
# -----------------------------------------------------
#  xmlWriter() is a visitor defined in mathquizXml.py
# -----------------------------------------------------
def xml(doc):
  doc.accept(mathquizXml.xmlWriter())
# -----------------------------------------------------
#  TeX visitor
# -----------------------------------------------------
def tex(doc):
  doc.accept(TeXWriter())

class TeXWriter(mathquizXml.nodeVisitor):
  """ This visitor class traverses the document tree
      and writes out the data in the form expected
      by the genquiz.sty style file.
  """

# A lot of this needs improvement.  For example, the
# number of choices per question is hard-wired to 4.
  def forQuiz(self,node):
    print '\\input genquiz.sty'
    print '\\def\\quizid{xxxxx}'
    print '\\def\\infoline{%s}' % node.title
    print '\\RecordAnswers'
    print '\\quiztop{%d}{4}' % len(node.questionList)
    print '\\signaturebox'
    print '\\vskip\\quizskip'
    print 'You may use the space below for your own work.'
    print '\\newpage'
    node.broadcast(self)
    print '\\bye'

  def forQuestion(self,node):
    print '\n\\exercise'
    print strval(node.question)
    node.broadcast(self)

  def forChoice(self,node):
    print '\\beginparts'
    node.broadcast(self)
    print '\\endparts'

  def forAnswer(self,node):
    print '\\fbox{\\hbox to 1cm{\strut\\hfil}}'

  def forItem(self,node):
    if node.expect == 'true':
      tag = '\\correct'
    else:
      tag = ''
    print '\\part %s%s' % (strval(node.answer),tag)
    if node.response:
      print '[%s]' % strval(node.response)


# -----------------------------------------------------
# Conversion routines: XML to DHTML
# -----------------------------------------------------
NoScript = """If you are reading this message either your
  browser does not support JavaScript or else JavaScript
  is not enabled.  You will need to enable JavaScript and
  then reload this page before you can use this quiz."""

CSStop = """<style type="text/css">
<!--
    span.nav { font-size: 90%; color: #999999 }
    th a.tha { text-decoration: none; color: #ffffcc;}
    th a:hover.tha { text-decoration: underline; color: #ffffcc;}
    th a:visited.tha { color: #ffffcc;}
    div.footer a:hover.global { text-decoration: underline;}
    td a:hover.global { text-decoration: underline;}

    #quiz tr { vertical-align: top; }

    #copy {
	font-family: sans-serif, verdana, helvetica;
	font-size: 60%; 
    }
    #copy A{
	text-decoration: none;
    }
    .QuizList { color: #3333AC; font-family: sans-serif, verdana, helvetica; font-weight: bold; text-decoration: none; text-align: left; }
    li.QuizList { list-style-image: url('"""+Images+"""arrow.gif'); }
    li.QuizList:hover { list-style-image: url('"""+Images+"""red_arrow.gif'); background-color: #FFFCF0; text-decoration: none; }
    .brown    { color: #cc3300; }
    .red      { color: red; }
    .QText    { text-align: left; }
    .RText    { color: black; text-align: left; }
    .QChoices { text-align: left; }
    span.ArrowQuestion img {text-align: top;}
    span.ArrowQuestion {color: #993333; font-size: 15px;line-height: 41px; background-color: #FFF3D9;}""" 

Qgeometry = """    {
      top: 160px;
      left: 180px;
      z-index: 0;
      position: absolute; 
      margin: -10px 0px 0px 0px;
      padding: 5px 0px 0px 0px;"""

Rgeometry = """    {
      position: absolute;
      top:  10px;
      left: 0px;
      padding: 5px;
      border: solid black 2px;
      visibility: hidden;
    }"""

QuizColour = ["purple","darkred","darkblue","darkgreen"]

# Document tree structure

#   doc.title
#      .questionList[].question
#                     .answer.type               (Choice)
#                            .itemList[].expect
#                                       .answer
#                                       .response 
#                     .answer.tag                (Answer)
#                            .whenTrue
#                            .whenFalse

def html(doc):
  """ Converts the document tree to HTML
  """
  print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"'
  print '    "http://www.w3.org/TR/html401/loose.dtd">'
  print '<html>\n<head>'
  # fudge, and hope to fix below!
  for attr in doc.metaList:
    s = '<meta'
    for k in attr.keys():
      s += ' %s="%s"' % (k, attr[k])
    s += '/>'
    print s
  for attr in doc.linkList:
    s = '<link'
    for k in attr.keys():
      s += ' %s="%s"' % (k, attr[k])
    s += '/>'
    print s
  print '<title>%s</title>' % doc.title

  course=doc.course[0]
  if course['code']=="MathQuiz":
    level = 'MOW'
    year  = 'GEM'
  elif len(course['code'])>4:
    level={'1':'JM', '2':'IM', '3':'SM', 'o':'', 'Q':''}[course['code'][4]]
    year ={'JM':'Junior', 'IM':'Intermediate', 'SM':'Senior', '':''}[level]
    level='UG/'+level
  else:
    level=''
    year=''

  print """  <meta name="organization" content="School of Mathematics and Statistics, University of Sydney">
  <meta name="Copyright" content="University of Sydney 2004"> 
  <meta name="GENERATOR" content="%s"> 
  <meta name="AUTHORS" content="Andrew Mathas and Don Taylor">
  <!--
  By reading through this file you should be able to extract the
  answers to the quiz; however, you will get more out of the quiz if
  you do the questions yourself. Of course, you are free to read the
  source if you wish.
  -->""" % VERSION
  qTotal = len(doc.questionList)
  if len(doc.discussionList)==0:
    currentQ='1'
  else:
    currentQ='-1     // start showing discussion'
  mathquizConfig.printInitialization(doc.src,course,currentQ,qTotal,level)

  # Automatically generated css specifying the quiz page
  print CSStop
  if len(doc.quizList)>0:       # index listing
    print '    #question-0'
    print Qgeometry
    print '    visibility: visible;\n    }'
      
  dnum=0
  for d in doc.discussionList:  # discussion
    dnum+=1
    print '    #question-%d' % dnum
    print Qgeometry
    if dnum==1:
      print '      visibility: visible;\n    }'
    else:
      print '      visibility: hidden;\n    }'

  qnum = 0
  for q in doc.questionList:     # questions
    qnum += 1
    print '\n    #question%d %s' % (qnum, Qgeometry)
    if len(doc.discussionList)==0 and qnum==1:
      print '      visibility: visible;'
    else:
      print '      visibility: hidden;'
#    print '      color: %s;' % QuizColour[qnum % len(QuizColour)]
    print '    }'
    print '\n    #answer%d' % qnum
    print '    {'
    print '      position: relative;'
    print '      visibility: visible;'
    print '      width: 100%;'
    print '    }'
    if isinstance(q.answer,mathquizXml.Choice):
      if q.answer.type == "multiple":
        print '\n    #q%dresponse0' % qnum
        print Rgeometry
      rnum = 0
      for s in q.answer.itemList:
        rnum += 1
        print '\n    #q%dresponse%d' % (qnum,rnum)
        print Rgeometry
    else:
      print '\n    #q%dtrue' % qnum
      print Rgeometry
      print '\n    #q%dfalse' % qnum
      print Rgeometry
  print '-->\n</style>'

  # print the javascript variables holding the quiz solutions and responses
  setPatterns(doc.questionList, doc.discussionList)

  print '</head>'
  print """<body bgcolor="#ffffff" background="" text="#000000" 
                 style="margin: 0px;">""" 
  print '<noscript>%s</noscript>' % NoScript

  # print the top of the table (using local configuration)
  mathquizConfig.printTableTop(doc, level, year, course)

  triangle="""  <tr valign="top">
      <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
        height="9">&nbsp;</td>"""

  space=   """    <tr>  <td height="5" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" 
           height="1" alt="" vspace="5" class="decor"></td>
   </tr>"""

  thinline="""  <tr valign="top" bgcolor="#EFE9C2">
         <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" 
           alt="" class="decor"></td>
   </tr>"""

  if len(course['name'])>0:
    # button for question numbers and meaning of symbols
    if len(doc.quizList)==0:
      if  doc.src=="mathquiz-manual":
        print """<ul class="navmenu">
    <li class="navmenu" style="list-style-image: none; list-style: none;">
      <div class="selspacing"><div class="dropdownroot" id="QSubmenu"></div></div>
      <script type="text/javascript"> domMenu_activate('QSubmenu'); </script>
    </li>
    <li class="navselected" style="list-style-image: none; list-style: none;">
       <div class="navselected">MathQuiz</div>
    </li>
  </ul>
"""
      else:
        print """<ul class="navmenu">
    <li class="navselectedsub" style="list-style-image: none; list-style: none;">
      <div class="selspacing"><div class="dropdownroot" id="CourseQSubmenu"></div></div>
      <script type="text/javascript"> domMenu_activate('CourseQSubmenu'); </script>
    </li>
  </ul>
"""
    else:
      mathquizConfig.printIndexSideMenu()

  print """<table width="160" border="0" cellspacing="0" cellpadding="0" class="nav">"""
  if len(doc.discussionList)>0:
    # links for discussion items
    dnum=0
    for d in doc.discussionList:
      dnum+=1
      print """<tr valign="top">
  <td class="navselectedsub"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt=""></td>
  <td width="5" class="navselectedsub">
     <img src=\""""+Images+"""bullet.gif" width="6" height="9" alt="" hspace="3" vspace="3">
  </td>
  <td width="100%%" class="navselectedsub">
     <a class="nav" href="javascript:void(0);" 
        onMouseOver="window.status=\'%s\'; return true;"
        onMouseOut="window.status=\'\'; return true;"
        onClick="return gotoQuestion(-%d);">
          %s
     </a>
  </td>""" % (d.heading, dnum, d.heading)
    print space
    print thinline
    print space

  if len(doc.questionList)>0:
    print """  <tr valign="top">
      <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9" height="9" style="padding-top: 8px">&nbsp;</td>
      <td colspan="2" class="headerright" style="padding-top: 8px"><B>Questions</B></td>
  </tr>"""
    print space
    print """  <tr valign="top">
     <td class="navselectedsub"><img src=\""""+Images+"""bpixel.gif" width="1" height="1" alt=""></td>
     <td class="navselectedsub" colspan="2">
     <a HREF="javascript:void(0);" onMouseOver="window.status=\'Question 1\';return true;"
        onClick="return gotoQuestion(1);">"""
    if len(doc.discussionList)==0:
      firstimage='%sborder1.gif' % Images
    else:
      firstimage='%sclear1.gif' % Images
    print '  <img alt="" src="%s" name="progress1" align="TOP"' % firstimage
    print '       height="31"width="31" border="0" hspace="2" vspace="2"></a>'
    for i in range(2,qTotal+1):
      if i % 2 == 1:
        print '<br>'
      print '<a HREF="javascript:void(0);" onClick="return gotoQuestion(%d);"' % i
      print '   OnMouseOver="window.status=\'Question %d\';return true;">' % i
      print '<img alt="" src="%sclear%d.gif" name="progress%d" align="TOP" height="31" width="31" border="0" hspace="2" vspace="2"></a>' % (Images,i,i)

    print '                 </td></tr>'
    print space
    imgTag = '    <tr>  <td class="nav"></td><td class="nav" colspan="2"><img alt="" src="'+Images+'%s.gif" align="%s" height="%d" width="%d" border="0" hspace="2" vspace="2">'
    print imgTag % ('star',"MIDDLE",12,12)
    print 'right first<br>&nbsp;&nbsp;&nbsp;&nbsp;attempt</td></tr>'
    print space
    print imgTag % ('tick',"MIDDLE",18,14)
    print 'right</td></tr>'
    print space
    print imgTag % ('cross',"MIDDLE",9,10)
    print 'wrong</td></tr>'
    print space
    print thinline
  # end of progress buttons

  print """  </tbody></table>
  <div align="center" ID="copy" style="width: 100%%; padding:20px 0px 20px 0px; margin: 0px;">
    <a href="/u/MOW/MathQuiz/doc/credits.html"
       onMouseOver="window.status='%s'; return true">
       <font face="3DArial, ArialBlack" color="yellow"><B>%s</B></font></a><br>
         <a href="http://www.usyd.edu.au"
            onMouseOver="window.status='University of Sydney'; return true">
            <font color="white">University of Sydney</font>
	 </a><br>
	   <a href="http://www.maths.usyd.edu.au"
              onMouseOver="window.status='School of Mathematics and Statistics'; return true">
         <font color="#CCFFFF">School of Mathematics<br> and Statistics</font>
           </a>
	<br>
	&copy; Copyright 2004-2006
  </div>
  <!-- end of side menu -->""" % ( VERSION, VERSION )
  print """</td>
   <td class="nav"><img src=\""""+Images+"""navy.gif" alt="" width="2"></td>
   <td valign="top" width="100%" class="content" id="content">
     <!-- start of main page -->"""

  print """<h1 style="padding: 15px 0px 0px 18px; margin: 5px 0px 7px 0px;">
    %s</h1>""" % doc.title

  if len(doc.questionList)>0:
      print   """<div style="position: relative; z-index: 100; float:right; padding: 0px 10px 0px 0px;">
    <span class="ArrowQuestion">
    <a onmouseover="return navOver('prevpage','Last unanswered question');" 
       onmouseout="return navOut('prevpage');" onclick="NextQuestion(-1);" 
       title="Last unanswered question">
     <img src=\""""+Images+"""n-prevpage.gif" alt="Last unanswered question"
          name="prevpage" id="prevpage" align="middle" border="0" height="15"
          hspace="0" width="32">
   </a> &nbsp;Question&nbsp;
   <a onmouseover="return navOver('nextpage','Next unanswered question');" 
      onmouseout="return navOut('nextpage');" onclick="NextQuestion(1);" 
      title="Next unanswered question">
     <img src=\""""+Images+"""n-nextpage.gif" alt="Next unanswered question"
          name="nextpage" id="nextpage" align="middle" border="0" height="15"
          hspace="0" width="32">
   </a>
   </span>
  </div>"""

  # now print the main page text
  if len(doc.quizList)>0:
    print '<div ID="question-0" style="width=80%;">'
    printHeading( course['name'] + ' Quizzes' )
    print "<ul>"
    qnum=0
    quizmenu=open('quiztitles.js','w')
    quizmenu.write("var QuizTitles = [\n")
    for q in doc.quizList:
      qnum+=1
      print """<li class="QuizList"><a href="%s" onMouseOver="window.status='%s'; return true" onMouseOut="window.status=''; return true">
  %s
</a></li>""" % (q['url'], q['title'], q['title'])
      quizmenu.write("  ['%s','%sQuizzes/%s']" %(q['title'],course['url'],q['url']))
      if qnum<len(doc.quizList):
	quizmenu.write(",\n");
      else:
	quizmenu.write("\n");


    print '</ul>\n</div>'
    quizmenu.write("];\n");
    quizmenu.close();

  # discussion(s) masquerade as negative questions
  if len(doc.discussionList)>0:
    dnum = 0
    for d in doc.discussionList:
      dnum+=1
      print '\n<div ID="question-%d" style="width:80%%;">' % dnum
      printHeading(d.heading)
      print '%s\n<p><br>\n' % strval(d.discussion)
      if len(doc.questionList)>0 and dnum==len(doc.discussionList):
        print '<input TYPE="button" NAME="next" VALUE="Start quiz"\n'
        print '       onClick="return gotoQuestion(1);">'
      print '</div>'

  if len(doc.questionList)>0:
    qnum = 0
    for q in doc.questionList:
      qnum += 1
      print '\n<div ID="question%d" style="width:80%%;">' % qnum
      printQuestion(q,qnum)
      printResponse(q,qnum)
      print '</div>'

  print """
  </table>
</body>
</html>"""

def setPatterns(questionList, discussionList):
  print '<script language="javascript" type="text/javascript">\n<!--'
  i = 0
  for q in questionList:
    print '  QList[%d] = new Array()' % i
    a = q.answer
    if isinstance(a,mathquizXml.Answer):
      print '  QList[%d].value = "%s"' % (i,a.value)
      print '  QList[%d].type = "input"' % i
    else:
      print '  QList[%d].type = "%s"' % (i,a.type)
      j = 0
      for s in a.itemList:
        print '  QList[%d][%d] = %s' % (i,j,s.expect)
        j += 1
    i += 1
  print '// -->\n</script>'
    
def printHeading(title):
  print """<div class="superspcr">&nbsp;</div>
       <div class="subheader">
         <div style="background-image: url("""+Images+"""wt.gif); background-position: right top; background-repeat: no-repeat;">"""
  print """    <h2>%s</h2>
         </div>
         <div class="subline">&nbsp;</div>
       </div>
       <div class="subspcr">&nbsp;</div>""" % title

def printQuestion(Q,n):
  printHeading( 'Question %d' % n )
  print '<div class="QText">'
  print strval(Q.question) 
  print '</div>'
  print '<form name="Q%dForm" action="" onSubmit="return false;">' % n
  snum = 0
  if isinstance(Q.answer,mathquizXml.Answer):
    print '<p><input TYPE="text"  onChange="checkAnswer();" SIZE="5">'
    if Q.answer.tag:
      print '<span class="QText"> ' + Q.answer.tag +'</span>'
  else:
    print '<table summary="List of question choices" cellspacing="4" cellpadding="4" width="100%">'
    print '<col width="2"><col width="2"><col width="*">'
    # print extra column specifications as necessary
    for c in range(1,Q.answer.cols):
      print '<col width="10"><col width="2"><col width="2"><col width="*">'
    for s in Q.answer.itemList:
      snum += 1
      printItem(s, n, snum)
    if s.parent.type=='single':  # no default answer for question
      print '<tr>  <td colspan=2><input type="hidden" checked'
      print '               name="Q%dhidden"></td></tr>' % n
    print '</table>'
  print '<p>'
  print '<input TYPE="button" VALUE="Check Answer" NAME="answer" onClick="checkAnswer();">'
  print '<span style="width:40px;">&nbsp;</span>'
  print '<input TYPE="button" VALUE="Next Question" NAME="next" onClick="nextQuestion(1);">'
  print '</form>'

def strval(ustr):
  if type(ustr) == type(u''):
    str = ''
    for c in ustr:
      str += chr(ord(c))
  else:
    str = ustr
  return str

def printItem(S,q,n):
  if S.parent.cols==1 or (n % S.parent.cols)==1: 
    print '<tr valign="top">'
  else: 
    print '  <td>&nbsp;</td>'
  print '      <td class="brown">%s)</td>' % alphabet[n]
  if S.parent.type == 'single':
    print '      <td><input TYPE="radio" NAME="Q%doptions"></td>' % q
    print '      <td><span class="QChoices">%s</span></td>' % strval(S.answer)
  elif S.parent.type == 'multiple':
    print '      <td><input TYPE="checkbox" NAME="Q%doptions%d"></td>' % (q,n)
    print '      <td><span class="QChoices">%s</span></td>' % strval(S.answer)
  else:
    print '<!-- internal error: %s -->' % S.parent.type
    print >> sys.stderr, 'Unknown question type encountered:',S.parent.type
  if (n % S.parent.cols)==0 or n==len(S.parent.itemList): print '</tr>'


def printResponse(Q,n):
  snum = 0
  print '\n<div ID="answer%d">' % n
  if isinstance(Q.answer,mathquizXml.Answer):
    s = Q.answer
    print '\n<div ID="q%dtrue">' % n
    print '<B>Your answer is correct</B><br>'
    if s.whenTrue:
      print '<div class="RText">%s</div>' % strval(s.whenTrue)
    print '</div>'
    print '\n<div ID="q%dfalse">' % n
    print '<B>Not correct. You may try again.</B>'
    if s.whenFalse:
      print '<div class="RText">%s</div>' % strval(s.whenFalse)
    print '</div>'
  elif Q.answer.type == "single":
    for s in Q.answer.itemList:
      snum += 1
      print '\n<div ID="q%dresponse%d">' % (n,snum)
      print '<B>'
      if s.expect == "true":
        print 'Your answer is correct.<br>'
      else:
        print 'Not correct. Choice <span class="brown">(%s)</span>' % alphabet[snum]
	print 'is <span class="red">%s</span>.' % s.expect
      print '</B>'
      if s.response:
        print '<div class="RText">%s</div>' % strval(s.response)
      print '</div>'
  else: # Q.answer.type == "multiple":
    for s in Q.answer.itemList:
      snum += 1
      print '\n<div ID="q%dresponse%d">' % (n,snum)
      print '<B>There is at least one mistake.</B><br>'
      print 'For example, choice <span class="brown">(%s)</span>' % alphabet[snum]
      print 'should be <span class="red">%s</span>.' % s.expect
      if s.response:
        print '<div class="RText">%s</div>' % strval(s.response)
      print '</div>'
    print '\n<div ID="q%dresponse0">' % n
    print '<B>Your answers are correct</B>'
    print '<ol type="a">'
    for s in Q.answer.itemList:
      print '<li class="brown"><div class="RText"><b>%s</b>. %s</div>' % (strval(s.expect.capitalize()),strval(s.response))
    print '</ol>'
    print '</div>'
  print '</div>'

# =====================================================
if __name__ == '__main__':
  main()

