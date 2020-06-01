#Currenly, OMGL primer data is stored in a large excel workbook. This script cleans and reformats this excel data for upload to the new primer datbase, which has been developed as a django web app. The script converts the excel file into 7 seperate csv files for upload into the tables which make up the new primer database. 

#import relevant libraries 
import pandas as pd 
import numpy as np
import csv
import sys

#convert the current excel sheet used for primer storage into a pandas dataframe for downstream reference. 
df = pd.read_csv('primer_database.csv')

#create csv file of all potential analysis types for upload to the 'Analysis_Type' table of the primer database
with open('analysis_type.csv', 'w', newline='') as file:
	writer = csv.writer(file)
	writer.writerow(["analysis_type_id", "analysis_type"])
	writer.writerow([0, "NGS"])
	writer.writerow([1, "Sanger"])
	writer.writerow([3, "MLPA"])
	writer.writerow([4, "Long Range"])
	writer.writerow([5, "Taqman"])
	writer.writerow([6, "RT-PCR"])
	writer.writerow([7, "Pyrosequencing"])
	writer.writerow([8, "ARMS: Mutant"])
	writer.writerow([9, "ARMS: Normal"])
	writer.writerow([10, "Light Scanner"])

#store the analysis type csv as pandas dataframe for downstream reference
df2 = pd.read_csv('analysis_type.csv')

#create the csv file for upload to the 'Gene' table of the database
def gene():

	#copy the relevant fields from the primer database
	df_g = df[['Gene', 'Chr']].copy()

	#convert all gene names to uppercase 
	df_g['Gene'] = df_g['Gene'].str.upper()

	#drop duplicate gene names 
	df_g = df_g.drop_duplicates(keep='first')

	#create a gene_id for each unique record 
	df_g['gene_id'] = df_g.groupby(['Gene', 'Chr']).ngroup()

	#save as csv
	df_g.to_csv('gene.csv', sep=',')

#call function
gene()

#store the gene.csv as a pandas dataframe for downstream reference 
df3 = pd.read_csv('gene.csv')


#create the csv file for upload to the 'Primer_Set' table of the database
def primer_set():

	#copy the relevant fields from the primer database
	df_ps = df[['Set']].copy()

	#create a new primer_set field based on the current field containing A / B / C
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

	#drop the original field 
	df_ps = df_ps.drop(columns = ['Set'])

	#drop duplicate sets names
	df_ps = df_ps.drop_duplicates(keep='first')

	#created a primer_set_id for each unique record 
	df_ps['primer_set_id'] = df_ps.groupby(['primer_set']).ngroup()

	#save as csv
	df_ps.to_csv('primer_set.csv', sep=',')

#call function
primer_set()

#store the primer_set.csv as a pandas dataframe for downstream reference
df4 = pd.read_csv('primer_set.csv')


#create the csv file for upload to the 'Imported_By' table of the database
def imported_by():

	#copy the relevant fields from the primer database
	df_i = df[['Imported By']].copy()

	#rename the column 
	df_i = df_i.rename(columns={'Imported By': 'imported_by'})

	#convert all names to uppercase
	df_i['imported_by'] = df_i['imported_by'].str.upper()

	#replace all names in the field with appropriate full names from lab telephone directory
	name = []
	status = []
	for index, row in df_i.iterrows():
		if 'ARIELE' in row[0]:
			name.append('Ariele Rosseto')
		elif 'BENITO' in row[0]:
			name.append('Benito Banos-Pinero')
		elif 'CNS' in row[0]:
			name.append('Caroline Sarton')
		elif 'CAROLINE' in row[0]:
			name.append('Caroline Sarton')
		elif 'CARL' in row[0]:
			name.append('Carl Fratter')
		elif 'CLAIRE HODGKISS' in row[0]:
			name.append('Claire Hodgkiss')
		elif 'CONRAD' in row[0]:
			name.append('Conrad Smith')
		elif 'ELIZABTH WOOD' in row[0]:
			name.apend('Elizabeth Wood')
		elif 'ELIZABETH' in row[0]:
			name.append('Elizabeth Wood')
		elif 'EMILY' in row[0]:
			name.append('Emily Packham')
		elif 'HANNAH BOON' in row[0]:
			name.append('Hannah Boon')
		elif 'MATTEN' in row[0]:
			name.append('Hannah Matten')
		elif 'HELEN LORD' in row[0]:
			name.append('Helen Lord')
		elif 'JESS GABRIEL' in row[0]:
			name.append('Jess Gabriel')
		elif 'JESSICA WOODLEY' in row[0]:
			name.append('Jessica Woodley')
		elif 'TAYLOR' in row[0]:
			name.append('John Taylor')
		elif 'JULIE' in row[0]:
			name.append('Julie')
		elif 'LIZZIE/MIKEB' in row[0]:
			name.append('Michael Bowman')
		elif 'BOWMAN' in row[0]:
			name.append('Michael Bowman')
		elif 'OLDRIDGE' in row[0]:
			name.append('Michael Oldridge')
		elif 'WARE' in row[0]:
			name.append('Pauline Ware')
		elif 'SARAH REID' in row[0]:
			name.append('Sarah Reid')
		elif 'BEDENHAM' in row[0]:
			name.append('Tina Bedenham')
		elif 'LESTER' in row[0]:
			name.append('Tracy Lester')
		elif 'TREENA' in row[0]:
			name.append('Treena Cranston')
		elif 'LOUISE' in row[0]:
			name.append('Louise Williams')
		else:
			name.append(row[0])
	df_i['imported_by'] = name	
	
	#add the status of the lab members 
	status = []
	for index, row in df_i.iterrows():
		if row[0] == 'Ariele Rosseto' or 'Elizabeth Wood' or 'Emily Packham' or 'Hannah Matten' or 'Jessica Woodley' or 'Julie' or 'Pauline Ware' or 'Sarah Reid':
			status.append('ex')
		else:
			status.append('current')
	df_i['status'] = status

	#drop duplicate names
	df_i = df_i.drop_duplicates(keep='first') 

	#created an imported_by_id for each unique record 
	df_i['imported_by_id'] = df_i.groupby(['imported_by']).ngroup()	

	#save as csv
	df_i.to_csv('imported_by.csv', sep=',')

#call function
imported_by()

#store the imported_by.csv as a pandas dataframe for downstream reference
df5 = pd.read_csv('imported_by.csv')


#create the csv file for upload to the 'Amplicon' table of the database
def amplicon():

	#copy the relevant fields from the primer database
	df_a = df[['Amplicon_ID', 'Fragment', 'Gene', 'Set']].copy()

	#convert gene names to uppercase
	df_a['Gene'] = df_a['Gene'].str.upper()

	#create a dictionary to pull the appropriate gene id for each record from the gene.csv file. Store these as a new column
	gene_dict = dict(zip(df3.Gene, df3.gene_id))
	df_a['gene_id'] = df_a['Gene'].map(gene_dict)

	#create a new analysis_type field based on the current field containing either NGS / A / B / C
	analysis_type = []
	for index, row in df_a.iterrows():
		if 'NGS' in row[3]:
			analysis_type.append('NGS')
		elif 'A' in row[3]:
			analysis_type.append('Sanger')
		elif 'B' in row[3]:
			analysis_type.append('Sanger')
		elif 'C' in row[3]:
			analysis_type.append('Sanger')
		else:
			analysis_type.append('Other')
	df_a['analysis_type'] = analysis_type

	#create a dictionary to pull the appropriate analysis_type_id for each record from the analysis_type.csv file. Store these as a new column
	analysis_type_dict = dict(zip(df2.analysis_type, df2.analysis_type_id))
	df_a['analysis_type_id'] = df_a['analysis_type'].map(analysis_type_dict)

	#create a new primer_set field based on the current field containing either A / B / C
	primer_set = []
	for index, row in df_a.iterrows():
		if 'A' in row[3]:
			primer_set.append('A')
		elif 'B' in row[3]:
			primer_set.append('B')
		elif 'C' in row[3]:
			primer_set.append('C')
		else:
			primer_set.append('Other')
	df_a['primer_set'] = primer_set

	#create a dictionary to pull the appropriate primer_set_id for each record from the primer_set.csv file. Store these as a new column
	primer_set_dict = dict(zip(df4.primer_set, df4.primer_set_id))
	df_a['primer_set_id'] = df_a['primer_set'].map(primer_set_dict)

	#exon data stored in the 'fragment' field for Sanger primers - field contains other information for NGS primers. Pull exon data from the fragment field for Sanger primers only and store as new column
	exon = []
	for index, row in df_a.iterrows():
		if row[6] == 0:
			exon.append(None)
		else:
			exon.append(row[1])
	df_a['exon'] = exon

	#drop irrelevant columns
	df_a = df_a.drop(columns = ['Fragment', 'Gene', 'Set', 'analysis_type', 'primer_set'])

	#drop duplicate records
	df_a = df_a.drop_duplicates(keep='first')

	#create an amplicon_id for each unique record 
	df_a['amplicon_id'] = df.groupby(['Amplicon_ID']).ngroup()

	#rename the amplicon_name column 
	df_a = df_a.rename(columns={'Amplicon_ID': 'amplicon_name'})

	#save as csv
	df_a.to_csv('amplicon.csv', sep=',')

#call function
amplicon()

#store the amplicon.csv as a pandas dataframe for downstream reference
df6 = pd.read_csv('amplicon.csv')


#create the csv file for upload to the 'Primer' table of the database
def primer(): 

	#forward and reverse primers stored as one 'amplicon' record - split as individual primers in new database - copy relevant columns into two dataframes for the forward and reverse primers, add appropriate direction and rename columns 
	df_p1 = df[['F', 'F Location', 'Alt Name F', 'Amplicon_ID', 'Date Entered Service/Imported', 'Imported By', 'Fragment', 'Set', 'Genomic Loc 1', 'Genomic Loc 2', 'Comments']].copy()

	df_p1 = df_p1.rename(columns={'F': 'sequence', 'F Location': 'location', 'Alt Name F': 'alt_name', 'Amplicon_ID':'amplicon_name', 'Date Entered Service/Imported': 'date_imported', 'Imported By': 'imported_by', 'Genomic Loc 1': 'genomic_location_start', 'Genomic Loc 2': 'genomic_location_end', 'Comments': 'comments'})

	direction_F = 'F'

	df_p1['direction'] = direction_F

	df_p2 = df[['R', 'R Location', 'Alt Name R', 'Amplicon_ID', 'Date Entered Service/Imported', 'Imported By', 'Fragment', 'Set', 'Genomic Loc 1', 'Genomic Loc 2', 'Comments']].copy()

	df_p2 = df_p2.rename(columns={'R': 'sequence', 'R Location': 'location', 'Alt Name R': 'alt_name', 'Amplicon_ID':'amplicon_name', 'Date Entered Service/Imported': 'date_imported', 'Imported By': 'imported_by', 'Genomic Loc 1': 'genomic_location_start', 'Genomic Loc 2': 'genomic_location_end', 'Comments': 'comments'})

	direction_R = 'R'

	df_p2['direction'] = direction_R

	#concatentate the two dataframes
	df_p3 = pd.concat([df_p1, df_p2])

	#empty sequence fields contain space - replace with nan to prevent downstream errors
	df_p3['sequence'] = df_p3['sequence'].replace(' ', np.nan)

	#drop primers with empty sequence 
	df_p3 = df_p3.dropna(subset=['sequence'])

	#create a dictionary to pull the appropriate amplicon_id for each record from the amplicon.csv file. Store these as a new column
	amplicon_dict = dict(zip(df6.amplicon_name, df6.amplicon_id))
	df_p3['amplicon_id'] = df_p3['amplicon_name'].map(amplicon_dict)

	#convert all names to uppercase
	df_p3['imported_by'] = df_p3['imported_by'].str.upper()

	#replace all names in the imported_by field with appropriate full name from the lab telephone directory
	name = []
	for index, row in df_p3.iterrows():
		if 'ARIELE' in row[5]:
			name.append('Ariele Rosseto')
		elif 'BENITO' in row[5]:
			name.append('Benito Banos-Pinero')
		elif 'CNS' in row[5]:
			name.append('Caroline Sarton')
		elif 'CAROLINE' in row[5]:
			name.append('Caroline Sarton')
		elif 'CARL' in row[5]:
			name.append('Carl Fratter')
		elif 'CLAIRE HODGKISS' in row[5]:
			name.append('Claire Hodgkiss')
		elif 'CONRAD' in row[5]:
			name.append('Conrad Smith')
		elif 'ELIZABTH WOOD' in row[5]:
			name.apend('Elizabeth Wood')
		elif 'ELIZABETH' in row[5]:
			name.append('Elizabeth Wood')
		elif 'EMILY' in row[5]:
			name.append('Emily Packham')
		elif 'HANNAH BOON' in row[5]:
			name.append('Hannah Boon')
		elif 'MATTEN' in row[5]:
			name.append('Hannah Matten')
		elif 'HELEN LORD' in row[5]:
			name.append('Helen Lord')
		elif 'JESS GABRIEL' in row[5]:
			name.append('Jess Gabriel')
		elif 'JESSICA WOODLEY' in row[5]:
			name.append('Jessica Woodley')
		elif 'TAYLOR' in row[5]:
			name.append('John Taylor')
		elif 'JULIE' in row[5]:
			name.append('Julie')
		elif 'LIZZIE/MIKEB' in row[5]:
			name.append('Michael Bowman')
		elif 'BOWMAN' in row[5]:
			name.append('Michael Bowman')
		elif 'OLDRIDGE' in row[5]:
			name.append('Michael Oldridge')
		elif 'WARE' in row[5]:
			name.append('Pauline Ware')
		elif 'SARAH REID' in row[5]:
			name.append('Sarah Reid')
		elif 'BEDENHAM' in row[5]:
			name.append('Tina Bedenham')
		elif 'LESTER' in row[5]:
			name.append('Tracy Lester')
		elif 'TREENA' in row[5]:
			name.append('Trenna Cranston')
		elif 'LOUISE' in row[5]:
			name.append('Louise Williams')
		else:
			name.append(row[5])
	df_p3['imported_by'] = name

	#create a dictionary to pull the appropriate imported_by_id for each record from the imported_by.csv file. Store these as a new column
	imported_by_dict = dict(zip(df5.imported_by, df5.imported_by_id))
	df_p3['imported_by_id'] = df_p3['imported_by'].map(imported_by_dict)

	#for ngs primers, the audit number is stored in the fragment field - pull this for NGS primers and store as new column
	ngs_audit_number = []
	for index, row in df_p3.iterrows():
		if 'NGS' in row[7]:
			ngs_audit_number.append(row[6])
		else:
			ngs_audit_number.append(None)
	df_p3['ngs_audit_number'] = ngs_audit_number	

	#drop irrelevant columns
	df_p3 = df_p3.drop(columns = ['amplicon_name', 'imported_by', 'Fragment', 'Set'])

	#standardise the date format by replacing . and - with /
	df_p3['date_imported'] = df_p3['date_imported'].replace(to_replace = '\.', value = '/', regex=True)
	df_p3['date_imported'] = df_p3['date_imported'].replace(to_replace = '-', value = '/', regex=True)

	#convert sequence to uppercase
	df_p3['sequence'] = df_p3['sequence'].str.upper()

	#replace empty ngs numbers with 0 to prevent errors downstream 
	df_p3['ngs_audit_number'] = df_p3['ngs_audit_number'].replace(np.nan, 0)

	#if there is a primer version number it is stored in the alt name column as the final component after the '_'. Pull this for primers and store as '1' otherwise. Store as new column.
	version = []
	for index, row in df_p3.iterrows():
		if pd.isnull(row[2]) == True or str(row[2]).split('_')[-1].startswith('v') == False:
			version.append('v1')
		else:
			version.append(str(row[2]).split('_')[-1])
	df_p3['version'] = version

	#strip the v from the version number to store as int
	df_p3['version'] = df_p3['version'].str.strip('v')

	#replace null values in genomic start and end locations with 0 values to prevent errors with database
	df_p3['genomic_location_start'] = df_p3['genomic_location_start'].replace(np.nan, 0)
	df_p3['genomic_location_end'] = df_p3['genomic_location_end'].replace(np.nan, 0)
	
	#create a primer id for each unique record
	df_p3['primer_id'] = df_p3.groupby(['sequence', 'location', 'direction', 'amplicon_id']).ngroup()

	#save as csv
	df_p3.to_csv('primer.csv', sep=',')

#call function
primer()	
