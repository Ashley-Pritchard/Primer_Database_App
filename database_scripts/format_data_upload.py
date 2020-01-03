import pandas as pd 
import numpy as np
import csv
import sys

df = pd.read_csv('primer_database.csv')
df2 = pd.read_csv('analysis_type.csv')

def gene():
	df_g = df[['Gene', 'Chr']].copy()
	df_g['Gene'] = df_g['Gene'].str.upper()
	df_g = df_g.drop_duplicates(keep='first')
	df_g['gene_id'] = df_g.groupby(['Gene', 'Chr']).ngroup()
	df_g.to_csv('gene.csv', sep=',')
gene()

df3 = pd.read_csv('gene.csv')

def primer_set():
	df_ps = df[['Set']].copy()
	primer_set = []
	for index, row in df_ps.iterrows():
		if 'A' in row[0]:
			primer_set.append('A')
		elif 'B' in row[0]:
			primer_set.append('B')
		elif 'C' in row[0]:
			primer_set.append('C')
		else:
			primer_set.append('Other')
	df_ps['primer_set'] = primer_set
	df_ps = df_ps.drop(columns = ['Set'])
	df_ps = df_ps.drop_duplicates(keep='first')
	df_ps['primer_set_id'] = df_ps.groupby(['primer_set']).ngroup()
	df_ps.to_csv('primer_set.csv', sep=',')
primer_set()

df4 = pd.read_csv('primer_set.csv')

def imported_by():
	df_i = df[['Imported By']].copy()
	df_i = df_i.rename(columns={'Imported By': 'imported_by'})
	df_i['imported_by'] = df_i['imported_by'].str.upper()
	name = []
	for index, row in df_i.iterrows():
		if 'ARIELE' in row[0]:
			name.append('AR')
		elif 'BENITO' in row[0]:
			name.append('BB')
		elif 'CNS' in row[0]:
			name.append('CNS')
		elif 'CAROLINE' in row[0]:
			name.append('CNS')
		elif 'CARL' in row[0]:
			name.append('CF')
		elif 'CLAIRE HODGKISS' in row[0]:
			name.append('CLHS')
		elif 'CONRAD' in row[0]:
			name.append('CS')
		elif 'ELIZABTH WOOD' in row[0]:
			name.apend('EW')
		elif 'ELIZABETH' in row[0]:
			name.append('EW')
		elif 'EMILY' in row[0]:
			name.append('EP')
		elif 'HANNAH BOON' in row[0]:
			name.append('HB')
		elif 'MATTEN' in row[0]:
			name.append('HM')
		elif 'HELEN LORD' in row[0]:
			name.append('HL')
		elif 'JESS GABRIEL' in row[0]:
			name.append('JEG')
		elif 'JESSICA WOODLEY' in row[0]:
			name.append('JW')
		elif 'TAYLOR' in row[0]:
			name.append('JMT')
		elif 'JULIE' in row[0]:
			name.append('J')
		elif 'LIZZIE/MIKEB' in row[0]:
			name.append('EW/MB')
		elif 'BOWMAN' in row[0]:
			name.append('MB')
		elif 'OLDRIDGE' in row[0]:
			name.append('MO')
		elif 'WARE' in row[0]:
			name.append('PW')
		elif 'SARAH REID' in row[0]:
			name.append('SR')
		elif 'BEDENHAM' in row[0]:
			name.append('TB')
		elif 'LESTER' in row[0]:
			name.append('TL')
		elif 'TREENA' in row[0]:
			name.append('TC')
		elif 'LOUISE' in row[0]:
			name.append('LIW')
		else:
			name.append(row[0])
	df_i['imported_by'] = name	
	df_i = df_i.drop_duplicates(keep='first')
	df_i['imported_by_id'] = df_i.groupby(['imported_by']).ngroup()	
	df_i.to_csv('imported_by.csv', sep=',')
imported_by()

df5 = pd.read_csv('imported_by.csv')

def amplicon():
	df_a = df[['Amplicon_ID', 'Fragment', 'Comments', 'Gene', 'Set', 'Genomic Loc 1', 'Genomic Loc 2']].copy()
	df_a = df_a.rename(columns = {'Genomic Loc 1': 'genomic_location_start', 'Genomic Loc 2': 'genomic_location_end', 'Comments': 'comments'})
	df_a['Gene'] = df_a['Gene'].str.upper()
	gene_dict = dict(zip(df3.Gene, df3.gene_id))
	df_a['gene_id'] = df_a['Gene'].map(gene_dict)
	analysis_type = []
	for index, row in df_a.iterrows():
		if 'NGS' in row[4]:
			analysis_type.append('NGS')
		elif 'A' in row[4]:
			analysis_type.append('Sanger')
		elif 'B' in row[4]:
			analysis_type.append('Sanger')
		elif 'C' in row[4]:
			analysis_type.append('Sanger')
		else:
			analysis_type.append('Other')
	df_a['analysis_type'] = analysis_type
	analysis_type_dict = dict(zip(df2.analysis_type, df2.analysis_type_id))
	df_a['analysis_type_id'] = df_a['analysis_type'].map(analysis_type_dict)
	primer_set = []
	for index, row in df_a.iterrows():
		if 'A' in row[4]:
			primer_set.append('A')
		elif 'B' in row[4]:
			primer_set.append('B')
		elif 'C' in row[4]:
			primer_set.append('C')
		else:
			primer_set.append('Other')
	df_a['primer_set'] = primer_set
	primer_set_dict = dict(zip(df4.primer_set, df4.primer_set_id))
	df_a['primer_set_id'] = df_a['primer_set'].map(primer_set_dict)
	exon = []
	for index, row in df_a.iterrows():
		if row[9] == 0:
			exon.append(None)
		else:
			exon.append(row[1])
	df_a['exon'] = exon
	df_a = df_a.drop(columns = ['Fragment', 'Gene', 'Set', 'analysis_type', 'primer_set'])
	df_a['amplicon_id'] = df.groupby(['Amplicon_ID']).ngroup()
	df_a = df_a.rename(columns={'Amplicon_ID': 'amplicon_name'})
	df_a['genomic_location_start'] = df_a['genomic_location_start'].replace(np.nan, 0)
	df_a['genomic_location_end'] = df_a['genomic_location_end'].replace(np.nan, 0)
	df_a.to_csv('amplicon.csv', sep=',')
amplicon()

df6 = pd.read_csv('amplicon.csv')

def primer(): 
	df_p1 = df[['F', 'F Location', 'Alt Name F', 'Amplicon_ID', 'Date Entered Service/Imported', 'Imported By', 'Fragment', 'Set']].copy()
	df_p1 = df_p1.rename(columns={'F': 'sequence', 'F Location': 'location', 'Alt Name F': 'alt_name', 'Amplicon_ID':'amplicon_name', 'Date Entered Service/Imported': 'date_imported', 'Imported By': 'imported_by'})
	direction_F = 'F'
	df_p1['direction'] = direction_F
	df_p2 = df[['R', 'R Location', 'Alt Name R', 'Amplicon_ID', 'Date Entered Service/Imported', 'Imported By', 'Fragment', 'Set']].copy()
	df_p2 = df_p2.rename(columns={'R': 'sequence', 'R Location': 'location', 'Alt Name R': 'alt_name', 'Amplicon_ID':'amplicon_name', 'Date Entered Service/Imported': 'date_imported', 'Imported By': 'imported_by'})
	direction_R = 'R'
	df_p2['direction'] = direction_R
	df_p3 = pd.concat([df_p1, df_p2])
	df_p3['sequence'] = df_p3['sequence'].replace(' ', np.nan)
	df_p3 = df_p3.dropna(subset=['sequence'])
	amplicon_dict = dict(zip(df6.amplicon_name, df6.amplicon_id))
	df_p3['amplicon_id'] = df_p3['amplicon_name'].map(amplicon_dict)
	df_p3['imported_by'] = df_p3['imported_by'].str.upper()
	name = []
	for index, row in df_p3.iterrows():
		if 'ARIELE' in row[5]:
			name.append('AR')
		elif 'BENITO' in row[5]:
			name.append('BB')
		elif 'CNS' in row[5]:
			name.append('CNS')
		elif 'CAROLINE' in row[5]:
			name.append('CNS')
		elif 'CARL' in row[5]:
			name.append('CF')
		elif 'CLAIRE HODGKISS' in row[5]:
			name.append('CLHS')
		elif 'CONRAD' in row[5]:
			name.append('CS')
		elif 'ELIZABTH WOOD' in row[5]:
			name.apend('EW')
		elif 'ELIZABETH' in row[5]:
			name.append('EW')
		elif 'EMILY' in row[5]:
			name.append('EP')
		elif 'HANNAH BOON' in row[5]:
			name.append('HB')
		elif 'MATTEN' in row[5]:
			name.append('HM')
		elif 'HELEN LORD' in row[5]:
			name.append('HL')
		elif 'JESS GABRIEL' in row[5]:
			name.append('JEG')
		elif 'JESSICA WOODLEY' in row[5]:
			name.append('JW')
		elif 'TAYLOR' in row[5]:
			name.append('JMT')
		elif 'JULIE' in row[5]:
			name.append('J')
		elif 'LIZZIE/MIKEB' in row[5]:
			name.append('EW/MB')
		elif 'BOWMAN' in row[5]:
			name.append('MB')
		elif 'OLDRIDGE' in row[5]:
			name.append('MO')
		elif 'WARE' in row[5]:
			name.append('PW')
		elif 'SARAH REID' in row[5]:
			name.append('SR')
		elif 'BEDENHAM' in row[5]:
			name.append('TB')
		elif 'LESTER' in row[5]:
			name.append('TL')
		elif 'TREENA' in row[5]:
			name.append('TC')
		elif 'LOUISE' in row[5]:
			name.append('LIW')
		else:
			name.append(row[5])
	df_p3['imported_by'] = name
	imported_by_dict = dict(zip(df5.imported_by, df5.imported_by_id))
	df_p3['imported_by_id'] = df_p3['imported_by'].map(imported_by_dict)
	ngs_audit_number = []
	for index, row in df_p3.iterrows():
		if 'NGS' in row[7]:
			ngs_audit_number.append(row[6])
		else:
			ngs_audit_number.append(None)
	df_p3['ngs_audit_number'] = ngs_audit_number	
	df_p3 = df_p3.drop(columns = ['amplicon_name', 'imported_by', 'Fragment', 'Set'])
	df_p3['date_imported'] = df_p3['date_imported'].replace(to_replace = '\.', value = '/', regex=True)
	df_p3['date_imported'] = df_p3['date_imported'].replace(to_replace = '-', value = '/', regex=True)
	df_p3['primer_id'] = df_p3.groupby(['sequence', 'location', 'direction', 'amplicon_id']).ngroup()
	df_p3['sequence'] = df_p3['sequence'].str.upper()
	df_p3['ngs_audit_number'] = df_p3['ngs_audit_number'].replace(np.nan, 0)
	df_p3.to_csv('primer.csv', sep=',')
primer()

df7 = pd.read_csv('primer.csv')



	
