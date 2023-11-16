import re
import cv2
import json
import pickle
import easyocr
import logging
import numpy as np
import face_recognition
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from odoo.tools import ustr
from odoo.http import request, Controller, route
from werkzeug.wrappers import Request, Response
from ..common.common_logging import Logging


_logger = Logging(filename='odoo.server', exec_name=__name__).get_logger()


def response(status: int,
             message: str,
             data: Optional = None) -> Dict[str, Any]:
    response = {'status': status, 'message': message}
    if data:
        response.update({'data': data})
    return response


class FlaskSPP(Controller):

    @staticmethod
    def _prepare_response_info(product_ids, qa_ids, company_id):
        data = {
            'product_ids': [{
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_price': product.list_price,
                    'product_duration': product.duration,
                    'product_slot': product.slot,
                    'product_priority': product.priority,
                    'product_description': [match.strip() for match in
                                            re.findall(r'<[^>]+>(.*?)<[^>]+>', product.description)]
            } for product in product_ids],
            'qas': [{
                'id': qa.id,
                'question': qa.question,
                'answer': qa.answer
            } for qa in qa_ids],
            'company': {
                'street': company_id.street,
                'email': company_id.email,
                'phone': company_id.phone,
                'name': company_id.name,
            }
        }
        return data

    @route('/odoo-api/spp/index/info', type='http', auth='public', methods=['GET'])
    def get_info_index(self):
        try:
            product_ids = request.env['product.template'].sudo().search([], order='id asc')
            qa_ids = request.env['spp.question.answer'].sudo().search([], order='id asc')
            company_id = request.env['res.company'].sudo().search([
                ('vat', '=', '9999999999'),
                ('company_registry', '=', '9999999999')
            ], limit=1)
            data = self._prepare_response_info(product_ids, qa_ids, company_id)
            return Response(json.dumps(response(status=200, message='Successfully', data=data)),
                            headers={'Content-Type': 'application/json'})
        except Exception as e:
            _logger.exception(ustr(e))
            return Response(json.dumps(response(status=500, message=ustr(e))),
                            headers={'Content-Type': 'application/json'})

    @staticmethod
    def _prepare_response_province(provinces):
        data = [(province.province_id, province.province_name) for province in provinces]
        return data

    @staticmethod
    def _prepare_response_district(districts):
        data = [(district.district_id, district.district_name) for district in districts]
        return data

    @staticmethod
    def _prepare_response_ward(wards):
        data = [(ward.ward_id, ward.ward_name) for ward in wards]
        return data

    @route('/odoo-api/spp/get-provinces', type='http', auth='public', methods=['GET'])
    def get_provinces(self):
        try:
            provinces = request.env['spp.province'].sudo().search([])
            if not provinces:
                return Response(json.dumps(response(status=400, message='The province not found.')),
                                headers={'Content-Type': 'application/json'})
            data = self._prepare_response_province(provinces)
            return Response(json.dumps(response(status=200, message='Successfully', data=data)),
                            headers={'Content-Type': 'application/json'})
        except Exception as e:
            _logger.exception(ustr(e))
            return Response(json.dumps(response(status=500, message=ustr(e))),
                            headers={'Content-Type': 'application/json'})

    @route('/odoo-api/spp/get-district/<int:province_id>', type='http', auth='public', methods=['GET'])
    def get_district(self, province_id):
        try:
            districts = request.env['spp.district'].sudo().search([('province_id', '=', province_id)])
            if not districts:
                return Response(json.dumps(response(status=400, message='The districts not found.')),
                                headers={'Content-Type': 'application/json'})
            data = self._prepare_response_district(districts)
            return Response(json.dumps(response(status=200, message='Successfully', data=data)),
                            headers={'Content-Type': 'application/json'})
        except Exception as e:
            _logger.exception(ustr(e))
            return Response(json.dumps(response(status=500, message=ustr(e))),
                            headers={'Content-Type': 'application/json'})

    @route('/odoo-api/spp/get-ward/<int:district_id>', type='http', auth='public', methods=['GET'])
    def get_ward(self, district_id):
        try:
            wards = request.env['spp.ward'].sudo().search([('district_id', '=', district_id)])
            if not wards:
                return Response(json.dumps(response(status=400, message='The wards not found.')),
                                headers={'Content-Type': 'application/json'})
            data = self._prepare_response_ward(wards)
            return Response(json.dumps(response(status=200, message='Successfully', data=data)),
                            headers={'Content-Type': 'application/json'})
        except Exception as e:
            _logger.exception(ustr(e))
            return Response(json.dumps(response(status=500, message=ustr(e))),
                            headers={'Content-Type': 'application/json'})

    @route('/odoo-api/spp/user/sign_up', type='json', auth='public', methods=['POST'], csrf=False)
    def register_user(self):
        try:
            UserObject = request.env['res.users'].sudo()
            payload = request.dispatcher.jsonrequest
            UserObject.signup(payload)
            user_id = UserObject.search([('login', '=', payload.get('login'))])
            user_id._change_password(payload.get('password'))
            return Response(json.dumps(response(status=200, message='Successfully')),
                            headers={'Content-Type': 'application/json'})
        except Exception as e:
            _logger.exception(ustr(e))
            return Response(json.dumps(response(status=500, message=ustr(e))),
                            headers={'Content-Type': 'application/json'})

    @route('/odoo-api/spp/user/sign_out', type='http', auth='none', csrf=False)
    def sign_out(self):
        try:
            request.session.logout(keep_db=True)
            return Response(json.dumps(response(status=200, message='Successfully')),
                            headers={'Content-Type': 'application/json'})
        except Exception as e:
            _logger.exception(ustr(e))
            return Response(json.dumps(response(status=500, message=ustr(e))),
                            headers={'Content-Type': 'application/json'})

    @staticmethod
    def _create_register_vehicle(product_id, user_id, license_plates: List[str]):
        request.env['spp.registered.vehicle'].sudo().create([{
            'product_id': product_id.id,
            'user_id': user_id.id,
            'license_plate': license_plate,
            'expire_date': datetime.now() + timedelta(days=product_id.duration)
        } for license_plate in license_plates])

    def _create_sale_order(self, user_id, service_id: int, license_plate: List[str]):
        product_id = request.env['product.template'].sudo().browse(service_id)
        sale_order = request.env['sale.order'].sudo().create({
            'partner_id': user_id.partner_id.id,
            'order_line': [(0, 0, {
                'product_id': product_id.id,
                'name': ' - '.join(license_plate),
                'product_uom_qty': 1
            })]
        })
        sale_order.action_confirm()
        self._create_register_vehicle(product_id, user_id, license_plate)

    @staticmethod
    def _validate_parameter(params, bufferer_image):
        if not params.get('uid'):
            return Response(json.dumps(response(status=400, message='The uid field is required.')),
                            headers={'Content-Type': 'application/json'})
        elif not params.get('service_id'):
            return Response(json.dumps(response(status=400, message='The service id field is required.')),
                            headers={'Content-Type': 'application/json'})
        elif not bufferer_image:
            return Response(json.dumps(response(status=400, message='The bufferer image face field is required.')),
                            headers={'Content-Type': 'application/json'})
        return True

    @staticmethod
    def encoding_face(face_image: List[bytes]):
        num_array = np.frombuffer(face_image, np.uint8)
        img_list = cv2.imdecode(num_array, cv2.IMREAD_COLOR)
        img_list_rgb = cv2.cvtColor(img_list, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img_list_rgb)[0]
        return encode

    @staticmethod
    def validate_license_plate(result: List[str]):
        if not result or len(result) != 2:
            return Response(json.dumps(response(status=400, message='OCR failed. D\'ont recognize license plate')),
                            headers={'Content-Type': 'application/json'})
        elif not result[0][:2].isnumeric():
            return Response(json.dumps(response(status=400, message='OCR failed. Local code invalid')),
                            headers={'Content-Type': 'application/json'})
        elif not result[0][-1].isalpha():
            return Response(
                json.dumps(response(status=400, message='OCR failed. Registration character series invalid')),
                headers={'Content-Type': 'application/json'})
        elif len(result[1]) not in [4, 5]:
            return Response(json.dumps(response(status=400, message='OCR failed. Length registration number invalid')),
                            headers={'Content-Type': 'application/json'})
        elif not result[1].isnumeric():
            return Response(json.dumps(response(status=400, message='OCR failed. Registration number invalid')),
                            headers={'Content-Type': 'application/json'})
        return True

    @staticmethod
    def clean_character(text):
        character_cleaned = re.sub(r'[^\w\s]', '', text)
        character_cleaned = re.sub(r'\s', '', character_cleaned)
        return character_cleaned

    @staticmethod
    def license_plate_ocr(license_plate_bytes: List[bytes]):
        reader = easyocr.Reader(['en'])
        license_plate_list = []
        for license_plate_byte in license_plate_bytes:
            result = [FlaskSPP.clean_character(r) for r in reader.readtext(image=license_plate_byte, detail=0)]
            if not FlaskSPP.validate_license_plate(result):
                return False
            license_plate_list.append(''.join(result).upper())
        return license_plate_list

    @staticmethod
    def _validate_quantity_slot_parking():
        quantity = request.env['ir.config_parameter'].sudo().get_param('spp.maximum_qty_slot_parking', False)
        if not quantity:
            return Response(json.dumps(response(status=400, message='Quantity slot parking not found.')),
                            headers={'Content-Type': 'application/json'})
        total_slot = request.env['spp.registered.vehicle'].sudo().search_count([])
        if total_slot >= int(quantity):
            return Response(json.dumps(response(status=400, message='Quantity slot parking is full.')),
                            headers={'Content-Type': 'application/json'})
        return True

    @route('/odoo-api/spp/service/register', type='http', auth='public', methods=['POST'], csrf=False)
    def register_service(self):
        try:
            is_be_registered = self._validate_quantity_slot_parking()
            if is_be_registered is not True:
                return is_be_registered
            params = request.httprequest.args
            bufferer_image = request.httprequest.data
            is_valid = self._validate_parameter(params, bufferer_image)
            if is_valid is not True:
                return is_valid
            images = pickle.loads(bufferer_image)
            image_faces = images.get('image_face_bytes')
            image_license_plate = images.get('image_license_plate_bytes')
            if not image_faces:
                return Response(json.dumps(response(status=400, message='Image face is required.')),
                                headers={'Content-Type': 'application/json'})
            elif not image_license_plate:
                return Response(json.dumps(response(status=400, message='Image license plate is required.')),
                                headers={'Content-Type': 'application/json'})
            for image in image_faces:
                if not image.get('face_binary'):
                    return Response(json.dumps(response(status=400, message='Image face binary is required.')),
                                    headers={'Content-Type': 'application/json'})
                elif not image.get('face_name'):
                    return Response(json.dumps(response(status=400, message='Name face is required.')),
                                    headers={'Content-Type': 'application/json'})
            license_plate_character = self.license_plate_ocr(image_license_plate)
            user_id = request.env['res.users'].sudo().browse(int(params.get('uid')))
            self._create_sale_order(user_id=user_id,
                                    service_id=int(params.get('service_id')),
                                    license_plate=license_plate_character)
            request.env['spp.user.face'].sudo().create([{
                'user_id': user_id.id,
                'face_encoding': pickle.dumps([self.encoding_face(image.get('face_binary')), image.get('face_name')]),
                'face_binary': image.get('face_binary'),
                'face_name': image.get('face_name')
            } for image in image_faces])
        except Exception as e:
            return Response(json.dumps(response(status=500, message=ustr(e))),
                            headers={'Content-Type': 'application/json'})

    @route('/odoo-api/spp/service/validate', type='http', auth='public', methods=['POST'], csrf=False)
    def validate_quantity_slot_parking(self):
        try:
            quantity = request.env['ir.config_parameter'].sudo().get_param('spp.maximum_qty_slot_parking', False)
            if not quantity:
                return Response(json.dumps(response(status=400, message='Quantity slot parking not found.')),
                                headers={'Content-Type': 'application/json'})
            total_slot = request.env['spp.registered.vehicle'].sudo().search_count([])
            if total_slot >= int(quantity):
                return Response(json.dumps(response(status=400, message='Quantity slot parking is full.')),
                                headers={'Content-Type': 'application/json'})
            return Response(json.dumps(response(status=200, message='Successfully.')),
                            headers={'Content-Type': 'application/json'})
        except Exception as e:
            return Response(json.dumps(response(status=500, message=ustr(e))),
                            headers={'Content-Type': 'application/json'})

    @route('/odoo-api/spp/user/profile', type='http', auth='public', methods=['POST'], csrf=False)
    def profile(self):
        try:
            params = request.httprequest.args
            uid = params.get('uid')
            if not uid:
                return Response(json.dumps(response(status=400, message='Uid is required.')),
                                headers={'Content-Type': 'application/json'})
            vehicle_ids = request.env['spp.registered.vehicle'].sudo().search([('user_id', '=', int(uid))])
            history_ids = request.env['spp.vehicle.io.history'].sudo().search([('user_id', '=', int(uid))])
            if not vehicle_ids:
                return Response(json.dumps(response(status=400, message='User not found.')),
                                headers={'Content-Type': 'application/json'})
            profile = {
                'current_package': [{
                    'id': vehicle_id.id,
                    'name': vehicle_id.product_id.name,
                    'price': vehicle_id.product_id.list_price,
                    'css': vehicle_id.state,
                    'state':
                        [v for k, v in dict(vehicle_id._fields['state'].selection).items() if k == vehicle_id.state][0],
                    'start_date': (vehicle_id.create_date + timedelta(hours=7)).strftime('%Y-%m-%m %H:%M:%S'),
                    'expire_date': (vehicle_id.expire_date + timedelta(hours=7)).strftime('%Y-%m-%m %H:%M:%S'),
                    'license_plate': vehicle_id.license_plate,
                    'package_description': [match.strip() for match in
                                            re.findall(r'<[^>]+>(.*?)<[^>]+>', vehicle_id.product_id.description)]
                } for vehicle_id in vehicle_ids],
                'histories': [{
                    'license_plate': history.license_plate,
                    'io_type':
                        [v for k, v in dict(history._fields['io_type'].selection).items() if k == history.io_type][0],
                    'io_datetime': (history.io_datetime + timedelta(hours=7)).strftime('%Y-%m-%m %H:%M:%S'),
                    'io_driver': history.driver
                } for history in history_ids]
            }
            return Response(json.dumps(response(status=200, message='Successfully.', data=profile)),
                            headers={'Content-Type': 'application/json'})
        except Exception as e:
            return Response(json.dumps(response(status=500, message=ustr(e))),
                            headers={'Content-Type': 'application/json'})

    @staticmethod
    def _prepare_response_authenticate_in_parking(registered_vehicle_id):
        face_id = request.env['spp.user.face'].sudo().search([('user_id', '=', registered_vehicle_id.user_id.id)])
        payload = {
            'user_id': registered_vehicle_id.user_id.id,
            'license_plate': registered_vehicle_id.license_plate,
            'face_encodings': face_id.face_encoding
        }
        return payload

    @route('/odoo-api/raspberry/authenticate/in_parking', type='http', auth='public', methods=['POST'], csrf=False)
    def authenticate_in_parking(self):
        try:
            params = request.httprequest.args
            license_plate = params.get('license_plate')
            if not license_plate:
                return Response(json.dumps(response(status=400, message='License Plate is required.')),
                                headers={'Content-Type': 'application/json'})
            registered_vehicle_id = request.env['spp.registered.vehicle'].sudo().search([
                ('license_plate', '=', license_plate)
            ])
            if not registered_vehicle_id:
                return Response(json.dumps(response(status=400, message='License Plate not found.')),
                                headers={'Content-Type': 'application/json'})
            elif registered_vehicle_id.state == 'expired':
                return Response(json.dumps(response(status=400, message='Subscription has expired.')),
                                headers={'Content-Type': 'application/json'})
            payload = self._prepare_response_authenticate_in_parking(registered_vehicle_id)
            return Response(json.dumps(response(status=200, message='Successfully.', data=payload)),
                            headers={'Content-Type': 'application/json'})
        except Exception as e:
            return Response(json.dumps(response(status=500, message=ustr(e))),
                            headers={'Content-Type': 'application/json'})

    @route('/odoo-api/raspberry/authenticate/out_parking', type='http', auth='public', methods=['POST'], csrf=False)
    def validate_out_parking(self):
        try:
            ...
        except Exception as e:
            return Response(json.dumps(response(status=500, message=ustr(e))),
                            headers={'Content-Type': 'application/json'})
