#import relevant libraries
from django.shortcuts import render, get_object_or_404
from .models import Primer, Amplicon, Analysis_Type, Imported_By, Gene, Primer_Set
from itertools import chain
from collections import Counter
from datetime import date 
import glob
import collections


#provides context for the index / search page 
def index(request):

	#pull the count of primers, amplicons and genes
	num_primers = Primer.objects.all().count()

	num_amplicons = Amplicon.objects.all().count()

	num_genes = Gene.objects.all().count()

	imp_by = Imported_By.objects.all()

	context = {
		'num_primers': num_primers,
		'num_amplicons': num_amplicons,
		'num_genes': num_genes,
		'imp_by': imp_by
	}

	return render(request, 'index.html', context=context)


#called after a primer is submitted on the order.html page. Function one of three - separated as the first two make changes to the database required for the third.
#adds a new gene to the database if the requested primer is in a gene not currently stored
def submitted1(request):
	
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

	#render the submitted html page 
	return render(request, 'submitted.html')


#function two of three for primer order submission. 
def submitted2(request):

	#call first function
	submitted1(request)

	#make changes to the amplicon table of the primer database 
	amplicon = Amplicon()

	#create amplicon name using other fields POTENTIALLY NEED MORE INFO / FIELDS 
	if request.POST.get('analysis_type') == 'Sanger':
		amplicon.amplicon_name = request.POST.get('set') + '_' + request.POST.get('gene') + '_' + request.POST.get('exon') + '_' + '_' + '_' + request.POST.get('direction') + '_' + '_' + '_' + request.POST.get('version')
	elif request.POST.get('analysis_type') == 'NGS':
		amplicon.amplicon_name = request.POST.get('set') + '_' + 'NGS' + '_' + '_' + '_' + '_' + request.POST.get('direction') + '_' + '_' + '_' + request.POST.get('version')
	elif request.POST.get('analysis_type') == 'Light Scanner':
		amplicon.amplicon_name = 'LS' + '_' + request.POST.get('gene') + '_' + request.POST.get('exon') + '_' + '_' + '_' + request.POST.get('direction') + '_' + '_' + '_' + request.POST.get('version')
	elif request.POST.get('analysis_type') == 'MLPA':
		amplicon.amplicon_name = 'ML' + '_' + request.POST.get('gene') + '_' + request.POST.get('exon') + '_' + '_' + '_' + request.POST.get('direction') + '_' + '_' + '_' + request.POST.get('version')
	elif request.POST.get('analysis_type') == 'Fluorescent':
		amplicon.amplicon_name = 'GM' + '_' + request.POST.get('gene') + '_' + request.POST.get('exon') + '_' + '_' + '_' + request.POST.get('direction') + '_' + '_' + '_' + request.POST.get('version')
	elif request.POST.get('analysis_type') == 'Long Range':
		amplicon.amplicon_name = 'LR' + '_' + request.POST.get('gene') + '_' + request.POST.get('exon') + '_' + '_' + '_' + request.POST.get('direction') + '_' + '_' + '_' + request.POST.get('version')
	elif request.POST.get('analysis_type') == 'RT-PCR':
		amplicon.amplicon_name = 'RT' + '_' + request.POST.get('gene') + '_' + request.POST.get('exon') + '_' + '_' + '_' + request.POST.get('direction') + '_' + '_' + '_' + request.POST.get('version')
	elif request.POST.get('analysis_type') == 'Taqman':
		amplicon.amplicon_name = 'TQ' + '_' + request.POST.get('gene') + '_' + request.POST.get('exon') + '_' + '_' + '_' + request.POST.get('direction') + '_' + '_' + '_' + request.POST.get('version')
	elif request.POST.get('analysis_type') == 'Pyrosequencing':
		amplicon.amplicon_name = 'P' + '_' + request.POST.get('gene') + '_' + request.POST.get('exon') + '_' + '_' + '_' + request.POST.get('direction') + '_' + '_' + '_' + request.POST.get('version')
	elif request.POST.get('analysis_type') == 'ARMS: Mutant':
		amplicon.amplicon_name = 'ARMS_M' + '_' + request.POST.get('gene') + '_' + request.POST.get('exon') + '_' + '_' + '_' + request.POST.get('direction') + '_' + '_' + '_' + request.POST.get('version')
	elif request.POST.get('analysis_type') == 'ARMS: Normal':
		amplicon.amplicon_name = 'ARMS_N' + '_' + request.POST.get('gene') + '_' + request.POST.get('exon') + '_' + '_' + '_' + request.POST.get('direction') + '_' + '_' + '_' + request.POST.get('version')


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

	#render the submitted html page
	return render(request, 'submitted.html')


#function three of three for primer order submission 
def submitted(request):
	
	#call second function
	submitted2(request)

	num_primers = len(request.POST.getlist('seq'))
	seq = request.POST.getlist('seq')
	direction = request.POST.getlist('direction')
	start = request.POST.getlist('start')
	end = request.POST.getlist('end')
	modification = request.getlist('modification')
	ngs = request.POST.getlist('ngs')
	alt_name = request.POST.getlist('alt_name')
	version = request.POST.getlist('version')
	comments = request.POST.getlist('comments')

	for i in range(num_primers):
		primer = Primer()
		primer.sequence = seq[i].upper()
		primer.direction = direction[i].upper()
		primer.modification = modification[i]
		primer.alt_name = alt_name[i]
		primer.comments = comments[i]

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

		today = date.today()
		primer.date_imported = today.strftime("%d/%m/%Y")

		primer.order_status = "Ordered"

		find_imp = Imported_By.objects.filter(imported_by=request.POST.get('imp_by'))
		for f in find_imp:
			primer.imported_by_id = f

		if version[i] == "":
			primer.version = 1
		else:
			primer.version = version[i]

		primer.amplicon_id = Amplicon.objects.all().order_by('-id')[0]

		primer.save()

	return render(request, 'submitted.html')


def order(request):
	return render(request, 'order.html')

#returns the order page for a new primer in response to user clicking the 'order primer' searchbar option
def order_form(request):

	number = list(range(0, int(request.GET.get('number'))))

	#pull imported by options from database to present as dropdown menu
	imp_by = Imported_By.objects.all()
	context = {
		"imp_by": imp_by,
		"number":number
	}

	#render the order html page
	return render(request, 'order_form.html', context=context)


#queries the database to pull primers matching the users search terms from the home / search page 
def search(request):

	#assign each of the user search inputs to variables 
	amp_id_input = request.GET.get('amp_id_input', None)
	gen_loc_input = request.GET.get('gen_loc_input', None)
	analysis_input = request.GET.get('analysis_input', None)
	set_input = request.GET.get('set_input', None)
	gene_input = request.GET.get('gene_input', None).upper()
	chr_input = request.GET.get('chr_input', None).upper()
	imp_by_input = request.GET.get('imp_by_input', None).upper()
	date_input = request.GET.get('date_input', None)

	#provide a count of how many fields the user completed 
	completed_fields = 0
	
	#if user completed amplicon id field, add 1 to the completed field variable and pull respective primers
	if amp_id_input !="":

		completed_fields +=1

		amp_id_query = Amplicon.objects.get(amplicon_name=amp_id_input)

		primer_amp = amp_id_query.primer_set.all()
	
	#if amplicon id field was not completed, set variables to "" to prevent errors of it not being assigned when set as context below
	else:

		amp_id_query = ""

		primer_amp =""	

	#if user completed the gene location fields, pull primers with a gene location between the specified start and end. As primers are stored in both directions, check both ways and concatenate the final results. As above, if the field was completed, add 1 to the completed fields variable, otherwise set the query to ""
	if gen_loc_input !="":

		completed_fields +=1

		gen_loc_fw_query = Primer.objects.filter(genomic_location_start__lte=gen_loc_input, genomic_location_end__gte=gen_loc_input)
		gen_loc_rev_query = Primer.objects.filter(genomic_location_start__gte=gen_loc_input, genomic_location_end__lte=gen_loc_input)

		gen_loc_query = list(chain(gen_loc_fw_query, gen_loc_rev_query))

	else: 

		gen_loc_query = ""

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

	#same process as for the analysis field input above repeated for 'primer set' input
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

	#same process as for the analysis field input above repeated for 'gene' input
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

	#same process as for the analysis field input above repeated for 'chromosome' input
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

	#same process as for the analysis field input above repeated for 'imported by' input
	if imp_by_input !="":

		completed_fields +=1

		imp_by_query = Imported_By.objects.filter(imported_by=imp_by_input)

		primer_imp_by = []
		for i in imp_by_query:
			primer_imp_by.append(i.primer_set.all())

	else:
		imp_by_query = ""
		primer_imp_by = ""

	#if date input field was completed by user, add 1 to the completed field varibale and pull primers - primers can be pulled directly as date is stored in the primer table of the database
	if date_input !="":

		completed_fields +=1

		date_query = Primer.objects.filter(date_imported=date_input)

	else: 
		date_query = ""

	#create an empty list and append all primers pulled from the database based on user input above
	primer_search = []

	#two for loops are required for those with input 2 foreign keys away from the primer table 
	for a in primer_amp:
		primer_search.append(a)

	for g in gen_loc_query:
		primer_search.append(g)

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

	for i in primer_imp_by:
		for x in i:
			primer_search.append(x)

	for d in date_query:
		primer_search.append(d)

	#provide a count for each primer occurance 
	occurence_count = collections.Counter(primer_search)

	#want to pull primers that match all search terms - append primers that appear in the primer search list the same number of times as the calculated completed fields variable 
	primer_search_results = []
	for primer, count in occurence_count.items():
		if count == completed_fields:
			primer_search_results.append(primer)

	#provide a count of the number of returned primers for the html page 
	num_primers = len(primer_search_results)
	
	#provide appropriate context for the search html page
	context = {
		'primer_search_results': primer_search_results,
		'num_primers': num_primers,
	}

	#render the search html page 
	return render(request, 'search.html', context=context)

#pulls primer information at the request of the user clicking on a specific primer on the search results html page 
def primer(request):

	#pulls information for the primer selected by the user from the database 
	primer_input = request.GET.get('selected_primer', None)
	primer = Primer.objects.get(id=primer_input)

	#the rendered primer page will permit the reorder of the primer - this requires input of who is ordering - pull imported_by names from the database for drop-down menu 
	imp_by = Imported_By.objects.all()

	#provide appropriate context for the primer html page 
	context = {
		'primer':primer,
		'imp_by':imp_by
	}

	#render the primer html page 
	return render(request, 'primer.html', context=context)
	
#pulls all primer information for an amplicon at the request of the user clicking on a specific amplicon on the search results html page 
def amplicon(request):

	#pulls information for the amplicon selected by the user from the database
	amplicon_input = request.GET.get('selected_amplicon', None)
	amplicon = Amplicon.objects.get(amplicon_name=amplicon_input)

	#pulls primer information for amplicon 
	primer = amplicon.primer_set.all()

	#provide context for the amplicon html page 
	context = {
		'amplicon': amplicon,
		'primer': primer
	}

	#render the html page 
	return render(request, 'amplicon.html', context=context)


#pulls the information of all primers with an order status of 'ordered' in response to the user clicking the 'primers on order' searchbar link
def ordered(request):

	ordered = Primer.objects.filter(order_status = "Ordered")

	#provide context for the ordered html page 
	context = {
		"ordered": ordered
	}

	#render the ordered html page 
	return render(request, 'ordered.html', context=context)


#allows user to order a primer for an exisiting amplicon - directed from link on the amplicon search result page, opens a form to submit a new primer 
def order_to_amplicon(request): 

	#pull the specific amplicon from the database
	pulled = Amplicon.objects.filter(pk=request.POST.get('amplicon'))

	#pulls imported_by information for drop down menu 
	imp_by = Imported_By.objects.all()

	#provide context for the 'order to amplicon' html page 
	context = {
	'pulled':pulled,
        'imp_by':imp_by
	}

	#render 'order to amplicon' html page 
	return render(request, 'order_to_amplicon.html', context=context)


#submission of a primer for an exisiting amplicon - request from the 'order to amplicon' html page 
def submitted_to_amplicon(request):

	#make changes to the primer table of the database 
	primer = Primer()

	#sequence input by user converted to uppercase and stored as new primer record in database 
	primer.sequence = request.POST.get('seq').upper()

	#direction input by user converted to uppercase and stored as new primer record in database
	primer.direction = request.POST.get('direction').upper()

	#if genomic start location input by user - input stored as new primer record in database, otherwise stored as None 
	if request.POST.get('start') != "":
		primer.genomic_location_start = request.POST.get('start')
	else:
		primer.genomic_location_start = None

	#if genomic end location input by user - input stored as new primer record in database, otherwise stored as None 
	if request.POST.get('end') != "":
		primer.genomic_location_end = request.POST.get('end')
	else:
		primer.genomic_location_end = None

	primer.modification = request.post.get('modification')

	#alt name input by user stored as a new primer record in database 
	primer.alt_name = request.POST.get('alt_name')

	#if ngs audit number input by user - input stored as a new primer record in database, otherwise stored as None 
	if request.POST.get('ngs') != "":
		primer.ngs_audit_number = request.POST.get('ngs')
	else:
		primer.ngs_audit_number = None

	#assign the date imported for the new primer record as todays date 
	today = date.today()
	primer.date_imported = today.strftime("%d/%m/%Y")

	#assign the order status of the new primer record to 'ordered'
	primer.order_status = "Ordered"

	#imported_by input by user stored as new primer record in database 
	find_imp = Imported_By.objects.filter(imported_by=request.POST.get('imp_by'))
	for f in find_imp:
		primer.imported_by_id = f

	#if version input by user - input stored as new primer record in database, otherwise stored as 1 
	if request.POST.get('version') == "":
		primer.version = 1
	else:
		primer.version = request.POST.get('version')

	#amplicon id for new primer record assigned to selected primer 
	amp = Amplicon.objects.filter(pk=request.POST.get('amplicon'))
	for a in amp:
		primer.amplicon_id = a

	#database updated with new primer record 
	primer.save()
	
	#context for the 'submitted to amplicon' html page 
	context = {
		'amp':amp
	}
	
	#render the 'submitted to amplicon' html page 
	return render(request, 'submitted_to_amplicon.html', context=context)


#reorders a primer at the request of the user clicking the 'reorder primer' button on the primer html page 
def reorder_primer(request):

	#pull specific primer from the database 
	reorder = Primer.objects.get(pk=request.POST.get('primer'))

	#make changes to the primer table of the database 
	primer = Primer()

	#assign new primer record the same sequence, direction, alt name and ngs audit number as the primer record selected for reorder 
	primer.sequence = reorder.sequence
	primer.genomic_location_start = reorder.genomic_location_start
	primer.genomic_location_end = reorder.genomic_location_end
	primer.location = reorder.location
	primer.direction = reorder.direction
	primer.modification = reorder.modification
	primer.alt_name = reorder.alt_name
	primer.ngs_audit_number = reorder.ngs_audit_number
	primer.comments = primer.comments

	#imported_by input by user stored as new primer record in database 
	find_imp = Imported_By.objects.filter(imported_by=request.POST.get('imp_by'))
	for f in find_imp:
		primer.imported_by_id = f

	#assign the date imported for the new primer record as todays date 
	today = date.today()
	primer.date_imported = today.strftime("%d/%m/%Y")
	primer.date_order_placed = today.strftime("%d/%m/%Y")

	#assign the order status of the new primer record to 'ordered'
	primer.order_status = "Ordered"

	#assign the new primer record the same version number and amplicon id as the primer record selected for reorder 
	primer.version = reorder.version
	primer.amplicon_id = reorder.amplicon_id

	#reason reordered input by user added to the primer record 
	primer.reason_reordered = request.POST.get('reason_reordered')

	#update the database 
	primer.save()
	
	#provide context for the 'submitted reorder primer' html page 
	context = {
		'reorder':reorder
	}
	
	#render the 'submitted reorder primer' html page 
	return render(request, 'submitted_reorder_primer.html', context=context)


#allow users to archive a primer currently recorded as 'stocked' from the primer search result html page 
def archive_primer(request):

	#pull the primer for archiving 
	archive = Primer.objects.get(pk=request.POST.get('archive'))

	#ammend the order status of the primer to archived 
	archive.order_status = 'Archived'

	#ammend the lab location to ""
	archive.location = ""

	#archived by input by user added to the primer record 
	find_arc = Imported_By.objects.filter(imported_by=request.POST.get('arc_by'))
	for f in find_arc:
		archive.archived_by = f

	#todays date added to the primer record as the date archived
	today = date.today()
	archive.date_archived = today.strftime("%d/%m/%Y")

	#reason archived input by user added to the primer record 
	archive.reason_archived = request.POST.get('reason_archived')

	#update the database 
	archive.save()
	
	#provide context for the archive primer html page 
	context = {
		'archive':archive
	}
	
	#render the archive primer html page 
	return render(request, 'archive_primer.html', context=context)


#allow users to update the status of a primer from having been requested to order placed with the company from the 'primers to be ordered' page  
def submit_order(request):

	#pull the selected primers for the status change based on the checkboxes selected on the 'primers to be ordered' html page
	primer_list = request.POST.getlist('primer')
	
	#iterate through the list of primers selected, update the order status and assign the 'date_order_placed' as todays date. 
	if 'ordered' in request.POST:
		for primer in primer_list:
			order = Primer.objects.get(pk=primer)
			order.order_status = 'Order Placed'
			today = date.today()
			order.date_order_placed = today.strftime("%d/%m/%Y")
			order.save()		

	if 'delete' in request.POST:
		for primer in primer_list:
			delete = Primer.objects.get(pk=primer)
			delete.delete()			

	#render the 'submit order' html page 
	return render(request, 'submit_order.html')

#pulls the information of all primers with an order status of 'ordered' in response to the user clicking the 'primers on order' searchbar link
def order_placed(request):

	ordered = Primer.objects.filter(order_status = "Order Placed")

	#provide context for the ordered html page 
	context = {
		"ordered": ordered
	}

	#render the ordered html page 
	return render(request, 'order_placed.html', context=context)

#allow users to update the status of a primer from having been requested to order placed with the company from the 'primers to be ordered' page  
def order_recieved(request):

	#pull the selected primers for the status change based on the checkboxes selected on the 'primers to be ordered' html page. 
	primer_list = request.POST.getlist('primer')
	list_len = len(request.POST.getlist('primer'))
	location_list = request.POST.getlist('location')
	
	#iterate through the list of primers selected, update the order status and assign the 'date_order_placed' as todays date. 
	if 'test' in request.POST:
		for i in range(list_len):
			recieved = Primer.objects.get(pk=primer_list[i])
			recieved.order_status = 'In Testing'
			today = date.today()
			recieved.date_order_recieved = today.strftime("%d/%m/%Y")
			recieved.location = location_list[i]
			recieved.save()		

	#iterate through the list of primers selected, update the order status and assign the 'date_order_placed' as todays date. 
	if 'stock' in request.POST:
		for i in range(list_len):
			recieved = Primer.objects.get(pk=primer_list[i])
			recieved.order_status = 'Stocked'
			today = date.today()
			recieved.date_order_recieved = today.strftime("%d/%m/%Y")
			recieved.location = location_list[i]
			recieved.save()			

	#render the 'submit order' html page 
	return render(request, 'order_recieved.html')

#pulls the information of all primers with an order status of 'ordered' in response to the user clicking the 'primers on order' searchbar link
def in_testing(request):

	testing = Primer.objects.filter(order_status = "In Testing")

	#provide context for the ordered html page 
	context = {
		"testing": testing
	}

	#render the in testing html page 
	return render(request, 'in_testing.html', context=context)


#allow users to update the status of a primer from having been requested to order placed with the company from the 'primers to be ordered' page  
def tested(request):

	#pull the selected primers for the status change based on the checkboxes selected on the 'primers to be ordered' html page
	primer_list = request.POST.getlist('primer')
	
	#iterate through the list of primers selected, update the order status and assign the 'date_order_placed' as todays date. 
	if 'validated' in request.POST:
		for primer in primer_list:
			tested = Primer.objects.get(pk=primer)
			tested.order_status = 'Stocked'
			today = date.today()
			tested.date_testing_completed = today.strftime("%d/%m/%Y")
			tested.save()		

	#iterate through the list of primers selected, update the order status and assign the 'date_order_placed' as todays date. 
	if 'not' in request.POST:
		for primer in primer_list:
			tested = Primer.objects.get(pk=primer)
			tested.order_status = 'Failed Validation'
			today = date.today()
			tested.date_tesing_completed = today.strftime("%d/%m/%Y")
			tested.save()			

	#render the 'submit order' html page 
	return render(request, 'tested.html')

#pulls the information of all primers with an order status of 'ordered' in response to the user clicking the 'primers on order' searchbar link
def failed(request):

	failed = Primer.objects.filter(order_status = "Failed Validation")

	#provide context for the ordered html page 
	context = {
		"failed": failed
	}

	#render the in testing html page 
	return render(request, 'failed.html', context=context)



	


