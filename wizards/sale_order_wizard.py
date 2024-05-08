import xlwt
import base64
from io import BytesIO
from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
import xml.etree.cElementTree as ET
from odoo.http import request
import os


class SaleOrderXmlWizard(models.TransientModel):
    _name = 'sale.order.xml.wizard'
    _description = 'Generate XML file'

    file_name = fields.Char('Filename', readonly=True)
    file = fields.Binary('File', readonly=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    image = fields.Binary()

    def create_xml_file_data(self):
        root = ET.Element('xml', encoding="utf-8", version="1.0")

        sale_record = self.env['sale.order'].search(
            [('date_order', '>=', self.start_date), ('date_order', '<=', self.end_date)])
        for order in sale_record:

            doc = ET.SubElement(root, "SaleOrder")
            order_id = ET.SubElement(doc, "orderId")
            order_id.text = order.name

            partner = ET.SubElement(doc, "partner")
            id = ET.SubElement(partner, "id")
            id.text = str(order.partner_id.id)
            par_name = ET.SubElement(partner, "name")
            par_name.text = str(order.partner_id.name)
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            image_url_1920 = base_url + '/web/image?' + 'model=res.partner&id=' + str(
                order.partner_id.id) + '&field=image_1920'
            par_img = ET.SubElement(partner, "Image")
            par_img.text = image_url_1920

            date = ET.SubElement(doc, "DateOrder", format="yyyy-MM-dd HH:mm:ss")
            date_val = ET.SubElement(date, "value")
            date_val.text = str(order.date_order)

            payment_term = ET.SubElement(doc, "PaymentTermId")
            payment_term.text = str(order.payment_term_id.name)

            template_data = ET.SubElement(doc, "QuotationTemplate")
            template_data.text = str(order.sale_order_template_id.name)
            sale_order_line = ET.SubElement(doc, "SaleOrderLine")
            for product in order.order_line:
                order_line = ET.SubElement(sale_order_line, "OrderLine")
                pro_data = ET.SubElement(order_line, "Product")
                pro_id = ET.SubElement(pro_data, "Id")
                pro_id.text = str(product.id)
                pro_name = ET.SubElement(pro_data, "Name")
                pro_name.text = str(product.name)
                price_unit = ET.SubElement(order_line, "PriceUnit")
                price_unit.text = str(product.price_unit)
                product_qty = ET.SubElement(order_line, "ProductUomQty")
                product_qty.text = str(product.product_uom_qty)
                if order.state == 'sale':
                    qty_delivered = ET.SubElement(order_line, "QtyDelivered")
                    qty_delivered.text = str(product.qty_delivered)
                    qty_invoiced = ET.SubElement(order_line, "QtyInvoiced")
                    qty_invoiced.text = str(product.qty_invoiced)
                tax_id = ET.SubElement(order_line, "TaxId")
                tax_id.text = str(product.tax_id.name)
                price_subtotal = ET.SubElement(order_line, "PriceSubtotal")
                price_subtotal.text = str(product.price_subtotal)

            amount_untaxed = ET.SubElement(doc, "Amount")
            amount_untaxed.text = str(order.amount_untaxed)
            amount_tax = ET.SubElement(doc, "Taxes")
            amount_tax.text = str(order.amount_tax)
            amt_total = ET.SubElement(doc, "Total")
            amt_total.text = str(order.amount_total)

        xmlstr = ET.tostring(root)
        file = base64.encodestring(xmlstr)
        self.file = file
        self.file_name = 'Sale Order' + '.xml'
        action = {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/sale.order.xml.wizard/%s/file/Sales Order.xml?download=true' % (
                self.id),
            'target': 'self',
        }

        return action
