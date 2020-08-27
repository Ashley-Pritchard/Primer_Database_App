from django.test import SimpleTestCase, TestCase, Client 
from django.urls import reverse, resolve
from primer_db_site.views import *
from primer_db_site.models import *
import json

#unit tests 

#url tests
class TestUrls(SimpleTestCase):

	def test_search_url_resolves(self):
		url = reverse('search')
		self.assertEquals(resolve(url).func, search)

	def test_primer_url_resolves(self):
		url = reverse('primer')
		self.assertEquals(resolve(url).func, primer)

	def test_amplicon_url_resolves(self):
		url = reverse('amplicon')
		self.assertEquals(resolve(url).func, amplicon)

	def test_order_url_resolves(self):
		url = reverse('order')
		self.assertEquals(resolve(url).func, order)

	def test_order_form_url_resolves(self):
		url = reverse('order_form')
		self.assertEquals(resolve(url).func, order_form)

	def test_submitted_url_resolves(self):
		url = reverse('submitted')
		self.assertEquals(resolve(url).func, submitted)

	def test_ordered_url_resolves(self):
		url = reverse('ordered')
		self.assertEquals(resolve(url).func, ordered)

	def test_order_to_amplicon_url_resolves(self):
		url = reverse('order_to_amplicon')
		self.assertEquals(resolve(url).func, order_to_amplicon)

	def test_submitted_to_amplicon_url_resolves(self):
		url = reverse('submitted_to_amplicon')
		self.assertEquals(resolve(url).func, submitted_to_amplicon)

	def test_reorder_primer_url_resolves(self):
		url = reverse('reorder_primer')
		self.assertEquals(resolve(url).func, reorder_primer)

	def test_archive_primer_url_resolves(self):
		url = reverse('archive_primer')
		self.assertEquals(resolve(url).func, archive_primer)

	def test_submit_order_url_resolves(self):
		url = reverse('submit_order')
		self.assertEquals(resolve(url).func, submit_order)

	def test_order_placed_url_resolves(self):
		url = reverse('order_placed')
		self.assertEquals(resolve(url).func, order_placed)

	def test_order_recieved_url_resolves(self):
		url = reverse('order_recieved')
		self.assertEquals(resolve(url).func, order_recieved)

	def test_in_testing_url_resolves(self):
		url = reverse('in_testing')
		self.assertEquals(resolve(url).func, in_testing)

	def test_tested_url_resolves(self):
		url = reverse('tested')
		self.assertEquals(resolve(url).func, tested)

	def test_failed_url_resolves(self):
		url = reverse('failed')
		self.assertEquals(resolve(url).func, failed)

	def test_remove_failed_url_resolves(self):
		url = reverse('remove_failed')
		self.assertEquals(resolve(url).func, remove_failed)

#view tests
class TestViews(TestCase):

	def setUp(self):
		self.client = Client()
		self.index_url = reverse('index')
		self.order_url = reverse('order')
		self.ordered_url = reverse('ordered')
		self.order_to_amplicon_url = reverse('order_to_amplicon')
		self.reorder_primer_url = reverse('reorder_primer')
		self.submit_order_url = reverse('submit_order')
		self.order_placed_url = reverse('order_placed')
		self.order_recieved_url = reverse('order_recieved')
		self.in_testing_url = reverse('in_testing')
		self.tested_url = reverse('tested')
		self.failed_url = reverse('failed')
		self.remove_failed_url = reverse('remove_failed')

	def test_index_GET(self):
		response = self.client.get(self.index_url)	
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'index.html')

	def test_order_GET(self):
		response = self.client.get(self.order_url)	
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'order.html')

	def test_ordered_GET(self):
		response = self.client.get(self.ordered_url)	
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'ordered.html')

	def test_order_to_amplicon_GET(self):
		response = self.client.get(self.order_to_amplicon_url)	
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'order_to_amplicon.html')


	def test_reoder_primer_GET(self):
		response = self.client.get(self.reorder_primer_url)	
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'submitted_reorder_primer.html')

	def test_submit_order_GET(self):
		response = self.client.get(self.submit_order_url)	
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'submit_order.html')

	def test_order_placed_GET(self):
		response = self.client.get(self.order_placed_url)	
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'order_placed.html')

	def test_order_recieved_GET(self):
		response = self.client.get(self.order_recieved_url)	
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'order_recieved.html')

	def test_in_testing_GET(self):
		response = self.client.get(self.in_testing_url)	
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'in_testing.html')

	def test_tested_GET(self):
		response = self.client.get(self.tested_url)	
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'tested.html')

	def test_failed_GET(self):
		response = self.client.get(self.failed_url)	
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'failed.html')

	def test_remove_failed_GET(self):
		response = self.client.get(self.remove_failed_url)	
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'remove_failed.html')


