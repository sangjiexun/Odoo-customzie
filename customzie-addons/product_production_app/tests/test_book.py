from odoo.tests.common import TransactionCase
class TestBook(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)
        self.Book = self.env['library.book']
        self.book_ode = self.Book.create({
            'name': 'Odoo Development Essentials',
            'isbn': '879-1-78439-279-6'})
        return result

    def test_create(self):
        "Test Books are active by default"
        self.assertEqual(self.book_ode.active, True)
    def test_check_isbn(self):
        "Check valid ISBN"
        self.assertTrue(self.book_ode._check_isbn)
