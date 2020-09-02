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
    context={"header":header}
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
            context.update({"headings":headings, "body": body, "subheader":subheader})
    else:
        subheader = "Your search returned <strong>0</strong> results"
        context.update({"subheader":subheader})
    #ADD IN GO DIRECT TO PAGE IF ONLY ONE RESULT
    if len(primers)==1:
        return HttpResponseRedirect(reverse("amplicon",args=[primers[0].amplicon_id.amplicon_name]))

    #render the search html page from templates directory
    return render(request, 'search.html', context=context)





#from the search results page, takes user clicking on specific amplicon as request and pulls respective primer information for those matching the amplicon id
@user_passes_test(is_logged_in, login_url=LOGINURL)
def amplicon(request,amplicon_input):
    #pull information for the amplicon selected by the user from the database
    amplicon = Amplicon.objects.get(amplicon_name=amplicon_input)
    #pull primer information for amplicon
    primer = amplicon.primer_set.all()
    header=f"Primer Database: Amplicon {amplicon.amplicon_name}"
    subheader=f"The following page provides a record of all OMGL primers associated with amplicon {amplicon.amplicon_name}. To <strong>reorder</strong> one or more of the below primers, <strong>select the box</strong> next to the primer and use the 'reorder' option at the bottom of the page."

    form=AmpliconOrderForm
    if request.method == "POST":
        form=form(request.POST)
        if "submit" not in request.POST or request.POST["submit"] != "save":
            return HttpResponseRedirect(reverse("amplicon", args=[amplicon.amplicon_name]))
        else:
            reorder_list = request.POST.getlist("requests")
            if reorder_list==[]:
                return HttpResponseRedirect(reverse("reorder_archive_primer",args=[0,amplicon.amplicon_name]))
            #May come back to tidy up if time...
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
                primer.imported_by_id = request.user

                #assign the 'date imported' to the new primer record as todays date
                today = date.today()
                primer.date_imported = today
                primer.date_order_placed = today

                #assign the order status of the new primer record to 'ordered'
                primer.order_status = "Ordered"

                #add reason reordered input by user to the primer record
                primer.reason_ordered = form.data["reason"]

                #close the current primer record
                reorder.order_status = "Closed"
                reorder.save()

                #update the database
                primer.save()
            return HttpResponseRedirect(reverse("reorder_archive_primer", args=[1,amplicon.amplicon_name]))
        return HttpResponseRedirect(reverse("amplicon", args=[amplicon.amplicon_name]))
    else:
        form=form()

        #list of heading (text) and primer attribute tuples. primer attr will be used to eval the actual attribute in a loop
        #e.g in headings[0] the title is "Primer" and the attr is "name" (e.g primer.name)
        in_stock_headings=[("Primer","name"), ("Order Status","order_status"), ("Analysis","amplicon_id.analysis_type_id.analysis_type"),
                  ("Gene", "amplicon_id.gene_id.gene_name"), ("Chromosome","amplicon_id.gene_id.chromosome"), ("Exon","amplicon_id.exon"),
                  ("Direction","direction"), ("Start","genomic_location_start"), ("End","genomic_location_end"),
                  ("Set","amplicon_id.primer_set_id.primer_set"), ("Location","location"), ("Sequence", "sequence"),
                  ("NGS Audit Number","ngs_audit_number"), ("Requested By", "imported_by_id.username"), ("Date Imported","date_imported"),
                  ("Amplicon Name", "amplicon_id.amplicon_name"), ("Alternative Name", "alt_name"), ("m13 tag", "m13_tag"),
                  ("3' Modification", "modification"), ("5' Modification","modification_5"), ("Version", "version"),
                  ("Reason Ordered","reason_ordered"), ("Comments","comments"), ("Date Testing Completed","date_testing_completed")]
        non_stock_headings=in_stock_headings[:-1]
        stocked_body, non_stocked_body=[],[]
        for p in primer:
            temp_body=[]
            if p.order_status=="Stocked":
                for h in in_stock_headings:
                    temp_body.append((h[0],eval(f"p.{h[1]}")))
                stocked_body.append((temp_body,p.id,p.name))
            else:
                for h in non_stock_headings:
                    temp_body.append((h[0],eval(f"p.{h[1]}")))
                if p.order_status=="Archived":
                    temp_body.append(("Date Archived",p.date_archived))
                non_stocked_body.append(temp_body)

        #provide context for the amplicon html page
        context = {
            'header': header,
            'subheader': subheader,
            "stocked_body":stocked_body,
            "non_stocked_body":non_stocked_body,
            "form":form,
            "url":reverse("amplicon", args=[amplicon.amplicon_name]),
            "cancelurl": reverse("amplicon",args=[amplicon.amplicon_name]),
        }

        #render the amplicon html page from the templates directory
        return render(request, 'amplicon.html', context=context)





#from the amplicon search result pages, the user can reorder a primer - function takes input of the user clicking 'reorder primer' as request.(Note that the archive in name is left over from a removed option to enable archiving primers)
@user_passes_test(is_logged_in, login_url=LOGINURL)
def reorder_archive_primer(request,success,amplicon):
    if success=="1":
        return render(request, "action_completed.html")
	#if primer was not selected
    elif success=="0":

    #render the 'warning' html page from the templates directory
        return render(request, 'warning.html', context={"message":"please click here to go back to reorder a primer",
                                                "url":f"/primer_database/amplicon/{amplicon}"})








#provides context for the order page - takes request from users clicking on the 'order new gene/version' option of the searchbar
@user_passes_test(is_logged_in, login_url=LOGINURL)
def order(request):
    header="Primer Database: New Primer Order"
    subheader="The following form facilitates the ordering of one or more <strong>new</strong> primers associated with a <strong>single amplicon set</strong>. To <strong>reorder</strong> a primer, please first use the <a class='active' href='/primer_database/'>search</a> function and then follow the appropriate links."
    form = NewPrimerOrderForm
    if request.method=="POST":
        if "submit" not in request.POST:
            return HttpResponseRedirect(reverse("order"))
        else:
            form = form(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse("order_form", args=[form.data["number"]]))
    else:
        form=form()
    submiturl = reverse("order")
    cancelurl = reverse("order")
    context = {
        "header": header,
        "subheader": subheader,
        "form": form,
        "submiturl": submiturl,
        "cancelurl": cancelurl,
    }
    return render(request, 'form.html', context=context)



#from the order page, takes user input of how many primers they wish to order as request
@user_passes_test(is_logged_in, login_url=LOGINURL)
def order_form(request,number):
    header="Primer Database: New Primer Order Form"
    subheader="Fill in the amplicon information first, then complete the tables for each of your primers. Required fields are marked with *."
    amplicon_form=OrderFormAmplicon
    primer_form=OrderFormPrimer
    if request.method=="POST":
        amplicon_form = amplicon_form(request.POST)
        primer_form = primer_form(request.POST)
        #have to error check this one here as it relies on values from both forms
        if Analysis_Type.objects.get(id=amplicon_form.data["analysis_type"]).analysis_type=="NGS":
            for audit_no in primer_form.data.getlist("ngs_number"):
                if audit_no=="":
                    primer_form.add_error("ngs_number","If amplicon type is NGS an audit number must be entered")
        if amplicon_form.is_valid() and primer_form.is_valid():
            genes = Gene.objects.filter(gene_name__icontains=amplicon_form.data["gene"], chromosome=amplicon_form.data["chromosome"])

            #if the submitted gene is not in the gene list, add the gene and respective chromosome to the database
            if genes.first() is None:
                gene = Gene()
                gene.gene_name = amplicon_form.data["gene"].upper()
                gene.chromosome = amplicon_form.data["chromosome"].upper()
                gene.save()
            else:
                gene=genes.first()

            analysis_type=Analysis_Type.objects.get(id=amplicon_form.data["analysis_type"])
            for i in range(0,int(number)):
                if analysis_type.analysis_type == 'Sanger':
                    new_amplicon = str(Primer_Set.objects.get(id=amplicon_form.data["primer_set"])) + '_' + gene.gene_name + '-' + amplicon_form.data["exon"]
                elif analysis_type.analysis_type == 'NGS':
                    new_amplicon = str(Primer_Set.objects.get(id=amplicon_form.data["primer_set"])) + '_' + gene.gene_name + '_NGS-' + primer_form.data.getlist("ngs_number")[i]
                elif analysis_type.analysis_type == 'Light Scanner':
                    new_amplicon = 'LS' + '_' + gene.gene_name + '-' + amplicon_form.data["exon"]
                elif analysis_type.analysis_type == 'MLPA':
                    new_amplicon = 'ML' + '_' + gene.gene_name + '-' + amplicon_form.data["exon"]
                elif analysis_type.analysis_type == 'Fluorescent':
                    new_amplicon = 'GM' + '_' + gene.gene_name + '-' + amplicon_form.data["exon"]
                elif analysis_type.analysis_type == 'Long Range':
                    new_amplicon = 'LR' + '_' + gene.gene_name + '-' + amplicon_form.data["exon"]
                elif analysis_type.analysis_type == 'RT-PCR':
                    new_amplicon = 'RT' + '_' + gene.gene_name + '-' + amplicon_form.data["exon"]
                elif analysis_type.analysis_type == 'Taqman':
                    new_amplicon = 'TQ' + '_' + gene.gene_name + '-' + amplicon_form.data["exon"]
                elif analysis_type.analysis_type == 'Pyrosequencing':
                    new_amplicon = 'P' + '_' + gene.gene_name + '-' + amplicon_form.data["exon"]
                elif analysis_type.analysis_type == 'ARMS: Mutant':
                    new_amplicon = 'ARMS_M' + '_' + gene.gene_name + '-' + amplicon_form.data["exon"]
                elif analysis_type.analysis_type == 'ARMS: Normal':
                    new_amplicon = 'ARMS_N' + '_' + gene.gene_name + '-' + amplicon_form.data["exon"]
                elif analysis_type.analysis_type == 'Probe':
                    new_amplicon = 'Probe' + '_' + gene.gene_name + '-' + amplicon_form.data["exon"]
                amplicons=Amplicon.objects.filter(amplicon_name=new_amplicon)
                if amplicons.first() is None:
                    amplicon = Amplicon()
                    #assign name as created above
                    amplicon.amplicon_name = new_amplicon

                    #set exon based on form submission
                    amplicon.exon = amplicon_form.data["exon"]

                    amplicon.analysis_type_id=analysis_type

                    amplicon.gene_id=gene

                    amplicon.primer_set_id=Primer_Set.objects.get(id=amplicon_form.data["primer_set"])
                    amplicon.save()
                else:
                    amplicon=amplicons.first()



                seq=primer_form.data.getlist("sequence")[i]
                direction=primer_form.data.getlist("direction")[i]
                start = primer_form.data.getlist('start')[i]
                end = primer_form.data.getlist('end')[i]
                m13 = primer_form.data.getlist('m13')[i]
                mod_3 = ('3\'' + primer_form.data.getlist('prime3')[i]) if primer_form.data.getlist('prime3')[i] is not "" else ""
                mod_5 = ('5\'' + primer_form.data.getlist('prime5')[i]) if primer_form.data.getlist('prime5')[i] is not "" else ""
                ngs = primer_form.data.getlist('ngs_number')[i]
                alt_name = primer_form.data.getlist('alt_name')[i]
                comments = primer_form.data.getlist('comments')[i]
                reason = primer_form.data.getlist('reason')[i]

                if analysis_type.analysis_type == 'Sanger':
                    new_primer = str(amplicon) + '___' + direction + '_' + mod_3 + '_' + mod_5
                elif analysis_type.analysis_type == 'NGS':
                    new_primer = str(amplicon) + '___' + direction + '_' + mod_3 + '_' + mod_5
                elif analysis_type.analysis_type == 'Light Scanner':
                    new_primer = str(amplicon) + '___' + direction + '_' + mod_3 + '_' + mod_5
                elif analysis_type.analysis_type == 'MLPA':
                    new_primer = str(amplicon) + '___' + direction + '_' + mod_3 + '_' + mod_5
                elif analysis_type.analysis_type == 'Fluorescent':
                    new_primer = str(amplicon) + '___' + direction + '_' + mod_3 + '_' + mod_5
                elif analysis_type.analysis_type == 'Long Range':
                    new_primer = str(amplicon) + '___' + direction + '_' + mod_3 + '_' + mod_5
                elif analysis_type.analysis_type == 'RT-PCR':
                    new_primer = str(amplicon) + '___' + direction + '_' + mod_3 + '_' + mod_5
                elif analysis_type.analysis_type == 'Taqman':
                    new_primer = str(amplicon) + '___' + direction + '_' + mod_3 + '_' + mod_5
                elif analysis_type.analysis_type == 'Pyrosequencing':
                    new_primer = str(amplicon) + '___' + direction + '_' + mod_3 + '_' + mod_5
                elif analysis_type.analysis_type == 'ARMS: Mutant':
                    new_primer = str(amplicon) + '___' + direction + '_' + mod_3 + '_' + mod_5
                elif analysis_type.analysis_type == 'ARMS: Normal':
                    new_primer = str(amplicon) + '___' + direction + '_' + mod_3 + '_' + mod_5
                elif analysis_type.analysis_type == 'Probe':
                    new_primer = str(amplicon) + '___' + direction + '_' + mod_3 + '_' + '_' + mod_5


                matching_primers=Primer.objects.filter(name__icontains=new_primer)
                version_count = 0
                version_number = []
                version = ()
                for p in matching_primers:
                    version_number.append(p.version)
                    #if sequecen matches, close current primer and assign same version number
                    if p.sequence == seq.upper():
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
                primer = Primer()
                primer.sequence = seq.upper()
                primer.direction = direction.upper()
                primer.modification = mod_3.upper()
                primer.modification_5 = mod_5.upper()
                primer.alt_name = alt_name
                primer.comments = comments
                primer.reason_ordered = reason
                primer.version = version
                primer.name = str(new_primer) + '_v' + str(version)

                if analysis_type.analysis_type == 'Sanger' and direction.upper() == 'F':
                    primer.m13_tag = 'GATAAACGACGGCCAGT'
                elif request.POST.get('analysis_type') == 'Sanger' and direction.upper() == 'R':
                    primer.m13_tag = 'CAGGAAACAGCTATGAC'
                elif m13 == "yes" and direction.upper() == "F":
                    primer.m13_tag = "GATAAACGACGGCCAGT"
                elif m13 == "yes" and direction.upper() == "R":
                    primer.m13_tag = "CAGGAAACAGCTATGAC"
                else:
                    primer.m13_tag = ""
                primer.date_imported=date.today()
                primer.order_status="Ordered"
                primer.imported_by_id=request.user
                primer.amplicon_id=amplicon
                primer.save()
        if "quit" in request.POST:
            return render(request, "submitted.html")
        elif "reorder" in request.POST:
            return HttpResponseRedirect(reverse("order"))

    else:
        amplicon_form=amplicon_form()
        primer_form=primer_form()
    submiturl = reverse("order_form",args=[number])
    cancelurl = reverse("order_form",args=[number])
    context = {
        "header":header,
        "subheader":subheader,
        "number":[i for i in range(0,int(number))],
        "amplicon_form": amplicon_form,
        "primer_form":primer_form,
        "submiturl": submiturl,
        "cancelurl": cancelurl,
	}

    #render the order html page from the templates directory
    return render(request, 'order_form.html', context=context)

## Primers to be Ordered Page ##


#takes user clicking the 'primers on order' searchbar link as request and pulls the information of all primers with an order status of 'ordered'
@user_passes_test(is_logged_in, login_url=LOGINURL)
def ordered(request):
    if request.method == "POST":
        primer_list = Primer.objects.filter(id__in=request.POST.getlist('primers'))
        if len(primer_list)!=0:
            if "csv" in request.POST:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="order_information.csv"'

                #write the relevant primer information to a csv file
                writer = csv.writer(response)
                writer.writerow(['name', 'sequence', '3\' modification', '5\' modification', 'location', 'reason_for_order', 'date received'])
                for primer in primer_list:
                    writer.writerow([primer.name, (primer.m13_tag + primer.sequence) if primer.m13_tag is not None else primer.sequence, primer.modification, primer.modification_5, primer.location, primer.reason_ordered])

                #export the csv file
                return response
            elif 'ordered' in request.POST:
                for primer in primer_list:
                    primer.order_status = 'Order Placed'
                    primer.date_order_placed = date.today()
                    primer.save()
                return render(request, 'action_completed.html')
            #if the 'delete' button is clicked - iterate through the list of primers selected and delete from the database
            elif 'delete' in request.POST:
                for primer in primer_list:
                    primer.delete()
                return render(request, 'action_completed.html')
        else:
            return render(request, 'warning.html', context={"message":"please click here to go back to the Primers to be Ordered page",
                                                    "url":"/primer_database/ordered/"})
    else:
        header="Primer Database: Primers to be Ordered"
        subheader="Primer information for primers to be order:"
        #pull primers with order status of ordered
        headers=["Primer ID", "Requested By", "Comments", "Select"]
        values=[]
        ids=[]
        ordered = Primer.objects.filter(order_status = "Ordered")
        for primer in ordered:
            values.append([primer.name,
                          primer.imported_by_id.username,
                          primer.comments,
                          ])
            ids.append(primer.id)
        #provide context for the ordered html page
        buttons=[["success", "submit", "csv", "Download Order Information", ""],
                 ["success", "submit", "ordered", "Mark As Ordered", ""],
                 ["danger", "submit", "delete", "Delete", "return confirm('Are you sure you wish to delete?');"]]
        context = {
            "headers": headers,
            "body":zip(values,ids),
            "header":header,
            "subheader":subheader,
            "extrabuttons":buttons,
        }

        #render the ordered html page from the templates directory
        return render(request, 'checked_list.html', context=context)


## Primers on Order Page ##
#takes user clicking the 'primers on order' searchbar link as request and pulls the information of all primers with an order status of 'order placed'
@user_passes_test(is_logged_in, login_url=LOGINURL)
def order_placed(request):
    if request.method=="POST":
        primer_list = Primer.objects.filter(id__in=request.POST.getlist('primers'))
        if len(primer_list)!=0:
            #if 'testing required sanger' is clicked - iterate through the list of primers selected, update the order status to 'in testing sanger', assign the 'date_order_received' as todays date and save changes to the database
            if ('test_sanger' in request.POST) or ('test_non_sanger' in request.POST):
                if 'test_sanger' in request.POST:
                    status='In Testing Sanger'
                elif 'test_non_sanger' in request.POST:
                    status='In Testing Non-Sanger'
                for primer in primer_list:
                    primer.order_status = status
                    primer.date_order_recieved = date.today()
                    primer.save()

                #return the order recieved html page from the templates directory
                return render(request, 'action_completed.html')


            #if 'testing not required' is clicked - iterate through the list of primers selected, update the order status to 'stocked', assign the 'date_order_received' as todays date and save changes to the database
            elif 'stock' in request.POST:
                header="Primer Database"
                subheader="Please update location information:"
                headers=["Primer ID", "Alternative Name", "Direction", "Imported By", "Location"]
                values=[]
                ids=[]
                locs=[]
                for primer in primer_list:
                    values.append([primer.name,
                                   primer.alt_name,
                                   primer.direction,
                                  primer.imported_by_id.username,
                                  ])
                    locs.append(primer.location if primer.location is not None else "")
                    ids.append(primer.id)
                context = {
                    "header":header,
                    "subheader":subheader,
                    "headers":headers,
                    "body":zip(values,locs,ids),
                }

                #instead render the 'order recieved' html page from the templates directory - this will direct users to update lab location for these primers as they are being moved to 'stocked'
                return render(request, 'order_recieved_non_test.html', context=context)

    else:
        #pull primers with order status of order placed
        primers = Primer.objects.filter(order_status = "Order Placed")
        header="Primer Database: Ordered Primers"
        subheader="Primer information for primers on order:"
        headers=["Primer ID", "Reason Ordered", "Requested By", "Select"]
        values=[]
        ids=[]
        ordered = Primer.objects.filter(order_status = "Ordered")
        for primer in ordered:
            values.append([primer.name,
                          primer.reason_ordered,
                          primer.imported_by_id.username,
                          ])
            ids.append(primer.id)
        buttons=[["success", "submit", "test_sanger", "Testing Required: Sanger", ""],
                 ["success", "submit", "test_non_sanger", "Testing Required: Non-Sanger", ""],
                 ["success", "submit", "stock", "Testing Not Required", ""]]
        #provide context for the order placed html page
        context = {
            "headers": headers,
            "body":zip(values,ids),
            "header":header,
            "subheader":subheader,
            "extrabuttons":buttons,
        }

        #render the order placed html page from the templates directory
        return render(request, 'checked_list.html', context=context)




#for primers submitted as recieved, update the location information
@user_passes_test(is_logged_in, login_url=LOGINURL)
def location_updated(request):

    #pull lists of submitted primers and locations
    primers = Primer.objects.filter(id__in=request.POST.getlist('primer'))
    location_list = request.POST.getlist('location')

    #update the location info for primers locations were submitted for
    for primer, loc in zip(primers,location_list):
        primer.order_status = 'Stocked'
        primer.date_order_recieved = date.today()
        primer.location=loc
        primer.save()

    #render the 'location_updated' html page from the templates directory
    return render(request, 'action_completed.html')





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
