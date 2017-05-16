# -*- coding: utf-8 -*-
from openerp import tools, models, fields, api, _
from ast import literal_eval


class AccountArVatLine(models.Model):
    """
    Modelo base para nuevos reportes argentinos de iva. La idea es que estas
    lineas tenga todos los datos necesarios y que frente a cambios en odoo, los
    mismos sean abosrvidos por este cubo y no se requieran cambios en los
    reportes que usan estas lineas.
    Se genera una linea para cada apunte contable afectado por iva
    Basicamente lo que hace es convertir los apuntes contables en columnas
    segun la informacion de impuestos y ademas agrega algunos otros
    campos
    """
    _name = "account.ar.vat.line"
    _description = "Línea de IVA para análisis en localización argentina"
    _auto = False
    # _rec_name = 'document_number'
    # _order = 'date asc, date_maturity asc, document_number asc, id'
    # _depends = {
    #     'res.partner': [
    #         'user_id',
    #     ],
    #     'account.move': [
    #         'document_type_id', 'document_number',
    #     ],
    #     'account.move.line': [
    #         'account_id', 'debit', 'credit', 'date_maturity', 'partner_id',
    #         'amount_currency',
    #     ],
    # }

    document_type_id = fields.Many2one(
        'account.document.type',
        'Document Type',
        readonly=True
    )
    # document_number = fields.Char(
    #     readonly=True,
    #     string='Document Number',
    # )
    date = fields.Date(
        readonly=True
    )
    # TODO analizar si lo hacemos related simplemente pero con store, no lo
    # hicimos por posibles temas de performance
    journal_type = fields.Selection([
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'),
    ],
        # readonly=True
        # related='journal_id.type',
        readonly=True
    )
    ref = fields.Char(
        'Partner Reference',
        readonly=True
    )
    name = fields.Char(
        'Label',
        readonly=True
    )
    base_21 = fields.Monetary(
        readonly=True,
        string='Grav. 21%',
        currency_field='company_currency_id',
    )
    iva_21 = fields.Monetary(
        readonly=True,
        string='IVA 21%',
        currency_field='company_currency_id',
    )
    base_27 = fields.Monetary(
        readonly=True,
        string='Grav. 27%',
        currency_field='company_currency_id',
    )
    iva_27 = fields.Monetary(
        readonly=True,
        string='IVA 27%',
        currency_field='company_currency_id',
    )
    base_10 = fields.Monetary(
        readonly=True,
        string='Grav. 10,5%',
        currency_field='company_currency_id',
    )
    iva_10 = fields.Monetary(
        readonly=True,
        string='IVA 10,5%',
        currency_field='company_currency_id',
    )
    base_25 = fields.Monetary(
        readonly=True,
        string='Grav. 2,5%',
        currency_field='company_currency_id',
    )
    iva_25 = fields.Monetary(
        readonly=True,
        string='IVA 2,5%',
        currency_field='company_currency_id',
    )
    base_5 = fields.Monetary(
        readonly=True,
        string='Grav. 5%',
        currency_field='company_currency_id',
    )
    iva_5 = fields.Monetary(
        readonly=True,
        string='IVA 5%',
        currency_field='company_currency_id',
    )
    per_iva = fields.Monetary(
        readonly=True,
        string='Perc. IVA',
        help='Percepción de IVA',
        currency_field='company_currency_id',
    )
    per_iibb = fields.Monetary(
        readonly=True,
        string='Perc. IIBB',
        help='Percepción de IIBB',
        currency_field='company_currency_id',
    )
    per_ganancias = fields.Monetary(
        readonly=True,
        string='Perc. Gan.',
        help='Percepción de ganancias',
        currency_field='company_currency_id',
    )
    ret_iva = fields.Monetary(
        readonly=True,
        string='Ret. IVA',
        help='Retención de IVA',
        currency_field='company_currency_id',
    )
    no_gravado_iva = fields.Monetary(
        readonly=True,
        string='No grav/ex',
        help='No gravado / Exento.\n'
        'Todo lo que tenga iva 0, exento, no gravado o no corresponde',
        currency_field='company_currency_id',
    )
    otros_impuestos = fields.Monetary(
        readonly=True,
        string='Otr. Imp',
        help='Otros Impuestos. Todos los impuestos otros impuestos que no sean'
        ' ni iva ni perc de iibb y que figuren en comprobantes afectados por '
        'IVA',
        currency_field='company_currency_id',
    )
    total = fields.Monetary(
        readonly=True,
        currency_field='company_currency_id',
    )
    # currency_id = fields.Many2one(
    #     'res.currency',
    #     'Currency',
    #     readonly=True
    # )
    # amount_currency = fields.Monetary(
    #     readonly=True,
    #     currency_field='currency_id',
    account_id = fields.Many2one(
        'account.account',
        'Account',
        readonly=True
    )
    # TODO idem, tal vez related con store? Performance?
    state = fields.Selection(
        [('draft', 'Unposted'), ('posted', 'Posted')],
        'Status',
        readonly=True
    )
    journal_id = fields.Many2one(
        'account.journal',
        'Journal',
        readonly=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        readonly=True
    )
    # TODO idem, tal vez related con store? Performance?
    afip_responsability_type_id = fields.Many2one(
        'afip.responsability.type',
        string='AFIP Responsability Type',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        readonly=True
    )
    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=True,
    )
    move_id = fields.Many2one(
        'account.move',
        string='Entry',
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Journal Item',
    )
    # payment_group_id = fields.Many2one(
    #     'account.payment.group',
    #     'Payment Group',
    #     compute='_compute_move_lines_data',
    # )
    # invoice_id = fields.Many2one(
    #     'account.invoice',
    #     'Invoice',
    #     compute='_compute_move_lines_data',
    # )
    # es una concatenacion de los name de los move lines
    # name = fields.Char(
    #     compute='_compute_move_lines_data',
    # )

    # TODO usar en v10
    # @api.model_cr
    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        env = api.Environment(cr, 1, {})
        ref = env.ref
        vat_tax_groups = env['account.tax.group'].search(
            [('tax', '=', 'vat')])
        # TODO ver si en prox versiones en vez de usar los tax group y ext id
        # usamos labels o algo mas odoo way
        vals = {
            'tg21': ref('l10n_ar_account.tax_group_iva_21').id,
            'tg10': ref('l10n_ar_account.tax_group_iva_10').id,
            'tg27': ref('l10n_ar_account.tax_group_iva_27').id,
            'tg25': ref('l10n_ar_account.tax_group_iva_25').id,
            'tg5': ref('l10n_ar_account.tax_group_iva_5').id,
            'tg_per_iva': ref('l10n_ar_account.tax_group_percepcion_iva').id,
            'tg_ret_iva': ref('l10n_ar_account.tax_group_retencion_iva').id,
            'tg_per_iibb': ref('l10n_ar_account.tax_group_percepcion_iibb').id,
            'tg_per_ganancias': ref(
                'l10n_ar_account.tax_group_percepcion_ganancias').id,
            'tg_iva0': tuple(vat_tax_groups.ids),
            'tg_other': tuple(vat_tax_groups.ids),
            'tg_vats': tuple(vat_tax_groups.ids),
        }
        query = """
SELECT
    aml.id,
    aml.id as move_line_id,
    aml.date,
    aml.move_id,
    aml.journal_id,
    aml.company_id,
    aml.partner_id,
    aml.name,
    aml.ref,
    am.afip_responsability_type_id,
    am.state,
    am.document_type_id,
    aj.type as journal_type,
/*    (CASE
        WHEN aml.payment_id is not null and ap.partner_type = 'supplier'
            THEN 'Pago'
        WHEN aml.payment_id is not null and ap.partner_type = 'customer'
            THEN 'Cobro'
        WHEN aml.invoice_id is not null THEN 'Invoice'
        ELSE 'Other' END) as tipo_doc,*/
    sum(CASE WHEN bt.tax_group_id=%(tg21)s THEN balance ELSE 0 END) as base_21,
    sum(CASE WHEN nt.tax_group_id=%(tg21)s THEN balance ELSE 0 END) as iva_21,
    sum(CASE WHEN bt.tax_group_id=%(tg10)s THEN balance ELSE 0 END) as base_10,
    sum(CASE WHEN nt.tax_group_id=%(tg10)s THEN balance ELSE 0 END) as iva_10,
    sum(CASE WHEN bt.tax_group_id=%(tg27)s THEN balance ELSE 0 END) as base_27,
    sum(CASE WHEN bt.tax_group_id=%(tg27)s THEN balance ELSE 0 END) as iva_27,
    sum(CASE WHEN bt.tax_group_id=%(tg25)s THEN balance ELSE 0 END) as base_25,
    sum(CASE WHEN bt.tax_group_id=%(tg25)s THEN balance ELSE 0 END) as iva_25,
    sum(CASE WHEN nt.tax_group_id=%(tg5)s THEN balance ELSE 0 END) as base_5,
    sum(CASE WHEN nt.tax_group_id=%(tg5)s THEN balance ELSE 0 END) as iva_5,
    --TODO separar sufido y aplicado o filtrar por tipo de operacion o algo?
    sum(CASE WHEN nt.tax_group_id=%(tg_per_iva)s THEN balance ELSE 0 END)
        as per_iva,
    sum(CASE WHEN nt.tax_group_id=%(tg_ret_iva)s THEN balance ELSE 0 END)
        as ret_iva,
    sum(CASE WHEN nt.tax_group_id=%(tg_per_iibb)s THEN balance ELSE 0 END)
        as per_iibb,
    sum(CASE WHEN nt.tax_group_id=%(tg_per_ganancias)s THEN balance ELSE 0 END)
        as per_ganancias,
    sum(CASE WHEN nt.tax_group_id in %(tg_iva0)s THEN balance ELSE 0 END)
        as no_gravado_iva,
    sum(CASE WHEN nt.tax_group_id not in %(tg_other)s THEN balance ELSE 0 END)
        as otros_impuestos,
    sum(balance) as total
FROM
    account_move_line aml
LEFT JOIN
    account_move as am
    ON aml.move_id = am.id
/*LEFT JOIN
    account_payment as ap
    ON aml.payment_id = ap.id*/
/*LEFT JOIN
    res_partner as rp
    ON aml.partner_id = rp.id*/
LEFT JOIN
    account_account AS aa
    ON aml.account_id = aa.id
LEFT JOIN
    account_journal AS aj
    ON aml.journal_id = aj.id
LEFT JOIN
    -- nt = net tax
    account_tax AS nt
    ON aml.tax_line_id = nt.id
LEFT JOIN
    account_move_line_account_tax_rel AS amltr
    ON aml.id = amltr.account_move_line_id
LEFT JOIN
    -- bt = base tax
    account_tax AS bt
    ON amltr.account_tax_id = bt.id
WHERE
    aa.internal_type not in ('payable', 'receivable') and
    (nt.tax_group_id in %(tg_vats)s or bt.tax_group_id in %(tg_vats)s)
GROUP BY
    aml.id, aj.type, am.state, am.document_type_id,
    am.afip_responsability_type_id
    /*move_id, journal_id, aj.type*/
        """ % vals

        cr.execute("""CREATE or REPLACE VIEW %s as (%s
        )""" % (self._table, query))