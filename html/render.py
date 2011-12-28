#!/usr/bin/env python
"""Helper to facilitate the process of rendering the markdown documentation into html,
using pandoc (http://johnmacfarlane.net/pandoc/)."""

import os
import re
import subprocess

RE_SIMPLE_MD = re.compile(r'\.md')
RE_INHTML_MDREF = re.compile(r'\.md(\#|\")')
RE_GREP_MD = re.compile(r'([a-zA-Z0-9\_\/\ ]+).md$')

def convertMdToHtml():
    "Walk the .. directory and convert its *.md files into html, using pandoc."
    lOutputDir = os.getcwd()
    def onWalk(pArg, pDir, pFileNames):
        lFileNames = pFileNames
        lFileNames.sort()
        for iFN in lFileNames:
            lM = RE_GREP_MD.match(iFN)
            if not lM:
                continue
            lInputFN = "%s/%s" % (pDir, iFN)
            print "processing %s" % lInputFN

            # Invoke pandoc and save the output to a tmp file.
            lP = subprocess.Popen(["pandoc", "--from=markdown", "--to=html", lInputFN], shell=False, stdout=subprocess.PIPE)
            lOut = lP.communicate()[0]
            lTmpOutputFN = "%s/%s.tmp" % (lOutputDir, lM.group(1))
            lTmpOutputF = open(lTmpOutputFN, "w+")
            lTmpOutputF.writelines(lOut)
            lTmpOutputF.close()

            # Convert any .md reference in the html, to a .html reference.
            # Insert a header for navigation, styles, smart links to console etc.
            # Note: Those js and css are found under server/src/www/doc, which is the main destination for the rendererd html at the moment.
            lTmpOutputF = open(lTmpOutputFN, "r")
            lOutputFN = "%s/%s.html" % (lOutputDir, lM.group(1))
            lOutputF = open(lOutputFN, "w+")
            
            lInsertedHeader = [ \
                "<head>\n", \
                "  <script src='js/jquery.js' type='text/javascript'></script>\n", \
                "  <script src='js/snippets_to_console.js' type='text/javascript'></script>\n", \
                "  <link href='css/mvdoc.css' rel='stylesheet' type='text/css' />\n", \
                "</head>\n", \
                "<div id='mvtocbar'>\n", \
                "  <select id='mvtoclist'>\n" ]
            for _iFN in lFileNames:
                _lM = RE_GREP_MD.match(_iFN)
                if not _lM:
                    continue
                _lN = RE_SIMPLE_MD.sub("", _iFN)
                lInsertedHeader.append("    <option value='%s'%s>%s</option>\n" % (_lN, ("", " SELECTED")[_iFN == iFN], _lN))
            lInsertedHeader.append("  </select>\n")
            lInsertedHeader.append("</div>\n")
            lOutputF.writelines(lInsertedHeader)
            
            def replaceMdref(mo):
                return ".html%s" % mo.group(1)
            for iLine in lTmpOutputF:
                lOutputF.writelines([RE_INHTML_MDREF.sub(replaceMdref, iLine)])

            lTmpOutputF.close()
            lOutputF.close()
            os.remove(lTmpOutputFN)
    os.path.walk("%s/.." % lOutputDir, onWalk, None)

convertMdToHtml()
