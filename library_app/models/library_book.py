from odoo import api, fields, models
from odoo.exceptions import Warning

class Book(models.Model):
    _name = 'library.book'
    _description = 'Book'
    _order = 'date_published,name desc'

    # String fields
    name = fields.Char(
        'Title',
        default=None,
        index=True,
        help='Book cover title',
        readonly=False,
        required=True,
        translate=False,
    )
    isbn = fields.Char('ISBN')
    book_type = fields.Selection(
        [('paper', 'Paperback'),
         ('hard', 'Hardcover'),
         ('electronic', 'Electronic'),
         ('other', 'Other')],
        'Type')
    notes = fields.Text('Internal Notes')
    descr = fields.Html('Description')

    # Numeric fields:
    copies = fields.Integer(default=1)
    avg_rating = fields.Float('Average Rating', (3, 2))
    price = fields.Monetary('Price', 'currency_id')
    currency_id = fields.Many2one('res.currency')  # price helper

    # Date and time fields
    date_published = fields.Date()
    last_borrow_date = fields.Datetime(
        'Last Borrowed On',
        default=lambda self: fields.Datetime.now(),
    )

    # Other fields
    active = fields.Boolean('Active?', default=True)
    image = fields.Binary('Cover')

    # Relational Fields
    publisher_id = fields.Many2one(
        'res.partner', string='Publisher')
    author_ids = fields.Many2many('res.partner', string='Authors')
    publisher_country_id = fields.Many2one(
        'res.country', string='Publisher Country',
        #related='publisher_id.country_id',
        compute='_compute_publisher_country',
        # store = False, @ 默认不在数据库中存储
        # inverse='_inverse_publisher_country',
        # search='_search_publisher_country',
    )

    # Book Category
    book_category = fields.Many2one(
        'library.book.category'
    )

    @api.multi
    def _check_isbn(self):
        self.ensure_one()
        isbn = self.isbn.replace('-', '')  # 为保持兼容性 Alan 自行添加
        digits = [int(x) for x in isbn if x.isdigit()]
        if len(digits) == 13:
            ponderations = [1, 3] * 6
            terms = [a * b for a, b in zip(digits[:12], ponderations)]
            remain = sum(terms) % 10
            check = 10 - remain if remain != 0 else 0
            return digits[-1] == check

    @api.multi
    def button_check_isbn(self):
        for book in self:
            if not book.isbn:
                raise Warning('Please provide an ISBN for %s' % book.name)
            if book.isbn and not book._check_isbn():
                raise Warning('%s is an invalid ISBN' % book.isbn)
            return True

    @api.depends('publisher_id.country_id')
    def _compute_publisher_country(self):
        for book in self:
            book.publisher_country_id = book.publisher_id.country_id