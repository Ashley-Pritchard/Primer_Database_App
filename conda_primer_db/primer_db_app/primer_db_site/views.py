from django.shortcuts import render, get_object_or_404
from .models import Primer, Amplicon, Analysis_Type, Imported_By, Gene, Primer_Set
from itertools import chain
from collections import Counter
from datetime import date 
import collections

def index(request):
	num_primers = Primer.objects.all().count()
	num_amplicons = Amplicon.objects.all().count()
	num_genes = Gene.objects.all().count()
	context = {
		'num_primers': num_primers,
		'num_amplicons': num_amplicons,
		'num_genes': num_genes
	}
	return render(request, 'index.html', context=context)

def submitted1(request):
	genes = Gene.objects.all()
	gene_names = []
	for g in genes:
		gene_names.append(g.gene_name)
	if request.POST.get('gene').upper() not in gene_names:
		gene = Gene()
		gene.gene_name = request.POST.get('gene').upper()
		gene.chromosome = request.POST.get('chr').upper()
		gene.save()
	return render(request, 'submitted.html')

def submitted2(request):
	submitted1(request)
	amplicon = Amplicon()
	if request.POST.get('amplicon') == "":
		amplicon.amplicon_name = request.POST.get('set') + '_' + request.POST.get('analysis_type') + '_' + request.POST.get('gene') + '_' + request.POST.get('exon') + '_' + request.POST.get('ngs') + '_' + request.POST.get('version')
	else:
		amplicon.amplicon_name = request.POST.get('amplicon').upper()
	amplicon.exon = request.POST.get('exon')
	find_analysis = Analysis_Type.objects.filter(analysis_type=request.POST.get('analysis_type'))
	for f in find_analysis:
		amplicon.analysis_type_id = f
	find_gene = Gene.objects.filter(gene_name=request.POST.get('gene').upper())
	for f in find_gene:
		amplicon.gene_id = f
	find_set = Primer_Set.objects.filter(primer_set=request.POST.get('set'))
	for f in find_set:
		amplicon.primer_set_id = f
	amplicon.save()	

	return render(request, 'submitted.html')

def submitted(request):
	submitted1(request)
	submitted2(request)

	primer = Primer()
	primer.sequence = request.POST.get('seq').upper()
	primer.direction = request.POST.get('direction').upper()
	primer.alt_name = request.POST.get('alt_name')
	primer.comments = request.POST.get('comments')
	if request.POST.get('start') != "":
		primer.genomic_location_start = request.POST.get('start')
	else:
		primer.genomic_location_start = None
	if request.POST.get('end') != "":
		primer.genomic_location_end = request.POST.get('end')
	else:
		primer.genomic_location_end = None
	if request.POST.get('ngs') != "":
		primer.ngs_audit_number = request.POST.get('ngs')
	else:
		primer.ngs_audit_number = None
	today = date.today()
	primer.date_imported = today.strftime("%d/%m/%Y")
	primer.order_status = "Ordered"
	find_imp = Imported_By.objects.filter(imported_by=request.POST.get('imp_by'))
	for f in find_imp:
		primer.imported_by_id = f
	if request.POST.get('version') == "":
		primer.version = 1
	else:
		primer.version = request.POST.get('version')
	primer.amplicon_id = Amplicon.objects.all().order_by('-id')[0]
	primer.save()

	if request.POST.get('seq2') != "":
		primer = Primer()
		primer.sequence = request.POST.get('seq2').upper()
		primer.direction = request.POST.get('direction2').upper()
		primer.alt_name = request.POST.get('alt_name2')
		if request.POST.get('ngs2') != "":
			primer.ngs_audit_number = request.POST.get('ngs2')
		else:
			primer.ngs_audit_number = None
		today = date.today()
		primer.date_imported = today.strftime("%d/%m/%Y")
		primer.order_status = "Ordered"
		find_imp = Imported_By.objects.filter(imported_by=request.POST.get('imp_by'))
		for f in find_imp:
			primer.imported_by_id = f
		if request.POST.get('version2') == "":
			primer.version = 1
		else:
			primer.version = request.POST.get('version2')
		primer.amplicon_id = Amplicon.objects.all().order_by('-id')[0]
		primer.save()

	if request.POST.get('seq3') != "":
		primer = Primer()
		primer.sequence = request.POST.get('seq3').upper()
		primer.direction = request.POST.get('direction3').upper()
		primer.alt_name = request.POST.get('alt_name3')
		if request.POST.get('ngs3') != "":
			primer.ngs_audit_number = request.POST.get('ngs3')
		else:
			primer.ngs_audit_number = None
		today = date.today()
		primer.date_imported = today.strftime("%d/%m/%Y")
		primer.order_status = "Ordered"
		find_imp = Imported_By.objects.filter(imported_by=request.POST.get('imp_by'))
		for f in find_imp:
			primer.imported_by_id = f
		if request.POST.get('version3') == "":
			primer.version = 1
		else:
			primer.version = request.POST.get('version3')
		primer.amplicon_id = Amplicon.objects.all().order_by('-id')[0]
		primer.save()
	
	return render(request, 'submitted.html')

def order(request):
	imp_by = Imported_By.objects.all()
	context = {
		"imp_by": imp_by
	}
	return render(request, 'order.html', context=context)

def search(request):
	amp_id_input = request.GET.get('amp_id_input', None)
	gen_loc_input = request.GET.get('gen_loc_input', None)
	analysis_input = request.GET.get('analysis_input', None)
	set_input = request.GET.get('set_input', None)
	gene_input = request.GET.get('gene_input', None).upper()
	chr_input = request.GET.get('chr_input', None).upper()
	imp_by_input = request.GET.get('imp_by_input', None).upper()
	date_input = request.GET.get('date_input', None)

	completed_fields = 0
	
	if amp_id_input !="":
		completed_fields +=1
		amp_id_query = Amplicon.objects.get(amplicon_name=amp_id_input)
		primer_amp = amp_id_query.primer_set.all()
	else:
		amp_id_query = ""
		primer_amp =""	

	if gen_loc_input !="":
		completed_fields +=1
		gen_loc_fw_query = Primer.objects.filter(genomic_location_start__lte=gen_loc_input, genomic_location_end__gte=gen_loc_input)
		gen_loc_rev_query = Primer.objects.filter(genomic_location_start__gte=gen_loc_input, genomic_location_end__lte=gen_loc_input)
		gen_loc_query = list(chain(gen_loc_fw_query, gen_loc_rev_query))

	else: 
		gen_loc_query = ""

	if analysis_input !="":
		completed_fields +=1
		analysis_query = Analysis_Type.objects.filter(analysis_type=analysis_input)
		primer_analysis = []
		for a in analysis_query:
			x = a.amplicon_set.all()
			for y in x:
				primer_analysis.append(y.primer_set.all())
	else:
		analysis_query = ""
		primer_analysis = ""

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

	if imp_by_input !="":
		completed_fields +=1
		imp_by_query = Imported_By.objects.filter(imported_by=imp_by_input)
		primer_imp_by = []
		for i in imp_by_query:
			primer_imp_by.append(i.primer_set.all())
	else:
		imp_by_query = ""
		primer_imp_by = ""

	if date_input !="":
		completed_fields +=1
		date_query = Primer.objects.filter(date_imported=date_input)
	else: 
		date_query = ""

	primer_search = []

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

	occurence_count = collections.Counter(primer_search)
	primer_search_results = []
	for primer, count in occurence_count.items():
		if count == completed_fields:
			primer_search_results.append(primer)
	num_primers = len(primer_search_results)
	
	context = {
		'amp_id_query': amp_id_query,
		'primer_amp': primer_amp,
		'gen_loc_query': gen_loc_query,
		'primer_analysis': primer_analysis,
		'primer_set': primer_set,
		'primer_gene': primer_gene,
		'primer_chr': primer_chr,
		'primer_imp_by' : primer_imp_by,
		'date_query': date_query,
		'primer_search': primer_search,
		'occurence_count': occurence_count,
		'primer_search_results': primer_search_results,
		'num_primers': num_primers,
	}

	return render(request, 'search.html', context=context)

def primer(request):
	primer_input = request.GET.get('selected_primer', None)
	if primer_input != "":
		primer = Primer.objects.get(id=primer_input)
	else:
		primer = ""
	imp_by = Imported_By.objects.all()
	context = {
		'primer_input': primer_input,
		'primer':primer,
		'imp_by':imp_by
	}

	return render(request, 'primer.html', context=context)
	
def amplicon(request):
	amplicon_input = request.GET.get('selected_amplicon', None)
	amplicon = Amplicon.objects.get(amplicon_name=amplicon_input)
	primer = amplicon.primer_set.all()
	context = {
		'amplicon': amplicon,
		'primer': primer
	}

	return render(request, 'amplicon.html', context=context)

def ordered(request):
	ordered = Primer.objects.filter(order_status = "Ordered")
	context = {
		"ordered": ordered
	}

	return render(request, 'ordered.html', context=context)

def order_to_amplicon(request): 
	pulled = Amplicon.objects.filter(pk=request.POST.get('amplicon'))
	imp_by = Imported_By.objects.all()
	context = {
	'pulled':pulled,
        'imp_by':imp_by
	}
	return render(request, 'order_to_amplicon.html', context=context)

def submitted_to_amplicon(request):
	primer = Primer()
	primer.sequence = request.POST.get('seq').upper()
	primer.direction = request.POST.get('direction').upper()
	primer.alt_name = request.POST.get('alt_name')
	if request.POST.get('ngs') != "":
		primer.ngs_audit_number = request.POST.get('ngs')
	else:
		primer.ngs_audit_number = None
	today = date.today()
	primer.date_imported = today.strftime("%d/%m/%Y")
	primer.order_status = "Ordered"
	find_imp = Imported_By.objects.filter(imported_by=request.POST.get('imp_by'))
	for f in find_imp:
		primer.imported_by_id = f
	if request.POST.get('version') == "":
		primer.version = 1
	else:
		primer.version = request.POST.get('version')
	amp = Amplicon.objects.filter(pk=request.POST.get('amplicon'))
	for a in amp:
		primer.amplicon_id = a
	primer.save()
	context = {
		'amp':amp
	}
	
	return render(request, 'submitted_to_amplicon.html', context=context)

def reorder_primer(request):
	reorder = Primer.objects.get(pk=request.POST.get('primer'))
	primer = Primer()
	primer.sequence = reorder.sequence
	primer.direction = reorder.direction
	primer.alt_name = reorder.alt_name
	primer.ngs_audit_number = reorder.ngs_audit_number
	find_imp = Imported_By.objects.filter(imported_by=request.POST.get('imp_by'))
	for f in find_imp:
		primer.imported_by_id = f	
	today = date.today()
	primer.date_imported = today.strftime("%d/%m/%Y")
	primer.order_status = "Ordered"
	primer.version = reorder.version
	primer.amplicon_id = reorder.amplicon_id
	primer.save()
	
	context = {
		'reorder':reorder
	}
	
	return render(request, 'submitted_reorder_primer.html', context=context)

def archive_primer(request):
	archive = Primer.objects.get(pk=request.POST.get('archive'))
	archive.order_status = 'Archived'
	find_arc = Imported_By.objects.filter(imported_by=request.POST.get('arc_by'))
	for f in find_arc:
		archive.archived_by = f
	today = date.today()
	archive.date_archived = today.strftime("%d/%m/%Y")
	archive.reason_archived = request.POST.get('reason_archived')
	archive.save()
	
	context = {
		'archive':archive
	}
	
	return render(request, 'archive_primer.html', context=context)


	


