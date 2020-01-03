import mysql.connector

db = mysql.connector.connect(
	host = 'localhost',
	user = 'ashley',
	passwd = 'primer_database',
	use_pure = True,
	database = 'primer_database'
)

mycursor = db.cursor()

mycursor.execute('CREATE TABLE analysis_type (analysis_type_id INT PRIMARY KEY NOT NULL, analysis_type VARCHAR(50) NOT NULL)')

mycursor.execute('CREATE TABLE gene (gene_id INT PRIMARY KEY NOT NULL, gene_name VARCHAR(50) NOT NULL, chromosome VARCHAR(5))')

mycursor.execute('CREATE TABLE primer_set (primer_set_id INT PRIMARY KEY NOT NULL, primer_set VARCHAR(10) NOT NULL)')

mycursor.execute('CREATE TABLE imported_by (imported_by_id INT PRIMARY KEY NOT NULL, imported_by VARCHAR(30) NOT NULL)')

mycursor.execute('CREATE TABLE amplicon (amplicon_id INT PRIMARY KEY NOT NULL, amplicon_name VARCHAR(100) NOT NULL, exon VARCHAR(20), comments VARCHAR(1000), genomic_location_start INT, genomic_location_end INT, gene_id INT, analysis_type_id INT, primer_set_id INT, FOREIGN KEY (gene_id) REFERENCES gene(gene_id), FOREIGN KEY (analysis_type_id) REFERENCES analysis_type(analysis_type_id), FOREIGN KEY (primer_set_id) REFERENCES primer_set(primer_set_id))')

mycursor.execute('CREATE TABLE primer (primer_id INT PRIMARY KEY NOT NULL, sequence VARCHAR(100) NOT NULL, location VARCHAR(50), direction VARCHAR(5), alt_name VARCHAR(255), ngs_audit_number INT, imported_by_id INT, date_imported VARCHAR(20), amplicon_id INT, FOREIGN KEY (amplicon_id) REFERENCES amplicon(amplicon_id), FOREIGN KEY (imported_by_id) REFERENCES imported_by(imported_by_id))')











