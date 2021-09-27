import pathlib
from flask_dotenv import DotEnv
import os
import sys
import common.logging

class Config:

    @classmethod
    def init_app(self, app):
        #########################################
        ##source  Load .ENV variables
        env = DotEnv()
        env.init_app(app, verbose_mode=True)
        env.eval(keys={
            'MAIL_PORT': int,
            'MAIL_USE_TLS': bool,
            'ADMINS': list
        })

        #########################################
        for hdlr in app.logger.handlers[:]:  # remove all old handlers
            app.logger.removeHandler(hdlr)

        common.logging.configure_logging()

        # if (not app.debug):
        #     auth = None
        #     if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
        #         auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        #     secure = None
        #     if app.config['MAIL_USE_TLS']:
        #         secure = ()
        #     mail_handler = SMTPHandler(
        #         mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        #         fromaddr='no-reply@embo.org',
        #         toaddrs=app.config['ADMINS'],
        #         subject='[smtag_api] ERROR',
        #         credentials=auth,
        #         secure=secure
        #     )
        #     Config.add_logger(app, mail_handler, level=logging.ERROR)

        ## Done
        app.config['JSON_SORT_KEYS'] = False
        app.logger.info("CONFIG LOADED")
