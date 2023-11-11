from typing import List
from odoo import fields, models, _, api
from odoo.exceptions import UserError
from odoo.tools import ustr
from ..dataclass.spp_address import Province, District, Ward
from ..common.func import Func


class SPPProvince(models.Model):
    _name = 'spp.province'
    _rec_name = 'province_name'
    _inherit = ['mail.thread']
    _description = 'SPP Provinces'

    def _default_country(self):
        return self.env['res.country'].search([('code', '=', 'VN')]).id

    country_id = fields.Many2one('res.country', string='Country', required=True, tracking=True,
                                 default=_default_country)
    province_id = fields.Integer(string='Province ID', required=True, tracking=True, index=True)
    province_code = fields.Char(string='Province Code', required=True, tracking=True)
    province_name = fields.Char(string='Province Name', required=True, tracking=True)
    district_ids = fields.One2many('spp.district', 'province_id', string='District')

    @api.model
    def sync_provinces(self):
        try:
            client = Func.get_api_client_spp(self)
            data_provinces: list = []
            result = client.sync_provinces()
            if not result:
                return
            lst_dataclass_province: List[Province] = [Province(*Province.parser_dict(res)) for res in result]
            province_ids = self.search([('province_id', 'in', [res.id for res in lst_dataclass_province])])
            lst_province_ids: List[int] = [province.province_id for province in province_ids]
            for data in lst_dataclass_province:
                if data.id not in lst_province_ids:
                    data_provinces.append(Province.parser_class(data))
            if lst_dataclass_province:
                self.create(data_provinces)
        except Exception as e:
            raise UserError(_(f'Sync province failed. Error: {ustr(e)}'))


class SPPDistrict(models.Model):
    _name = 'spp.district'
    _rec_name = 'district_name'
    _inherit = ['mail.thread']
    _description = 'SPP Districts'

    district_id = fields.Integer(string='District ID', required=True, tracking=True)
    district_code = fields.Char(string='District Code', required=True, tracking=True)
    district_name = fields.Char(string='District Name', required=True, tracking=True)
    province_id = fields.Many2one('spp.province', string='Province', required=True, tracking=True, index=True)
    ward_ids = fields.One2many('spp.ward', 'district_id', string='Ward')

    @api.model
    def sync_districts(self):
        try:
            client = Func.get_api_client_spp(self)
            data_districts: list = []
            result = client.sync_districts()
            if not result:
                return
            lst_dataclass_district: List[District] = [District(*District.parser_dict(res)) for res in result]
            district_ids = self.search([('district_id', 'in', [rec.id for rec in lst_dataclass_district])])
            lst_district_ids: List[int] = [district.district_id for district in district_ids]
            for data in lst_dataclass_district:
                if data.id not in lst_district_ids:
                    province_id = self.env['spp.province'].search([('province_id', '=', data.province_id)])
                    if not province_id:
                        continue
                    data_districts.append(District.parser_class(data, province_id=province_id.id))
            if data_districts:
                self.create(data_districts)
        except Exception as e:
            raise UserError(_(f'Sync district failed. Error: {str(e)}'))


class SPPWard(models.Model):
    _name = 'spp.ward'
    _rec_name = 'ward_name'
    _inherit = ['mail.thread']
    _description = 'SPP Wards'

    ward_id = fields.Integer(string='Ward ID', required=True, tracking=True)
    ward_name = fields.Char(string='Ward Name', required=True, tracking=True)
    did = fields.Integer(string='DID', required=True, tracking=True)
    district_id = fields.Many2one('spp.district', string='District', required=True, tracking=True)

    @api.model
    def sync_wards(self):
        try:
            client = Func.get_api_client_spp(self)
            data_wards: list = []
            result = client.sync_wards()
            if not result:
                return
            lst_dataclass_ward: List[Ward] = [Ward(*Ward.parser_dict(res)) for res in result]
            ward_ids = self.search([('ward_id', 'in', [rec.id for rec in lst_dataclass_ward])])
            lst_ward_ids: List[int] = [ward.ward_id for ward in ward_ids]
            for data in lst_dataclass_ward:
                if data.id not in lst_ward_ids:
                    district_id = self.env['spp.district'].search([('district_id', '=', data.district_id)])
                    if not district_id:
                        continue
                    data_wards.append(Ward.parser_class(data, district_id=district_id.id))
            if data_wards:
                self.create(data_wards)
        except Exception as e:
            raise UserError(_(f'Sync ward failed. Error: {str(e)}'))