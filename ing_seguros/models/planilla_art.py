# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import Warning
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class PlanillaART(models.Model):
    _name           = 'ing.seguros.planilla.art'
    _order          = 'create_date desc'

    _list_two       = [ ('1','Escoriaciones'),
                        ('2','Heridas punzantes'),
                        ('3','Heridas cortantes'),
                        ('5','Heridas de bala'),
                        ('7','Contusiones'),
                        ('9','Torceduras'),
                        ('10','Luxaciones'),
                        ('11','Fracturas cerradas'),
                        ('12','Amputaciones'),
                        ('14','Quemaduras'),
                        ('15','Cuerpo extraño en ojos'),
                        ('23','Esguinces'),
                        ('24','Fracturas expuestas'),
                        ('27','Perdida auditiva'),
                        ('34','Efectos de cuerpo extraño en oído'),
                        ('35','Efectos de cuerpo extraño en nariz'),
                        ('36','Efectos por picaduras'),
                        ('37','Desgarro')]
    _list_three     = [ ('1','Región craneana'),
                        ('2','Ojos'),
                        ('4','Oído'),
                        ('6','Boca'),
                        ('7','Nariz'),
                        ('9','Cara'),
                        ('15','Cabeza, ubicaciones múltiples'),
                        ('20','Región cervical'),
                        ('23','Tórax'),
                        ('25','Pelvis'),
                        ('30','Hombro'),
                        ('31','Brazo'),
                        ('32','Codo'),
                        ('33','Antebrazo'),
                        ('34','Muñeca'),
                        ('35','Mano'),
                        ('36','Dedos de la mano'),
                        ('40','Cadera'),
                        ('41','Muslo'),
                        ('42','Rodilla'),
                        ('43','Pierna'),
                        ('44','Tobillo'),
                        ('45','Pie'),
                        ('46','Dedos de los pies'),
                        ('126','Testículos'),
                        ('29','Tronco, ubicaciones múltiples'),
                        ('181','Ubicaciones múltiples'),
                        ('190','Cabeza y Cuello'),
                        ('200','Miembros superiores'),
                        ('201','Miembros inferiores')]

    state           = fields.Selection([('draft','Borrador'),('save','Guardado')], default='draft')
    type_accident   = fields.Selection([('AC','Accidente de Trabajo'),('EP','Enfermedad Profesional'),('R','Reingreso')],
                                       string='Tipo de accidente', required=True)
    employee_id     = fields.Many2one('hr.employee', string='Empleado', required=True,
                                      domain='[("tipo_contrato_id","in",["Planta Temporaria","Planta Permanente"])]')
    regular_shift   = fields.Selection([('F','Fijo'),('R','Rotativo')], required=True, string='Turno Habitual')
    init_hour_day   = fields.Float('Hora inicio', required=True)
    end_hour_day    = fields.Float('Hora fin', required=True)
    init_day_accide = fields.Float('Inicio de Jornada el dia del accidente', required=True)
    date_accident   = fields.Date('Fecha del accidente', required=True)
    hour_accident   = fields.Float('Hora del accidente', required=True)
    detail_accident = fields.Text('Detalle del accidente', required=True)
    cod_pos         = fields.Char('Codigo Postal', required=True)
    location        = fields.Char('Localidad', required=True)
    edad            = fields.Integer('Edad', compute='_calcule_edad', store=False, required=True)
    form_accident   = fields.Selection([('101','Caídas de personas por caídas desde alturas'),
                                        ('102','Caídas de personas por caídas en profundidades'),
                                        ('201','Derrumbe (caídas de tierra, de rocas, de piedra, de nieve)'),
                                        ('203','Caídas de objetos en curso de manutencion manual'),
                                        ('301','Pisada sobre objetos'),
                                        ('302','Coques contra objetos inmóviles'),
                                        ('304','Golpes por objetos inmóviles'),
                                        ('401','Atrapamiento por un objeto'),
                                        ('501','Esfuerzos físicos excesivos al levantar objetos'),
                                        ('502','Esfuerzos físicos excesivos al empujar objetos'),
                                        ('601','Exposicion al calor (de la atmósfera o del ambiente de trabajo)'),
                                        ('602','Exposicion al frío (de la atmósfera o del ambiente de trabajo)'),
                                        ('603','Contacto con sustancias u objetos calientes'),
                                        ('605','Contacto con fuego'),
                                        ('702','Contacto con fuente de generación o transmición eléctrica'),
                                        ('801','Contacto por inhalación de sustancias químicas'),
                                        ('802','Contacto por ingestión de sustancias químicas'),
                                        ('902','Incendio'),
                                        ('903','Atropellamiento de animales'),
                                        ('904','Mordedura de animales'),
                                        ('905','Picaduras'),
                                        ('906','Atropellamiento por vehículos'),
                                        ('907','Choque por vehículos'),
                                        ('909','Agresión con armas'),
                                        ('910','Agresión sin armas'),
                                        ('911','Injuria punzo-cortante o contusa involuntaria')],
                                       string='Forma del Accidente', required=True)
    material_agent  = fields.Selection([('10702','Correas, Cables, Poleas, Cadenas'),
                                        ('10703','Generadores de energía eléctrica'),
                                        ('10801','Maquinarias para agricultura'),
                                        ('10802','Maquinarias para ganadería'),
                                        ('10803','Tractores, Tractores con remolque'),
                                        ('10916','Maquinarias para el trabajo de metales'),
                                        ('10919','Maquinarias para la cosntrucción'),
                                        ('31501','Cañerías de Gas, Aire, Agua, etc.'),
                                        ('20001','Camiones'),
                                        ('20006','Automóviles'),
                                        ('20007','Motocicletas'),
                                        ('20008','Bicicletas'),
                                        ('30800','Cámaras (incluye cámaras frigoríficas)'),
                                        ('60800','Insectos, Arácnidos, Serpientes'),
                                        ('61000','Residuos'),
                                        ('30906','Estanterías'),
                                        ('60300','Árboles, Plantas, Cultivos'),
                                        ('31304','Herramientas manuales'),
                                        ('31402','Andamios'),
                                        ('20101','Grúas'),
                                        ('40201','Polvos'),
                                        ('40203','Líquidos'),
                                        ('40204','Productos químicos'),
                                        ('50103','Agua (ambiente de trabajo externo)'),
                                        ('31006','Calderas'),
                                        ('50107','Ruido (ambiente de trabajo externo)'),
                                        ('50108','Fuego (ambiente de trabajo externo)'),
                                        ('50109','Humo'),
                                        ('50201','Pisos'),
                                        ('50203','Escaleras'),
                                        ('50205','Aberturas'),
                                        ('50208','Ruido (ambiente de trabajo interno)'),
                                        ('50209','Agua (ambiente de trabajo interno)'),
                                        ('50210','Fuego (ambiente de trabajo interno)'),
                                        ('30901','Silos'),
                                        ('60100','Arma de fuego'),
                                        ('60200','Arma blanca'),
                                        ('31001','Altos hornos'),
                                        ('60600','Animelas de cría'),
                                        ('61700','Personas')],
                                       string='Agente material asociado', required=True)
    affected_zone   = fields.Selection(_list_three, string='Zona del cuerpo afectada', required=True)
    affected_zone2  = fields.Selection(_list_three)
    affected_zone3  = fields.Selection(_list_three)
    nature_injury   = fields.Selection(_list_two, string='Naturaleza de la lesion', required=True)
    nature_injury2  = fields.Selection(_list_two)
    nature_injury3  = fields.Selection(_list_two)

    def _calcule_edad(self):
        self.edad = relativedelta(datetime.now(), self.employee_id.birthday).years

    def name_get(self):
        return [(record.id, str(record.employee_id.name) + '-' + str(record.date_accident)) for record in self]

    @api.model
    def create(self, vals):
        vals['state'] = 'save'
        return super().create(vals)

    def print_planilla(self):
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": f"/report/html/ing_seguros.planilla_art_template/{self.id}?context=%7B%22lang%22%3A%22es_ES%22%2C%22tz%22%3A%22America%2FBuenos_Aires%22%2C%22uid%22%3A274%2C%22allowed_company_ids%22%3A%5B1%5D%7D",
        }
