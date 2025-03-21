from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    @api.model
    def create(self, vals):
        project = super().create(vals)

        # Tạo External ID cho project vừa tạo
        self.env['ir.model.data'].create({
            'name': f'project_project_{project.id}',
            'module': 'project',
            'model': 'project.project',
            'res_id': project.id,
        })
        
        return project
