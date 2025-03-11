{
    'name': 'Custom Discuss Gmail Integration',
    'version': '1.0',
    'summary': 'Extend Discuss module with Gmail inbox integration',
    'description': 'Fetch and display Gmail inbox messages in the Discuss module',
    'author': 'Your Name',
    'website': 'https://crm2.wsoftpro.com',
    'category': 'Communication',
    'depends': ['mail'],
    'data': [
        'views/discuss_view.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'custom_gmail/static/src/css/gmail_inbox.css',
            'custom_gmail/static/src/css/compose_modal.css',
            'custom_gmail/static/src/js/GmailInbox.js',
            'custom_gmail/static/src/js/state.js',
            'custom_gmail/static/src/js/functions/loadMessages.js',
            'custom_gmail/static/src/js/functions/toggleStar.js',
            'custom_gmail/static/src/js/functions/onReply.js',
            'custom_gmail/static/src/js/functions/onReplyAll.js',
            'custom_gmail/static/src/js/functions/onForward.js',
            'custom_gmail/static/src/js/functions/openComposeModal.js',
            'custom_gmail/static/src/js/functions/fillComposeForm.js',
            'custom_gmail/static/src/js/functions/onSendEmail.js',
            'custom_gmail/static/src/js/functions/index.js', 
            'custom_gmail/static/src/js/uiUtils.js',
            'custom_gmail/static/src/js/storageUtils.js',
            'custom_gmail/static/src/js/ckeditor.js',
            'custom_gmail/static/src/js/template.js',
        ]
    },
    'installable': True,
    'application': False,
}
