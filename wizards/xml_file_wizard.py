import xlwt
import base64
from io import BytesIO
from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
import xml.etree.cElementTree as ET


class XmlFileWizard(models.TransientModel):
    _name = 'xml.file.wizard'
    _description = 'XML file Wizard'

    file = fields.Binary(string='File', attachment=True, store=True)
    file_name = fields.Char('File name')

    def read_xml_file_data(self):
        stream = BytesIO(base64.b64decode(self.file))
        root = ET.parse(stream).getroot()
        for elem in root:
            order_line_values = []
            state_data = ''
            for info in elem.findall('SaleOrderLine'):
                for minfo in info.findall('OrderLine'):
                    if minfo.findall('QtyDelivered'):
                        state_data = 'sale'
                        line = (0, 0, {'product_id': int(minfo.find('Product/Id').text),
                                       'product_uom_qty': float(minfo.find('ProductUomQty').text),
                                       'price_unit': float(minfo.find('PriceUnit').text),
                                       'qty_delivered': float(minfo.find('QtyDelivered').text),
                                       'qty_invoiced': float(minfo.find('QtyInvoiced').text),
                                       'price_subtotal': float(minfo.find('PriceSubtotal').text)
                                       })
                        order_line_values.append(line)

                    else:
                        state_data = 'draft'
                        line = (0, 0, {'product_id': int(minfo.find('Product/Id').text),
                                       'product_uom_qty': float(minfo.find('ProductUomQty').text),
                                       'price_unit': float(minfo.find('PriceUnit').text),
                                       'price_subtotal':float(minfo.find('PriceSubtotal').text)
                                       })
                        order_line_values.append(line)

            sale_record = {
                'partner_id': int(elem.find('partner/id').text),
                "date_order": elem.find('DateOrder/value').text,
                "state": state_data,
                "amount_untaxed": float(elem.find('Amount').text),
                "amount_tax": float(elem.find('Taxes').text),
                "amount_total": float(elem.find('Total').text),
                "order_line": order_line_values,
            }
            record = self.env['sale.order'].create(sale_record)
            return record
