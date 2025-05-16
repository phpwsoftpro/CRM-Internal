from odoo.api import Environment, SUPERUSER_ID

def post_init_hook_set_outlook_config(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    env['outlook.config.setup'].set_outlook_config_params()
