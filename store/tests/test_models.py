from django.test import TestCase

from store.models import Category

class TestCategoriesModel(TestCase):

    def setUp(self):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")
        self.data1 = Category.objects.create(name='Test', slug='test')

    def test_category_model_entry(self):
        data = self.data1
        self.assertTrue(isinstance(data, Category))
        self.assertEqual(str(data), 'Test')