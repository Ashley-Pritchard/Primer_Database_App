#views - each function takes a web request and returns a web response. The web app has search bar at the top - the below requests have been ordered into respecitive pages and their derivatives. 

#import relevant libraries
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import *
from itertools import chain
from collections import Counter
from datetime import date 
import glob
import collections
import csv


## Search Page ##


#provides context for the index / search page - takes request from users clicking on the 'search' option of the searchbar 
def index(request):

	#pull the count of primers, amplicons and genes
	num_primers = Primer.objects.all().count()
	num_amplicons = Amplicon.objects.all().count()
	num_genes = Gene.objects.all().count()

	#the search page provides a dropdown menu to look up primers by who they were 'imported by' - pull this information from the database
	imp_by = Imported_By.objects.all()

	#assign pulled information as context for the page 
	context = {
		'num_primers': num_primers,
		'num_amplicons': num_amplicons,
		'num_genes': num_genes,
		'imp_by': imp_by
	}

	#returns the index html page from the templates directory 
	return render(request, 'index.html', context=context)





#takes the users search terms from the index /search page as the request and queries the database to pull matching primers 
def search(request):

	#assign each of the user search inputs to variables 
	amp_id_input = request.GET.get('amp_id_input', None)
	analysis_input = request.GET.get('analysis_input', None)
	set_input = request.GET.get('set_input', None)
	gene_input = request.GET.get('gene_input', None).upper()
	chr_input = request.GET.get('chr_input', None).upper()
	alt_input = request.GET.get('alt_input', None)

	#provide a count of how many fields the user completed 
	completed_fields = 0
	
	#if user completed amplicon id field, add 1 to the completed field variable and pull respective primers
	if amp_id_input !="":
		completed_fields +=1
		amp_id_query = Amplicon.objects.filter(amplicon_name__icontains=amp_id_input)

		primer_amp = []
		for a in amp_id_query:
			primer_amp.append(a.primer_set.all())
	
	#if amplicon id field was not completed, set variables to "" to prevent errors of it not being assigned when set as context below
	else:
		amp_id_query = ""
		primer_amp =""	

	#if user completed the analysis input field, add 1 to the completed field varibale and pull resepctive primers 
	if analysis_input !="":
		completed_fields +=1
		analysis_query = Analysis_Type.objects.filter(analysis_type=analysis_input)

		#due to foreign key set-up, two steps to pull primer information from analysis_type: analysis_type -> amplicon -> primer 		
		primer_analysis = []
		for a in analysis_query:
			x = a.amplicon_set.all()
			for y in x:
				primer_analysis.append(y.primer_set.all())

	#if analysis type field was not completed, set variables to "" to prevent downstream errors 
	else:
		analysis_query = ""
		primer_analysis = ""

	#same process as for the analysis field input above is repeated for 'primer set' input
	if set_input !="":
		completed_fields +=1
		set_query = Primer_Set.objects.filter(primer_set=set_input)

		primer_set = []
		for s in set_query:
			x = s.amplicon_set.all()
			for y in x:
				primer_set.append(y.primer_set.all())

	else:
		set_query = ""
		primer_set = ""

	#same process as for the analysis field input above is repeated for 'gene' input
	if gene_input !="":
		completed_fields +=1
		gene_query = Gene.objects.filter(gene_name=gene_input)

		primer_gene = []
		for g in gene_query:
			x = g.amplicon_set.all()
			for y in x:
				primer_gene.append(y.primer_set.all())

	else:
		gene_query = ""
		primer_gene = ""

	#same process as for the analysis field input above is repeated for 'chromosome' input
	if chr_input !="":
		completed_fields +=1
		chr_query = Gene.objects.filter(chromosome=chr_input)

		primer_chr = []
		for c in chr_query:
			x = c.amplicon_set.all()
			for y in x:
				primer_chr.append(y.primer_set.all())

	else:
		chr_query = ""
		primer_chr = ""

	#if user completed the alt name field, add 1 to the completed field variable and pull respective primers
	if alt_input !="":
		completed_fields +=1
		primer_alt = Primer.objects.filter(alt_name__icontains=alt_input)

	else:
		primer_alt = ""

	#create an empty list and append all primers pulled from the database based on user input above
	primer_search = []

	#append primers to list - two for loops are required for those with input 2 foreign keys away from the primer table 
	for a in primer_amp:
		for x in a:
			primer_search.append(x)

	for a in primer_analysis:
		for x in a:
			primer_search.append(x)

	for s in primer_set:
		for x in s:
			primer_search.append(x)

	for g in primer_gene:
		for x in g:
			primer_search.append(x)

	for c in primer_chr:
		for x in c:
			primer_search.append(x)

	for a in primer_alt:
		primer_search.append(a)

	#provide a count for each primer occurance 
	occurence_count = collections.Counter(primer_search)

	#want to pull primers that match all search terms - append primers that appear in the primer search list the same number of times as the calculated completed fields variable 
	primer_search_results = []
	for primer, count in occurence_count.items():
		if count == completed_fields:
			primer_search_results.append(primer)

	#order results alphabetically
	primer_search_results.sort(key=lambda x: x.name)

	#provide a count of the number of returned primers for the html page 
	num_primers = len(primer_search_results)
	
	#provide appropriate context for the search html page
	context = {
		'primer_search_results': primer_search_results,
		'num_primers': num_primers,
	}

	#render the search html page from templates directory
	return render(request, 'search.html', context=context)





#from the search results page, takes user clicking on specific amplicon as request and pulls respective primer information for those matching the amplicon id 
def amplicon(request):

	#pull information for the amplicon selected by the user from the database
	amplicon_input = request.GET.get('selected_amplicon', None)
	amplicon = Amplicon.objects.get(amplicon_name=amplicon_input)

	#pull primer information for amplicon 
	primer = amplicon.primer_set.all()

	#the rendered primer page will permit the reorder of the primer - this requires input of who is ordering - pull imported_by names from the database for drop-down menu 
	imp_by = Imported_By.objects.all()

	#provide context for the amplicon html page 
	context = {
		'amplicon': amplicon,
		'primer': primer,
		'imp_by':imp_by
	}

	#render the amplicon html page from the templates directory 
	return render(request, 'amplicon.html', context=context)





#from both the primer and amplicon search result pages, the user can reorder a primer - function takes input of the user clicking 'reorder primer' as request. Users can also archive a primer from the primer search result page - function takes input of the user clicking 'archive primer' as request. 
def reorder_archive_primer(request):

	#if user selects 'reorder primer'
	if 'reorder' in request.POST:

		#user can select single primer to reorder from primer page or one or more primers from the amplicon page - pull specific primer(s) from the database 
		reorder_list = request.POST.getlist('primer')

		#check a primer was selected 
		if len(reorder_list) != 0:

			#loop through list of primers 
			for i in reorder_list:
				reorder = Primer.objects.get(pk=i)

				#make changes to the primer table of the database 
				primer = Primer()

				#assign new primer record with the same sequence, genomic location, direction, modification, alt name, ngs audit number, version, amplicon id comments and location as the primer record selected for reorder 
				primer.name = reorder.name
				primer.sequence = reorder.sequence
				primer.genomic_location_start = reorder.genomic_location_start
				primer.genomic_location_end = reorder.genomic_location_end
				primer.direction = reorder.direction
				primer.modification = reorder.modification
				primer.alt_name = reorder.alt_name
				primer.ngs_audit_number = reorder.ngs_audit_number
				primer.version = reorder.version
				primer.amplicon_id = reorder.amplicon_id
				primer.comments = reorder.comments
				primer.location = reorder.location

				#assingn the 'imported_by' input selected by user to new primer record 
				find_imp = Imported_By.objects.filter(imported_by=request.POST.get('imp_by'))
				for f in find_imp:
					primer.imported_by_id = f

				#assign the 'date imported' to the new primer record as todays date 
				today = date.today()
				primer.date_imported = today.strftime("%d/%m/%Y")
				primer.date_order_placed = today.strftime("%d/%m/%Y")

				#assign the order status of the new primer record to 'ordered'
				primer.order_status = "Ordered"

				#add reason reordered input by user to the primer record 
				primer.reason_ordered = request.POST.get('reason_reordered')

				#update the database 
				primer.save()
	
			#render the 'submitted reorder primer' html page from the templates directory 
			return render(request, 'submitted_reorder_primer.html')

		#if primer was not selected 
		else:

			#render the 'warning' html page from the templates directory 
			return render(request, 'warning.html')

	#if user selects 'archive primer'
	if 'archive' in request.POST:

		#user can select primer(s) to archive from primer page - pull specific primer(s) from the database
		archive_list = request.POST.getlist('primer')

		#check primer was selected
		if len(archive_list) != 0:

			#loop through primers 
			for i in archive_list:
				archive = Primer.objects.get(pk=i)

				#ammend the order status of the primer to archived 
				archive.order_status = 'Archived'

				#ammend the lab location to ""
				archive.location = ""

				#assign the 'archived by' input selected by user to the primer record 
				find_arc = Imported_By.objects.filter(imported_by=request.POST.get('imp_by'))
				for f in find_arc:
					archive.archived_by_id = f

				#assign the 'date archived' to the primer record as todays date 
				today = date.today()
				archive.date_archived = today.strftime("%d/%m/%Y")

				#add reason archived input by user to the primer record 
				archive.reason_archived = request.POST.get('reason_archived')

				#update the database 
				archive.save()
		
			#render the archive primer html page from the templates directory
			return render(request, 'archive_primer.html')

		#if no primer was selected 
		else:

			#render the 'warning' html page from the templates directory
			return render(request, 'warning.html')




##Order Primer Page ## 


#provides context for the order page - takes request from users clicking on the 'order primer' option of the searchbar 
def order(request):
	#renders the 'order' html page from the templates directory
	return render(request, 'order.html')





#from the order page, takes user input of how many primers they wish to order as request 
def order_form(request):

	#pull number of primers user selected for ordering as a range
	number = list(range(0, int(request.GET.get('number'))))

	#pull imported by options from database to present as dropdown menu
	imp_by = Imported_By.objects.all()

	#provide as context for the order form html page
	context = {
		"imp_by": imp_by,
		"number":number
	}

	#render the order html page from the templates directory 
	return render(request, 'order_form.html', context=context)





#from the order form page, takes submission of new primer(s) as request
#function one of three - separated as the first two make changes to the database required for the third
#function 1 - adds a new gene to the database if the requested primer is in a gene not currently stored
def submit_new_gene(request):

	#pull all genes from the database and store as a list 
	genes = Gene.objects.all()
	gene_names = []
	for g in genes:
		gene_names.append(g.gene_name)

	#if the submitted gene is not in the gene list, add the gene and respective chromosome to the database 
	if request.POST.get('gene').upper() not in gene_names:
		gene = Gene()
		gene.gene_name = request.POST.get('gene').upper()
		gene.chromosome = request.POST.get('chr').upper()

		#save the changes to the database 
		gene.save()

	#render the submitted html page from the templates directory
	return render(request, 'submitted.html')


#function 2 of 3 - adds new amplicon to the database if the requested primer is for an amplicon not currently stored
def submit_new_amplicon(request):

	#call first function
	submit_new_gene(request)

	#pull all amplicons from the database and store as list 
	amplicons = Amplicon.objects.all()
	all_amplicons = []
	for a in amplicons:
		all_amplicons.append(a.amplicon_name)

	#create amplicon name using field input 
	if request.POST.get('analysis_type') == 'Sanger':
		new_amplicon = request.POST.get('set') + '_' + request.POST.get('gene') + '-' + request.POST.get('exon')
	elif request.POST.get('analysis_type') == 'NGS':
		new_amplicon = request.POST.get('set') + '_' + request.POST.get('gene') + '_NGS-' + request.POST.get('ngs')
	elif request.POST.get('analysis_type') == 'Light Scanner':
		new_amplicon = 'LS' + '_' + request.POST.get('gene') + '-' + request.POST.get('exon')
	elif request.POST.get('analysis_type') == 'MLPA':
		new_amplicon = 'ML' + '_' + request.POST.get('gene') + '-' + request.POST.get('exon')
	elif request.POST.get('analysis_type') == 'Fluorescent':
		new_amplicon = 'GM' + '_' + request.POST.get('gene') + '-' + request.POST.get('exon')
	elif request.POST.get('analysis_type') == 'Long Range':
		new_amplicon = 'LR' + '_' + request.POST.get('gene') + '-' + request.POST.get('exon')
	elif request.POST.get('analysis_type') == 'RT-PCR':
		new_amplicon = 'RT' + '_' + request.POST.get('gene') + '-' + request.POST.get('exon')
	elif request.POST.get('analysis_type') == 'Taqman':
		new_amplicon = 'TQ' + '_' + request.POST.get('gene') + '-' + request.POST.get('exon')
	elif request.POST.get('analysis_type') == 'Pyrosequencing':
		new_amplicon = 'P' + '_' + request.POST.get('gene') + '-' + request.POST.get('exon')
	elif request.POST.get('analysis_type') == 'ARMS: Mutant':
		new_amplicon = 'ARMS_M' + '_' + request.POST.get('gene') + '-' + request.POST.get('exon')
	elif request.POST.get('analysis_type') == 'ARMS: Normal':
		new_amplicon = 'ARMS_N' + '_' + request.POST.get('gene') + '-' + request.POST.get('exon')

	#if amplicon does not exist, add to the database
	if new_amplicon not in all_amplicons:
		amplicon = Amplicon()

		#assign name as created above
		amplicon.amplicon_name = new_amplicon

		#set exon based on form submission
		amplicon.exon = request.POST.get('exon')

		#select analysis type from database by filtering on what was input in the submission
		find_analysis = Analysis_Type.objects.filter(analysis_type=request.POST.get('analysis_type'))
		for f in find_analysis:
			amplicon.analysis_type_id = f

		#select gene from database by filtering on what was input in the submission
		find_gene = Gene.objects.filter(gene_name=request.POST.get('gene').upper())
		for f in find_gene:
			amplicon.gene_id = f

		#select set from database by filtering on what was input in the submission
		find_set = Primer_Set.objects.filter(primer_set=request.POST.get('set'))
		for f in find_set:
			amplicon.primer_set_id = f

		#save the changes to the database
		amplicon.save()	

	#render the submitted html page from templates directory 
	return render(request, 'submitted.html')


#function three of three for primer order submission
def submitted(request):

	#call second function
	submit_new_amplicon(request)

	#pull number of primers submitted by calculating the length of the sequence list (mandatory field)
	num_primers = len(request.POST.getlist('seq'))

	#pull lists for each input field for primer(s) submitted 
	seq = request.POST.getlist('seq')
	direction = request.POST.getlist('direction')
	start = request.POST.getlist('start')
	end = request.POST.getlist('end')
	m13 = request.POST.getlist('m13')
	mod_3 = request.POST.getlist('3_modification')
	mod_5 = request.POST.getlist('5_modification')
	ngs = request.POST.getlist('ngs')
	alt_name = request.POST.getlist('alt_name')
	comments = request.POST.getlist('comments')
	reason = request.POST.getlist('reason')

	#pull all primers from the database and store as list 
	primers = Primer.objects.all()
	all_primers = []
	for p in primers:
		all_primers.append(p.name)

	#loop through the number or primers submitted 
	for i in range(num_primers):

		#add 3' and 5' prefix to modification for naming if exist
		if mod_3[i] != "":
			modification_3 = '3\'' + mod_3[i]
		else:
			modification_3 = mod_3[i]
		if mod_5[i] != "":
			modification_5 = '5\'' + mod_5[i]
		else:
			modification_5 = mod_5[i]

		#check if a version of the primer already exists
		if request.POST.get('analysis_type') == 'Sanger':
			new_primer = request.POST.get('set') + '_' + request.POST.get('gene') + '-' + request.POST.get('exon') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'NGS':
			new_primer = request.POST.get('set') + '_' + request.POST.get('gene') + '_NGS-' + request.POST.get('ngs') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'Light Scanner':
			new_primer = 'LS_' + request.POST.get('gene') + '-' + request.POST.get('exon') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'MLPA':
			new_primer = 'ML_' + request.POST.get('gene') + '-' + request.POST.get('exon') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'Fluorescent':
			new_primer = 'GM_' + request.POST.get('gene') + '-' + request.POST.get('exon') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'Long Range':
			new_primer = 'LR_' + request.POST.get('gene') + '-' + request.POST.get('exon') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'RT-PCR':
			new_primer = 'RT_' + request.POST.get('gene') + '-' + request.POST.get('exon') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_tye') == 'Taqman':
			new_primer = 'TQ_' + request.POST.get('gene') + '-' + request.POST.get('gene') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'Pyrosequencing':
			new_primer = 'P_' + request.POST.get('gene') + '-' + request.POST.get('gene') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'ARMS: Mutant':
			new_primer = 'ARMS_M_' + request.POST.get('gene') + '-' + request.POST.get('exon') + '___' + direction[i].upper() + '_' + modficiation_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'ARMS: Normal':
			new_primer = 'ARMS_N_' + request.POST.get('gene') + '-' + request.POST.get('exon') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5

		#save list of matching primers
		matching_primers = [p for p in all_primers if new_primer in p]

		#loop through matching primers to get a count of primer versions and current version number
		version_count = 0
		version_number = []
		version = ()
		for m in matching_primers:
			primer_version = Primer.objects.filter(name=m)

			for p in primer_version:
				version_number.append(p.version)
				#if sequecen matches, close current primer and assign same version number 
				if p.sequence == seq[i].upper():
					version = p.version
					version_count += 1
					p.order_status = 'Closed'
					p.save()

		#if does not match a sequence of any current primer version, make new primer version
		if version_count == 0:
			if len(version_number) != 0:
				version = max(version_number) + 1
			else:
				version = 1

		#make changes to the primer table of the database 
		primer = Primer()

		#assgin user input to each field of the primer table
		primer.sequence = seq[i].upper()
		primer.direction = direction[i].upper()
		primer.modification = mod_3[i]
		primer.modification_5 = mod_5[i]
		primer.alt_name = alt_name[i]
		primer.comments = comments[i]
		primer.reason_ordered = reason[i]
		primer.version = version
		primer.name = str(new_primer) + '_v' + str(version)

		#if requested, add m13 tag as either forward or reverse 
		if m13[i] == "no":
			primer.m13_tag = ""
		elif m13[i] == "yes" and direction[i] == "f":
			primer.m13_tag = "GATAAACGACGGCCAGT"
		elif m13[i] == "yes" and direction[i] == "r":
			primer.m13_tag = "CAGGAAACAGCTATGAC"

		#if genomic start or end location and ngs number is blank, assign 'None', otherwise assign user input
		if start[i] != "":
			primer.genomic_location_start = start[i]
		else:
			primer.genomic_location_start = None

		if end[i] != "":
			primer.genomic_location_end = end[i]
		else:
			primer.genomic_location_end = None

		if ngs[i] != "":
			primer.ngs_audit_number = ngs[i]
		else:
			primer.ngs_audit_number = None

		#assign todays date as 'date imported' for new primer record 
		today = date.today()
		primer.date_imported = today.strftime("%d/%m/%Y")

		#assign 'order status' to ordered
		primer.order_status = "Ordered"

		#assign 'imported by' to user selection
		find_imp = Imported_By.objects.filter(imported_by=request.POST.get('imp_by'))
		for f in find_imp:
			primer.imported_by_id = f

		#assign the amplicon id
		if request.POST.get('analysis_type') == 'Sanger':
			amplicon_name = request.POST.get('set') + '_' + request.POST.get('gene') + '-' + request.POST.get('exon')
		elif request.POST.get('analysis_type') == 'NGS':
			amplicon_name = request.POST.get('set') + '_' + request.POST.get('gene') + '_NGS-' + request.POST.get('ngs')
		elif request.POST.get('analysis_type') == 'Light Scanner':
			amplicon_name = 'LS_' + request.POST.get('gene') + '-' + request.POST.get('exon')
		elif request.POST.get('analysis_type') == 'MLPA':
			amplicon_name = 'ML_' + request.POST.get('gene') + '-' + request.POST.get('exon')
		elif request.POST.get('analysis_type') == 'Fluorescent':
			amplicon_name = 'GM_' + request.POST.get('gene') + '-' + request.POST.get('exon')
		elif request.POST.get('analysis_type') == 'Long Range':
			amplicon_name = 'LR_' + request.POST.get('gene') + '-' + request.POST.get('exon')
		elif request.POST.get('analysis_type') == 'RT-PCR':
			amplicon_name = 'RT_' + request.POST.get('gene') + '-' + request.POST.get('exon')
		elif request.POST.get('analysis_type') == 'Taqman':
			amplicon_name = 'TQ_' + request.POST.get('gene') + '-' + request.POST.get('exon')
		elif amplicon_name == 'Pyrosequencing':
			amplicon_name = 'P_' + request.POST.get('gene') + '-' + request.POST.get('exon')
		elif amplicon_name == 'ARMS: Mutant':
			amplicon_name = 'ARMS_M_' + request.POST.get('gene') + '-' + request.POST.get('exon')
		elif amplicon_name == 'ARMS: Normal':
			amplicon_name = 'ARMS_N_' + request.POST.get('gene') + '-' + request.POST.get('exon')

		find_amp = Amplicon.objects.get(amplicon_name = amplicon_name)
		primer.amplicon_id = find_amp

		#save changes to the database
		primer.save()

		#provide primer context
		context = {
			"primer": primer
		}

	if 'quit' in request.POST:
		#render the submitted html page from the templates directory if they choose to quit
		return render(request, 'submitted.html', context=context)

	if 'reload' in request.POST:
		#render the order.html page from the templates directory if they choose to order more primers
		return render(request, 'order.html')


## Primers to be Ordered Page ##


#takes user clicking the 'primers on order' searchbar link as request and pulls the information of all primers with an order status of 'ordered' 
def ordered(request):

	#pull primers with order status of ordered
	ordered = Primer.objects.filter(order_status = "Ordered")

	#provide context for the ordered html page 
	context = {
		"ordered": ordered
	}

	#render the ordered html page from the templates directory
	return render(request, 'ordered.html', context=context)





#from the 'primers on order page', users are able to select primers and can click one of three buttons to either download the primer information for placing an order for the primers with a company, change the status of the primer to having been ordered with a company or delete the primer order before it is ordered from a company - this function takes the user clicking on any of these buttons as request 
def submit_order(request):

	#pull the selected primers based on the checkboxes selected on the 'primers to be ordered' html page
	primer_list = request.POST.getlist('primer')

	#if the 'download order information' button is clicked, provide a pop up for accepting the download of a csv file
	if 'csv' in request.POST:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="order_information.csv"'

		#write the relevant primer information to a csv file 
		writer = csv.writer(response)
		writer.writerow(['name', 'sequence', 'location', 'reason_for_order', 'date received'])
		for primer in primer_list:
			export = Primer.objects.get(pk=primer)
			writer.writerow([export.name, export.m13_tag + export.sequence, export.location, export.reason_ordered])

		#export the csv file
		return response

	
	#if the 'ordered' button is clicked - iterate through the list of primers selected, update the order status and assign the 'date_order_placed' as todays date. 
	if 'ordered' in request.POST:
		for primer in primer_list:
			order = Primer.objects.get(pk=primer)
			order.order_status = 'Order Placed'
			today = date.today()
			order.date_order_placed = today.strftime("%d/%m/%Y")
			order.save()		

	#if the 'delete' button is clicked - iterate through the list of primers selected and delete from the database
	if 'delete' in request.POST:
		for primer in primer_list:
			delete = Primer.objects.get(pk=primer)
			delete.delete()			

	#render the 'submit order' html page from the templates directory 
	return render(request, 'submit_order.html')





## Primers on Order Page ##


#takes user clicking the 'primers on order' searchbar link as request and pulls the information of all primers with an order status of 'order placed' 
def order_placed(request):

	#pull primers with order status of order placed
	ordered = Primer.objects.filter(order_status = "Order Placed")

	#provide context for the order placed html page 
	context = {
		"ordered": ordered
	}

	#render the order placed html page from the templates directory 
	return render(request, 'order_placed.html', context=context)





#from the 'primers to be ordered' page, allow users to update the status of a primer from having been requested to order placed with the company - takes users selecting primer(s) and clicking on either 'recieved: testing required' or 'recieved: testing not required' as request
def order_recieved(request):

	#pull the selected primer(s) based on the checkboxes selected on the 'primers to be ordered' html page. 
	primer_list = request.POST.getlist('primer')

	#calculate how many primers have been selected from the length of the primer list
	list_len = len(request.POST.getlist('primer'))

	#if 'testing required sanger' is clicked - iterate through the list of primers selected, update the order status to 'in testing sanger', assign the 'date_order_received' as todays date and save changes to the database
	if 'test_sanger' in request.POST:
		for i in range(list_len):
			recieved = Primer.objects.get(pk=primer_list[i])
			recieved.order_status = 'In Testing Sanger'
			today = date.today()
			recieved.date_order_recieved = today.strftime("%d/%m/%Y")
			recieved.save()		

	#if 'testing required non sanger' is clicked - iterate through the list of primers selected, update the order to 'in testing non sanger',assign the 'date order received' as todays date and save changes to the database
	if 'test_non_sanger' in request.POST:
		for i in range(list_len):
			recieved = Primer.objects.get(pk=primer_list[i])
			recieved.order_status = 'In Testing Non-Sanger'
			today = date.today()
			recieved.date_order_recieved = today.strftime("%d/%m/%Y")
			recieved.save()

	#if 'testing not required' is clicked - iterate through the list of primers selected, update the order status to 'stocked', assign the 'date_order_received' as todays date and save changes to the database
	if 'stock' in request.POST:
		for i in range(list_len):
			recieved = Primer.objects.get(pk=primer_list[i])
			recieved.order_status = 'Stocked'
			today = date.today()
			recieved.date_order_recieved = today.strftime("%d/%m/%Y")
			recieved.save()			

	#provide context of submitted primers for the order_recieved html page 
	location_list = []
	for i in range(list_len):
		location_list.append(Primer.objects.get(pk=primer_list[i]))

	context = {
		"location_list":location_list
	} 

	#render the 'submit order' html page from the templates directory 
	return render(request, 'order_recieved.html', context=context)





#for primers submitted as recieved, update the location information
def location_updated(request):

	#pull lists of submitted primers and locations 
	primer = request.POST.getlist('primer')
	location_list = request.POST.getlist('location')
	list_len = len(request.POST.getlist('location'))

	#update the location info for primers locations were submitted for 
	for i in range(list_len):
		update = Primer.objects.get(pk=primer[i])
		if location_list[i] != "":
			update.location = location_list[i]
		update.save()

	#render the 'location_updated' html page from the templates directory
	return render(request, 'location_updated.html')





## In Testing Page ##


#takes user clicking the 'in testing:sanger' searchbar link as request and pulls the information of all sanger primers with an order status of 'in testing' 
def in_testing_sanger(request):

	#pull primers with order status of in testing and analysis type of sanger
	testing = Primer.objects.filter(order_status = "In Testing Sanger")

	#provide context for the in testing: sanger html page 
	context = {
		"testing": testing
	}

	#render the in testing: sanger html page from the templates directory
	return render(request, 'in_testing_sanger.html', context=context)




#takes user clicking the 'in testing: non sanger' searchbar link as request and pulls information of all non sanger primers in testin
def in_testing_non_sanger(request):

	#pulls primers with order status of in testing and analysis type of non-sanger
	testing = Primer.objects.filter(order_status = "In Testing Non-Sanger")

	#provide context for the in testing: non-sanger html page 
	context = {
		"testing": testing
	}

	#return the in testing: non sanger html page from the templates directory
	return render(request, 'in_testing_non_sanger.html', context=context)




#from the 'in testing' page, allows users to update the status of a primer from in testing to either stocked or failed validation - takes user selecting primers and clicking 'validated' or 'not validated' as request   
def tested(request):

	#pull all primers from 'in testing' page 
	all_primer_list = request.POST.getlist('all_primers')

	#pull worksheet info from free text field for all primers 
	worksheet_list = request.POST.getlist('worksheet')

	#pull the selected primers based on the checkboxes selected on the 'in testing' page
	primer_list = request.POST.getlist('primer')

	#update any changes to the worksheet number
	list_len = len(worksheet_list)
	for i in range(list_len):
		update = Primer.objects.get(pk=all_primer_list[i])
		if worksheet_list[i] != "":
			update.worksheet_number = worksheet_list[i]
		update.save()

	#if save was selcted
	if 'save' in request.POST:
		check_status = Primer.objects.get(pk=all_primer_list[0])
		if check_status.order_status == 'In Testing Sanger':

			#pull primers with order status of in testing sanger
			testing = Primer.objects.filter(order_status = "In Testing Sanger")

			#provide context for the in testing html page
			context = {
				"testing": testing
			}

			#render the in testing sanger html page from the templates directory
			return render(request, 'in_testing_sanger.html', context=context)

		else:

			#pull primers with order status of in testing non sanger
			testing = Primer.objects.filter(order_status = "In Testing Non-Sanger")

			#provide context for the in testing html page
			context = {
				"testing": testing
			}

			#render the in testing non sanger html page from the templates directory
			return render(request, 'in_testing_non_sanger.html', context=context)

	#if 'validated' clicked - iterate through the list of primers selected, update the order status to 'stocked', assign the 'date_testing_completed' as todays date and save changes to database
	if 'validated' in request.POST:
		for primer in primer_list:
			tested = Primer.objects.get(pk=primer)
			tested.order_status = 'Stocked'
			today = date.today()
			tested.date_testing_completed = today.strftime("%d/%m/%Y")
			tested.save()		

	#if 'not validated' selected, iterate through the list of primers selected, update the order status to 'failed validation', assign the 'date_testing_completed' as todays date and save changes to database 
	if 'not' in request.POST:
		for primer in primer_list:
			tested = Primer.objects.get(pk=primer)
			tested.order_status = 'Failed Validation'
			today = date.today()
			tested.date_testing_completed = today.strftime("%d/%m/%Y")
			tested.save()			

	#if 'export name and sequence' selected, download a csv file with resepctive information
	if 'export' in request.POST:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="primer_testing.csv"'

		#write information to csv file
		writer = csv.writer(response)
		writer.writerow(['name', 'sequence'])
		for primer in primer_list:
			export = Primer.objects.get(pk=primer)
			writer.writerow([export.name, export.m13_tag + export.sequence])

		#export the csv file 
		return response

	#render the 'tested' html page from the templates directory
	return render(request, 'tested.html')





## Failed Validation Page ##


#takes user clicking the 'failed validation' searchbar link as request and pulls the information of all primers with an order status of 'failed validation'
def failed(request):

	#pull primers with order status of failed validation
	failed = Primer.objects.filter(order_status = "Failed Validation")

	#provide context for the failed html page 
	context = {
		"failed": failed
	}

	#render the failed html page from the templates directory
	return render(request, 'failed.html', context=context)





#allows users to remove primers from the 'failed validation' primers by changing their order status to archived - takes users selecting primers and clicking on 'remove' as request
def remove_failed(request):

	#pull selected primer(s) from the database 
	update_list = request.POST.getlist('primer')

	#if choose to discard primer
	if 'discard' in request.POST: 
		#iterate through primer list, update order status and save changes to database 
		for i in update_list:
			update = Primer.objects.get(pk=i)
			update.order_status = 'Failed_Validation_Archived'
			update.save()

	#if choose to retest primer 
	if 'retest' in request.POST:
		#iterate through primer list, update order status and save changes to database
		for i in update_list:
			update = Primer.objects.get(pk=i)
			update.order_status = "Retesting"
			update.save()

	#render the remove failed html page from templates directory 
	return render(request, 'remove_failed.html')





##Retesting Page##


#takes user cliking on the 'primers in retesting' searchbar link as request and pulls the information of all primers with an order status of 'retesting'
def retesting(request):

	#pull primers with an order status of retesting
	testing = Primer.objects.filter(order_status = "Retesting")

	#provide context for the retesting html page 
	context = {
		"testing": testing
	}

	#render the retesting html page from the templates directory 
	return render(request, 'retesting.html', context=context)




#from the 'retesting' page, allows users to update the status of a primer from retesting to either stocked or failed testing archived - takes user selecting primers and clicking validated or not validated as request:
def retested(request):

	#pull all primers from 'restesting' page
	all_primer_list = request.POST.getlist('all_primers')

	#pull worksheet info from freetext field fo all primers
	worksheet_list = request.POST.getlist('worksheet')

	#pull the selected primers based on the checkbox selected on the retesting page
	primer_list = request.POST.getlist('primer')

	#update any changes made to the worklist field
	list_len = len(worksheet_list)
	for i in range(list_len):
		update = Primer.objects.get(pk=all_primer_list[i])
		if worksheet_list[i] != "":
			update.worksheet_number = worksheet_list[i]
		update.save()

	#if 'save' was selected, reload the page
	if 'save' in request.POST:
		#pull primers with order status of retesting
		testing = Primer.objects.filter(order_status = "Retesting")

		#provide context for the retesting html page
		context = {
			"testing": testing
		}

		#render the retesting html page from the templates directory
		return render(request, 'retesting.html', context=context)

	#if 'validated' clicked - iterate through the list of primers selected, update the order status to stocked, assign the 'date retesting completed' as todays date and save the changes to the database 
	if 'validated' in request.POST:
		for primer in primer_list:
			tested = Primer.objects.get(pk=primer)
			tested.order_status = 'Stocked'
			today = date.today()
			tested.date_retesting_completed = today.strftime("%d/%m/%Y")
			tested.save()

	#if 'not validated' clicked - iterate through the list of primers selected, update the order status to 'failed validation archived', assign the 'date retesting completed' as todays date and save to database 
	if 'not validated' in request.POST:
		for primer in primer_list:
			tested = Primer.objects.get(pk=primer)
			tested.order_status = 'Failed_Validation_Archived'
			today = date.today()
			tested.date_retesting_completed = today.strftime("%d/%m/%Y")
			tested.save()

	#render the  'tested' html page from the templates directory 
	return render(request, 'tested.html')
