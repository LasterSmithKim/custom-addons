from odoo import api, fields, models
from odoo.exceptions import Warning
import isbnlib


class Machine(models.Model):
    _name = 'goods.machine'
    _description = 'Machine'
    name = fields.Char('Title', required=True)
    code = fields.Char('CodeNb')
    active = fields.Boolean('Active?', default=True)
    isactive = fields.Boolean('IsActive?', default=True)
    date_issue = fields.Date()
    image = fields.Binary('Cover')
    cooking_luhn = fields.Char(compute='_cooking_luhn', store=True) #存储计算字段，使其可以被检索

    @api.multi
    def _check_code(self):
        self.ensure_one()
        code = self.code.replace('-', '')  # 为保持兼容性 Alan 自行添加
        digits = [int(x) for x in code if x.isdigit()]  # 可能是清洗数据为 如果是数字的遍历对象都int化拼接成新整数
        if len(digits) == 13:
            ponderations = [1, 3] * 6
            terms = [a * b for a, b in zip(digits[:12], ponderations)]
            remain = sum(terms) % 10
            check = 10 - remain if remain != 0 else 0
            return digits[-1] == check

    @api.multi
    def _check_luhn(self):  #验证校验位是否正确
        self.ensure_one()
        code = self.code.replace('-', '') #清理数据 -
        digits = [int(x) for x in code if x.isdigit()]
        s = 0
        digits_length = len(digits)
        for _ in range(1,digits_length + 1):
            t = int(digits[digits_length - _])
            if _ % 2 == 0:
                t *= 2
                s += t if t < 10 else t % 10 + t // 10
            else:
                s += t
        return s % 10 == 0

    @api.depends('code')
    def _cooking_luhn(self):  # 已知code求校验位 与check_luhn奇偶数位相反
        for machine in self:
            code = machine.code.replace('-', '') #清理数据 -
            digits = [int(x) for x in code if x.isdigit()]
            s = 0
            digits_length = len(digits)
            for _ in range(1,digits_length + 1):
                t = int(digits[digits_length - _])
                if _ % 2 == 0:
                    s += t
                else:
                    t *= 2
                    s += t if t < 10 else t % 10 + t // 10
            machine.cooking_luhn = 10 - s % 10

    @api.multi
    def button_check_isbn(self):
        for machine in self:
            if not machine.code:
                raise Warning('Please provide an Code for %s' % machine.name)
            #if machine.code and not machine._check_code():
            if machine.code and not machine._check_luhn():
                raise Warning('%s is an invalid Code' % machine.code)
                return True
