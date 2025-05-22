from odoo import models, fields, api, _
from datetime import date


class LibraryBooks(models.Model):
    _name = 'library.books'
    _description = 'Books'
    

    name = fields.Char(string='Books Name')
    total = fields.Float(string='Stock buku')
    description = fields.Text(string='Description')

    transaction_ids = fields.One2many(
        comodel_name='library.transaction', 
        inverse_name='book_ids', 
        string='Transactions')
    
    testing_field = fields.Char(string='Testing Field')

    total_books = fields.Integer(string='Available Books', compute='_compute_available_books', store=True)

    @api.depends('transaction_ids.state')
    def _compute_available_books(self):
        for record in self:
            in_progress_count = len(record.transaction_ids.filtered(lambda t: t.state == 'progress' and record.id in t.book_ids.ids))
            record.total_books = int(record.total) - in_progress_count


