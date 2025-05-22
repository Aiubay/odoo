from odoo import models, fields, api, _
from datetime import date,timedelta
from odoo.exceptions import UserError


class LibraryTransaction(models.Model):
    _name = 'library.transaction'
    _description = 'Library Transaction'

    name = fields.Char(string='Transaction Name', copy=False, readonly=True, index=True, default='New')
    description = fields.Text(string='Description')
    rent_date = fields.Date(string='Tanggal Pinjam')

    book_ids = fields.Many2one(
        'library.books', 
        string='Books',
        required=True,
        domain="[('total_books', '>', 0)]",
    )
    
    return_date = fields.Date(string='Tanggal Kembali')
    
    partner_id = fields.Many2one('res.partner', string='Peminjam',required=True)
  
    @api.constrains('book_ids')
    def _check_book_availability(self):
        for record in self:
            if record.book_ids and record.book_ids.total_books <= 0:
                raise UserError(_("The selected book is not available for borrowing."))

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("progress", "Progress"),
            ("done", "Done")
        ], string='Status', default="draft"
    )

    def action_draft(self):
        self.return_date = False
        self.rent_date = False
        self.state = 'draft'

    def action_progress(self):
        for session in self:
            if session.state != 'draft':
                raise UserError("Only draft sessions can be progressed.")
            if not session.rent_date:
                session.rent_date = date.today()
            else:
                raise UserError("The selected book is not available for borrowing.")
            
            session.state = 'progress'

    def action_done(self):
        for session in self:
            if session.state != 'progress':
                raise UserError("Only sessions in progress can be completed.")
            if not session.return_date:
                session.return_date = date.today() + timedelta(days=7)
            session.state = 'done'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('library.transaction') or 'New'
        return super(LibraryTransaction, self).create(vals)
    