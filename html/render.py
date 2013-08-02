#!/usr/bin/env python
"""Helper to facilitate the process of rendering the markdown documentation into html,
using pandoc (http://johnmacfarlane.net/pandoc/)."""

import os
import re
import subprocess
import codecs

RE_DEMO_MD = re.compile(r'^demo_.*')
RE_SIMPLE_MD = re.compile(r'\.md')
RE_INHTML_MDREF = re.compile(r'\.md(\#|\")')
RE_GREP_MD = re.compile(r'([a-zA-Z0-9\_\/\ \[\]]+).md$')

def convertMdToHtml():
    "Walk the .. directory and convert its *.md files into html, using pandoc."
    lOutputDir = os.getcwd()
    def onWalk(pArg, pDir, pFileNames):
        if -1 != pDir.find("deprecated"):
            return
        lFileNames = pFileNames
        lFileNames.sort()
        if lFileNames.count("intro.md") > 0: # Force 'intro' at the beginning of the toc.
            lFileNames.remove("intro.md")
            lFileNames.insert(0, "intro.md")
        for iFN in lFileNames:
            lM = RE_GREP_MD.match(iFN)
            if not lM:
                continue
            lInputFN = "%s/%s" % (pDir, iFN)
            print ("processing %s" % lInputFN)

            # Invoke pandoc and save the output to a tmp file.
            lP = subprocess.Popen(["pandoc", "--from=markdown", "--to=html", lInputFN], shell=False, stdout=subprocess.PIPE)
            lOut = lP.communicate()[0]
            lTmpOutputFN = "%s/%s.tmp" % (lOutputDir, lM.group(1))
            lTmpOutputF = open(lTmpOutputFN, "wb+")
            lTmpOutputF.write(lOut)
            lTmpOutputF.close()

            # Convert any .md reference in the html, to a .html reference.
            # Insert a header for navigation, styles, smart links to console etc.
            # Note: Those js and css are found under server/src/www/doc, which is the main destination for the rendererd html at the moment.
            lTmpOutputF = codecs.open(lTmpOutputFN, "r", "utf-8", 'replace')
            lOutputFN = "%s/%s.html" % (lOutputDir, lM.group(1))
            lOutputF = codecs.open(lOutputFN, "w+", "utf-8", 'replace')

            lInsertedHeader = [ \
                "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n", \
                "<head>\n", \
                "  <meta name='viewport' content='width=device-width, initial-scale=1.0' />\n", \
                "  <script src='js/jquery.js' type='text/javascript'></script>\n", \
                "  <script src='js/snippets_to_console.js' type='text/javascript'></script>\n", \
                "  <link href='css/afydoc.css' rel='stylesheet' type='text/css' media='screen and (min-device-width: 600px)' />\n", \
                "  <link href='../m/doc/css/afydoc.css' rel='stylesheet' type='text/css' media='screen and (max-device-width: 599px)' />\n", \
                "  <meta http-equiv='content-type' content='text/html; charset=utf-8'></meta>\n", \
                "</head>\n", \
                "<div id='width_constraint' class='horizontally_centered'>\n", \
                "<div id='generic_header'>\n", \
                "<img src='images/logo_small.png' id='gh_logo_img'></img>\n", \
                "<div id='afytocbar'>\n", \
                "  <select id='afytoclist'>\n" ]
            lAppendAfter = []
            for _iFN in lFileNames:
                _lM = RE_GREP_MD.match(_iFN)
                if not _lM:
                    continue
                _lN = RE_SIMPLE_MD.sub("", _iFN)
                _lOption = "    <option value='%s'%s>%s</option>\n" % (_lN, ("", " SELECTED")[_iFN == iFN], _lN)
                if RE_DEMO_MD.match(_iFN):
                    lAppendAfter.append(_lOption)
                    continue
                lInsertedHeader.append(_lOption)
            for _iOpt in lAppendAfter:
              lInsertedHeader.append(_iOpt)
            lInsertedHeader.append("  </select>\n")
            lInsertedHeader.append("</div>\n") # afytocbar
            lInsertedHeader.append("</div>\n") # generic_header
            lOutputF.writelines(lInsertedHeader)

            def replaceMdref(mo):
                return ".html%s" % mo.group(1)
            for iLine in lTmpOutputF:
                lOutputF.writelines([RE_INHTML_MDREF.sub(replaceMdref, iLine)])
            lOutputF.writelines(["</div>\n"])

            lTmpOutputF.close()
            lOutputF.close()
            os.remove(lTmpOutputFN)
    lPaths = os.walk("%s/.." % lOutputDir)
    for iP in lPaths:
        onWalk(None, iP[0], iP[2])

convertMdToHtml()
