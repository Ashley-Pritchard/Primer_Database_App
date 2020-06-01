---------------------
-- Primer Database --
---------------------

Ashley Pritchard <br>
README Last Updated: 13/05/2020 <br><br>

FUNCTION <br>

This repository contains the code for the development of 1) a primer database for the Oxford Medical Genomics Laboratories (OMGL) and 2) a django web app for interaction with the database. <br><br>

DESCRIPTION <br>

Prior to this project, primer data for the OMGL lab was stored as an excel file. The 'database_script' directory contains the script that was developed to clean,reformat and export this data into a format that could be uploaded into the new django database. <br>
The conda_primer_db directory contains the code for the django app, which follows the standard django format. <br>
The primer database app has 6 pages that can be navigated to from the homepage:<br> 
1) The 'search' page provides a means to search the database for primers and amplicons. Selected primers can also be reordered or archived from here.<br> 
2) The 'order' page allows an order for a new primer or primers to be placed for a single amplicon at a time.<br> 
3) The 'orders placed' page shows the primers that have been placed by lab members which have not yet been ordered from the companies. These primers can be selected and relevant information 'downloaded' to enable an order to be placed with a company, marked as 'ordered' to indicate that the order has been placed with the company or 'deleted' to cancel the order.<br>
4) The 'primers on order' page shows the primers which have been ordered from companies but have not yet arrived in the lab. When they are delievered, their lab location can be added and they can be marked as either 'recieved: testing required' or 'recieved: testing not required'. If testing is not required, they will be immediately recorded as 'stocked'.<br>
5) The 'primers in testing' page shows the primers that are currently undergoing valdation. The primers can be selected and marked as either 'validated' or 'not validated' and those that are validated will be marked as 'stocked'.<br>
6) The 'failed validation' page shows the primers that did not pass testing. They can be selected and removed from the page following acknowledgement. 

REQUIREMENTS <br>

Requirments can be found in the 'requirements.txt' file. 
