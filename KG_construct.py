from KG_extractor import KG_extractor
from PyPDF2 import PdfReader
import urllib
import re
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession


class KG_construct(KG_extractor):
	def __init__(self,spark):
		KG_extractor.__init__(self)
		self.spark = spark
		self.spark = SparkSession.builder.enableHiveSupport().getOrCreate()
		self.spark.sql("CREATE DATABASE IF NOT EXISTS graph_database")

	def extract_table(self):
		df = self.spark.read.table("graph_database.triple_relation")
		return df

	def drop_table(self):
		self.spark.sql("drop table graph_database.triple_relation")

	def download_pdf(self, url, filepath):
		response = urllib.request.urlopen(url)
		pdf_document = response.read()
		#name = string(pdf_document[0:15])
		self.curr_pdf_path = filepath + '/' + '1pdf.pdf'# + name + '.pdf'
		file = open(self.curr_pdf_path, "wb")
		file.write(pdf_document)
		file.close()

	def convert_conversation(self, user_id, text):
		self.text = text
		self.user_id = user_id
		self.core()

	def convert_pdf(self):
		self.read_pdf(self.curr_pdf_path)
		self.core()

	def core(self):
		#self.read_pdf(self.curr_pdf_path)
		self.text_clean()
		self.sentence_divider()
		valid_sentence = 1
		self.total_valid_sentence = 0
		for l in range(len(self.sentences)):
			self.construct_triples(self.sentences[l])
			if self.sentence_structure['prefix'] == []:
				valid_sentence = 0
			if self.sentence_structure['suffix'] == []:
				valid_sentence = 0
			if self.sentence_structure['verb_relation'] == []:
				valid_sentence = 0
			if not valid_sentence == 0:
				self.total_valid_sentence += 1
				self.triple_construction(self.sentences[l])
			valid_sentence = 1
			self.purge_sentence_structure()


	def read_pdf(self, filepath):
		self.reader = PdfReader(filepath)
		page_num = self.reader.numPages
		self.text = '.'
		for i in range(page_num):
			page = self.reader.pages[i]
			self.text += page.extract_text() + '.'
			#self.text_origin = self.text

	def text_clean(self):
		self.text = self.text.replace("\n", " ")
		self.text = self.text.replace("\x03", ".")

	def import_text(self, text):
		self.text = text

	def convert_to_text(self,list_text):
		l = []
		for x in list_text:
			l = l + x
		m_string = ''
		for x in l:
			m_string += ' ' + str(x)
		m_string_ = ''
		for x in m_string:
			m_string_ += str.lower(x)

		return m_string_


	def triple_construction(self,texts):
		#data = request.get_json() # get the json from the post request object

		user_id = self.user_id
		source  = self.sentence_structure['prefix']
		source = self.convert_to_text(source)
		self.check_source = source
		#source = data['source']
		relation = self.sentence_structure['verb_relation']
		relation = self.convert_to_text(relation)
		self.check_relation = relation
		#relation_user = data['relationuser']
		target = self.sentence_structure['suffix']
		target = self.convert_to_text(target)
		self.check_target = target
		#id_ = data['id']
		#time = data['time']
		columns = ["user_id","source","relation","target"]
		data = [(user_id,source,relation,target)]
		df_temp = self.spark.sparkContext.parallelize(data).toDF(columns)
		tables = self.spark.catalog.listTables("graph_database")
		if "triple_relation" in [table.name for table in tables]:
			df_temp.write.mode('append').saveAsTable("graph_database.triple_relation")
		else:
			df_temp.write.mode('overwrite').saveAsTable("graph_database.triple_relation")


	def sentence_divider(self):
		"""
		generate each individual sentence from paragraph
		"""
		self.sentences = [x for x in re.split("[//.|//!|//?|\n]", self.text) if x!=""]





