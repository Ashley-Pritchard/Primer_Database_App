#views - each function takes a web request and returns a web response. The web app has search bar at the top - the below requests have been ordered into respecitive pages and their derivatives.

#import relevant libraries
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.contrib import messages
from .models import *
from .forms import *
from itertools import chain
from collections import Counter
from datetime import date
import glob
import collections
import csv

LOGINURL = settings.LOGIN_URL

#used in user_passes_test decorator to check if someone if logged in
def is_logged_in(user):
    return user.is_active

def loginview(httprequest):
    if httprequest.user.is_authenticated:
        logout(httprequest)
        messages.success(httprequest,"You are now logged out")
        return HttpResponseRedirect(reverse("index"))
    else:
        if httprequest.method == "POST" and "login" in httprequest.POST:
            form = LoginForm(httprequest.POST)
            if form.is_valid():
                user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
                if user is not None and user.is_active:
                    login(httprequest, user)
                    return HttpResponseRedirect(reverse("index"))

                else:
                    try:
                        User.objects.get(username=form.cleaned_data["username"])
                        messages.success(httprequest, "Incorrect password entered")
                    except:
                        messages.success(httprequest, f'User {form.cleaned_data["username"]} does not exist')
            else:
                pass

        else:
            form = LoginForm()
    return render(httprequest, "login.html", {"form": form})

@user_passes_test(is_logged_in, login_url=LOGINURL)
def change_password(httprequest):
    if httprequest.method == 'POST':
        form = PasswordChangeForm(httprequest.user, httprequest.POST)
        if form.is_valid():
            if form.cleaned_data["old_password"]==form.cleaned_data["new_password1"]:
                messages.success(httprequest, 'Your password new password cannot be your old password')
                return HttpResponseRedirect(reverse("change_password"))
            user = form.save()
            update_session_auth_hash(httprequest, user)  # Important!
            return HttpResponseRedirect(reverse("index"))
        else:
            errors=[]
            for v in form.errors.values():
                errors+=[str(v[0]).strip('<ul class="errorlist"><li><\lie></').replace("didn't", "do not")]
            messages.success(httprequest, (" ".join(errors)))
    else:
        form = PasswordChangeForm(httprequest.user)
    submiturl = reverse("change_password")
    cancelurl = reverse("index")
    context={"form": form, "heading":"Change Password for {}".format(httprequest.user),
             "submiturl": submiturl, "cancelurl": cancelurl}

    return render(httprequest, "pwform.html", context)

## Search Page ##


#provides context for the index / search page - takes request from users clicking on the 'search' option of the searchbar
@user_passes_test(is_logged_in, login_url=LOGINURL)
def index(request):
    if request.method=="POST":
        if "submit" not in request.POST:
            return HttpResponseRedirect(reverse("index"))
        else:
            form = IndexSearchForm(request.POST)
            if form.is_valid():
                queries = []
                for key, query in [("Amplicon_ID", "amplicon_id__amplicon_name__icontains"), ("Chromosome", "amplicon_id__gene_id__chromosome__exact"),
                                    ("Primer_Set", "amplicon_id__primer_set_id__primer_set__exact"),("Gene", "amplicon_id__gene_id__gene_name__exact"),
                                   ("Analysis_Type", "amplicon_id__analysis_type_id__analysis_type__exact"), ("Alt_Name","alt_name__icontains"),
                                  ]:
                    val = form.cleaned_data[key]
                    if val:
                        queries += ["{}={}".format(query, val)]
                return HttpResponseRedirect(reverse("search", args=[";".join(queries)]))
    else:
        form=IndexSearchForm()
    submiturl = reverse("index")
    cancelurl = reverse("index")
    #pull the count of primers, amplicons and genes
    num_primers = Primer.objects.all().count()
    num_amplicons = Amplicon.objects.all().count()
    num_genes = Gene.objects.all().count()
    header="Primer Database: Search and Reorders"
    subheader=f"Welcome to the Primer Database for the OUH Molecular Genetics Laboratory. We currently have <strong>{num_primers}</strong> primers covering <strong>{num_amplicons}</strong> amplicons and <strong>{num_genes}</strong> genes. Fill in one or more boxes in the form below to search for primers: "
    #assign pulled information as context for the page
    context = {
        "header": header,
    	"subheader": subheader,
        "form": form,
        "submiturl": submiturl,
        "cancelurl": cancelurl,
    }

    #returns the index html page from the templates directory
    return render(request, 'form.html', context=context)





#takes the users search terms from the index /search page as the request and queries the database to pull matching primers
@user_passes_test(is_logged_in, login_url=LOGINURL)
def search(request,filters):

    header="Primer Database: Search Results"

    query = dict([q.split("=") for q in filters.split(";")])
    primers=Primer.objects.filter(**query)

    if len(primers)>0:
        headings = ["Amplicon ID", "Primer ID", "Alt Name", "Location", "Comments"]
        subheader = f"Your search returned <strong>{len(primers)}</strong> results. Click on the Amplicon ID for full information about individual primers or primer sets."
        body=[]
        for p in primers:
            values=[p.amplicon_id.amplicon_name,
                    p.name,
                    p.alt_name,
                    p.location,
                    p.comments,
                    ]
            #THIS WILL NEED CHANGING WHEN AMPLICON PAGE GETS UPDATED TO NEW STYLE
            urls=[reverse("amplicon",args=[p.amplicon_id.amplicon_name]),
                  "",
                  "",
                  "",
                  "",
                  ]
            body.append(zip(values,urls))
    else:
        subheader = "Your search returned <strong>0</strong> results"
    #ADD IN GO DIRECT TO PAGE IF ONLY ONE RESULT
    if len(primers)==1:
        print("ONLY 1")

    context = {
        "header": header,
        "subheader": subheader,
        "headings":headings,
        "body": body,
    }

    #render the search html page from templates directory
    return render(request, 'search.html', context=context)





#from the search results page, takes user clicking on specific amplicon as request and pulls respective primer information for those matching the amplicon id
@user_passes_test(is_logged_in, login_url=LOGINURL)
def amplicon(request,amplicon_input):

	#pull information for the amplicon selected by the user from the database
	amplicon = Amplicon.objects.get(amplicon_name=amplicon_input)

	#pull primer information for amplicon
	primer = amplicon.primer_set.all()

	#the rendered primer page will permit the reorder of the primer - this requires input of who is ordering - pull imported_by names from the database for drop-down menu
	imp_by = Imported_By.objects.all()

	#provide a count of stocked primers as context for the page
	count_stocked = 0
	for p in primer:
		if p.order_status != 'Stocked':
			count_stocked += 1


	#provide context for the amplicon html page
	context = {
		'amplicon': amplicon,
		'primer': primer,
		'imp_by': imp_by,
		'count_stocked': count_stocked
	}

	#render the amplicon html page from the templates directory
	return render(request, 'amplicon.html', context=context)





#from the amplicon search result pages, the user can reorder a primer - function takes input of the user clicking 'reorder primer' as request.(Note that the archive in name is left over from a removed option to enable archiving primers)
@user_passes_test(is_logged_in, login_url=LOGINURL)
def reorder_archive_primer(request):

	#if user selects 'reorder primer'
	if 'reorder' in request.POST:

		#pull specific primer(s) from the database
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
				primer.modification_5 = reorder.modification_5
				primer.alt_name = reorder.alt_name
				primer.ngs_audit_number = reorder.ngs_audit_number
				primer.version = reorder.version
				primer.amplicon_id = reorder.amplicon_id
				primer.comments = reorder.comments
				primer.location = reorder.location
				primer.date_testing_completed = reorder.date_testing_completed
				primer.m13_tag = reorder.m13_tag


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

				#close the current primer record
				reorder.order_status = "Closed"
				reorder.save()

				#update the database
				primer.save()

			#render the 'submitted reorder primer' html page from the templates directory
			return render(request, 'submitted_reorder_primer.html')

		#if primer was not selected
		else:

			#render the 'warning' html page from the templates directory
			return render(request, 'warning.html')





##Order Primer Page ##


#provides context for the order page - takes request from users clicking on the 'order new gene/version' option of the searchbar
@user_passes_test(is_logged_in, login_url=LOGINURL)
def order(request):
	#renders the 'order' html page from the templates directory
	return render(request, 'order.html')





#from the order page, takes user input of how many primers they wish to order as request
@user_passes_test(is_logged_in, login_url=LOGINURL)
def order_form(request):

	#pull number of primers user selected for ordering as a range
	number = list(range(0, int(request.GET.get('number'))))

	#pull imported by options from database to present as dropdown menu
	imp_by = Imported_By.objects.all()
	analysis_type = Analysis_Type.objects.all()
	primer_set = Primer_Set.objects.all()

	#provide as context for the order form html page
	context = {
		"imp_by": imp_by,
		"number":number,
		"analysis_type":analysis_type,
		"primer_set": primer_set,
	}

	#render the order html page from the templates directory
	return render(request, 'order_form.html', context=context)





#from the order form page, takes submission of new primer(s) as request
#function one of three - separated as the first two make changes to the database required for the third
#function 1 - adds a new gene to the database if the requested primer is in a gene not currently stored
@user_passes_test(is_logged_in, login_url=LOGINURL)
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
@user_passes_test(is_logged_in, login_url=LOGINURL)
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
	elif request.POST.get('analysis_type') == 'Probe':
		new_amplicon = 'Probe' + '_' + request.POST.get('gene') + '-' + request.POST.get('exon')

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
@user_passes_test(is_logged_in, login_url=LOGINURL)
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
			modification_3 = '3\'' + mod_3[i].upper()
		else:
			modification_3 = mod_3[i].upper()
		if mod_5[i] != "":
			modification_5 = '5\'' + mod_5[i].upper()
		else:
			modification_5 = mod_5[i].upper()

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
		elif request.POST.get('analysis_type') == 'Taqman':
			new_primer = 'TQ_' + request.POST.get('gene') + '-' + request.POST.get('gene') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'Pyrosequencing':
			new_primer = 'P_' + request.POST.get('gene') + '-' + request.POST.get('gene') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'ARMS: Mutant':
			new_primer = 'ARMS_M_' + request.POST.get('gene') + '-' + request.POST.get('exon') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'ARMS: Normal':
			new_primer = 'ARMS_N_' + request.POST.get('gene') + '-' + request.POST.get('exon') + '___' + direction[i].upper() + '_' + modification_3 + '_' + modification_5
		elif request.POST.get('analysis_type') == 'Probe':
			new_primer = 'Probe_' + request.POST.get('gene') + '-' + request.POST.get('exon') + '___' + direction[i].upper() + '_' + modification_3 + '_' + '_' + modification_5

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
		primer.modification = mod_3[i].upper()
		primer.modification_5 = mod_5[i].upper()
		primer.alt_name = alt_name[i]
		primer.comments = comments[i]
		primer.reason_ordered = reason[i]
		primer.version = version
		primer.name = str(new_primer) + '_v' + str(version)

		#if requested, add m13 tag as either forward or reverse
		if request.POST.get('analysis_type') == 'Sanger' and direction[i] == 'f':
			primer.m13_tag = 'GATAAACGACGGCCAGT'
		elif request.POST.get('analysis_type') == 'Sanger' and direction[i] == 'r':
			primer.m13_tag = 'CAGGAAACAGCTATGAC'
		elif m13[i] == "yes" and direction[i] == "f":
			primer.m13_tag = "GATAAACGACGGCCAGT"
		elif m13[i] == "yes" and direction[i] == "r":
			primer.m13_tag = "CAGGAAACAGCTATGAC"
		else:
			primer.m13_tag = ""

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
		elif request.POST.get('analysis_type') == 'Pyrosequencing':
			amplicon_name = 'P_' + request.POST.get('gene') + '-' + request.POST.get('exon')
		elif request.POST.get('analysis_type') == 'ARMS: Mutant':
			amplicon_name = 'ARMS_M_' + request.POST.get('gene') + '-' + request.POST.get('exon')
		elif request.POST.get('analysis_type') == 'ARMS: Normal':
			amplicon_name = 'ARMS_N_' + request.POST.get('gene') + '-' + request.POST.get('exon')
		elif request.POST.get('analysis_type') == 'Probe':
			amplicon_name = 'Probe_' + request.POST.get('gene') + '-' + request.POST.get('exon')
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
@user_passes_test(is_logged_in, login_url=LOGINURL)
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
@user_passes_test(is_logged_in, login_url=LOGINURL)
def submit_order(request):

	#pull the selected primers based on the checkboxes selected on the 'primers to be ordered' html page
	primer_list = request.POST.getlist('primer')

	#if the 'download order information' button is clicked, provide a pop up for accepting the download of a csv file
	if 'csv' in request.POST:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="order_information.csv"'

		#write the relevant primer information to a csv file
		writer = csv.writer(response)
		writer.writerow(['name', 'sequence', '3\' modification', '5\' modification', 'location', 'reason_for_order', 'date received'])
		for primer in primer_list:
			export = Primer.objects.get(pk=primer)
			if export.m13_tag != 'None':
				writer.writerow([export.name, export.m13_tag + export.sequence, export.modification, export.modification_5, export.location, export.reason_ordered])
			else:
				writer.writerow([export.name, export.sequence, export.modification, export.modification_5, export.location, export.reason_ordered])

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
@user_passes_test(is_logged_in, login_url=LOGINURL)
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
@user_passes_test(is_logged_in, login_url=LOGINURL)
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

		#return the order recieved html page from the templates directory
		return render(request, 'order_recieved.html')

	#if 'testing required non sanger' is clicked - iterate through the list of primers selected, update the order to 'in testing non sanger',assign the 'date order received' as todays date and save changes to the database
	if 'test_non_sanger' in request.POST:
		for i in range(list_len):
			recieved = Primer.objects.get(pk=primer_list[i])
			recieved.order_status = 'In Testing Non-Sanger'
			today = date.today()
			recieved.date_order_recieved = today.strftime("%d/%m/%Y")
			recieved.save()

		#return the order recieved html page from the templates directory
		return render(request, 'order_recieved.html')

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

		#instead render the 'order recieved' html page from the templates directory - this will direct users to update lab location for these primers as they are being moved to 'stocked'
		return render(request, 'order_recieved_non_test.html', context=context)




#for primers submitted as recieved, update the location information
@user_passes_test(is_logged_in, login_url=LOGINURL)
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
@user_passes_test(is_logged_in, login_url=LOGINURL)
def in_testing_sanger(request):

	#pull primers with order status of in testing and analysis type of sanger
	testing = Primer.objects.filter(order_status = "In Testing Sanger")

	#provide context for the in testing: sanger html page
	context = {
		"testing": testing
	}

	#render the in testing: sanger html page from the templates directory
	return render(request, 'in_testing_sanger.html', context=context)




#takes user clicking the 'in testing: non sanger' searchbar link as request and pulls information of all non sanger primers in testing
@user_passes_test(is_logged_in, login_url=LOGINURL)
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
@user_passes_test(is_logged_in, login_url=LOGINURL)
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

	#repeat for location
	location_list = request.POST.getlist('location')

	list_len_loc = len(location_list)
	for i in range(list_len_loc):
		update_loc = Primer.objects.get(pk=all_primer_list[i])
		if location_list[i] != "":
			update_loc.location = location_list[i]
		update_loc.save()

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
@user_passes_test(is_logged_in, login_url=LOGINURL)
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
@user_passes_test(is_logged_in, login_url=LOGINURL)
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
@user_passes_test(is_logged_in, login_url=LOGINURL)
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
@user_passes_test(is_logged_in, login_url=LOGINURL)
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

	#repeat for location
	location_list = request.POST.getlist('location')

	list_len_loc = len(location_list)
	for i in range(list_len_loc):
		update_loc = Primer.objects.get(pk=all_primer_list[i])
		if location_list[i] != "":
			update_loc.location = location_list[i]
		update_loc.save()

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
	if 'not' in request.POST:
		for primer in primer_list:
			tested = Primer.objects.get(pk=primer)
			tested.order_status = 'Failed_Validation_Archived'
			today = date.today()
			tested.date_retesting_completed = today.strftime("%d/%m/%Y")
			tested.save()

	#render the  'tested' html page from the templates directory
	return render(request, 'tested.html')
