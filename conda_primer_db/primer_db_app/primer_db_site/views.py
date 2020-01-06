from django.shortcuts import render, get_object_or_404
from .models import Primer, Amplicon, Analysis_Type, Imported_By, Gene, Primer_Set
from itertools import chain
from collections import Counter
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

def search(request):
	amp_id_input = request.GET.get('amp_id_input', None)
	gen_loc_input = request.GET.get('gen_loc_input', None)
	analysis_input = request.GET.get('analysis_input', None)
	set_input = request.GET.get('set_input', None)
	gene_input = request.GET.get('gene_input', None)
	chr_input = request.GET.get('chr_input', None)
	imp_by_input = request.GET.get('imp_by_input', None)
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
		gen_loc_fw_query = Amplicon.objects.filter(genomic_location_start__lte=gen_loc_input, genomic_location_end__gte=gen_loc_input)
		gen_loc_rev_query = Amplicon.objects.filter(genomic_location_start__gte=gen_loc_input, genomic_location_end__lte=gen_loc_input)
		gen_loc_query = list(chain(gen_loc_fw_query, gen_loc_rev_query))
		primer_gene_loc = []
		for g in gen_loc_query:
			primer_gene_loc.append(g.primer_set.all())

	else: 
		gen_loc_query = ""
		primer_gene_loc = ""

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
	for g in primer_gene_loc:
		for x in g:
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
	for i in primer_imp_by:
		primer_search.append(i)
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
		'primer_gene_loc': primer_gene_loc,
		'primer_analysis': primer_analysis,
		'primer_set': primer_set,
		'primer_gene': primer_gene,
		'primer_chr': primer_chr,
		'primer_imp_by' : primer_imp_by,
		'date_query': date_query,
		'primer_search': primer_search,
		'occurence_count': occurence_count,
		'primer_search_results': primer_search_results,
		'num_primers': num_primers
	}

	return render(request, 'search.html', context=context)

def primer(request):
	primer_input = request.GET.get('selected_primer', None)
	amplicon = Amplicon.objects.get(amplicon_name=primer_input)
	context = {
		'amplicon': amplicon,
		'primer_input': primer_input
	}

	return render(request, 'primer.html', context=context)
	



	


