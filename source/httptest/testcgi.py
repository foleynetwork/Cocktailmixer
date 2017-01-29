#!/usr/bin/env python
import cgi
import Zutat
print "Content-type:text/html\r\n\r\n"


form = cgi.FieldStorage()
 
val1 = form.getvalue('first')
val2 = form.getvalue('last')
x = Zutat.CocktailMaschine() 
print """
<html><head><title>Test URL Encoding</title></head><body>
Hello my name is %s %s
</body></html>""" % (val1, val2)
