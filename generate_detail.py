import json, sys, os, glob
sys.path.append(".")
import utils
cols = {}
def make(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric):
    basehtml = """
<html>
</html>"""
    open(filename, "w").write(basehtml)
if __name__ == "__main__":
    make("detail.html", "", "", "", "", "");

