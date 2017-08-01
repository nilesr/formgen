import sys, os, subprocess, copy
import generate_table
import generate_detail
import generate_index
import generate_graph
import generate_tabs
class helper():
	def __init__(self):
		self.filanames = []
		self.queue = []
		self.translations = {}
		self.static_files = [];
	def make_table(self, filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric):
		self.queue.append(["table", filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric])
	def make_detail(self, filename, customHtml, customCss, customJsOl, customJsGeneric):
		self.queue.append(["detail", filename, customHtml, customCss, customJsOl, customJsGeneric])
	def make_index(self, filename, customJs, customCss):
		self.queue.append(["index", filename, customJs, customCss])
	def make_graph(self, filename, customCss, customJs):
		self.queue.append(["graph", filename, customCss, customJs])
	def make_tabs(self, filename, customJs, customCss):
		self.queue.append(["tabs", filename, customJs, customCss])
	def _make(self, utils, filenames):
		for q in self.queue:
			if q[0] == "detail":
				generate_detail.make(utils, *(q[1:]))
			elif q[0] == "table":
				generate_table.make(utils, *(q[1:]))
			elif q[0] == "index":
				generate_index.make(utils, *(q[1:]))
			elif q[0] == "graph":
				generate_graph.make(utils, *(q[1:]))
			elif q[0] == "tabs":
				generate_tabs.make(utils, *(q[1:]))
			else:
				print("Bad type in queue " + q[0]);
				sys.exit(0);
			filenames.append(q[1])
		return filenames, self.translations, self.static_files
	def extend(helper, filename, newfilename, newJsOl, newJsGeneric = ""):
		new = copy.deepcopy([x for x in helper.queue if x[1] == filename][0])
		new[1] = newfilename
		new[4] += newJsOl
		new[6] += newJsGeneric
		helper.queue.append(new);

