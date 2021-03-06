import pathlib
from flask_dotenv import DotEnv
import os
import sys
import logging
from logging.handlers import RotatingFileHandler


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
        ## Setup loggers
        if not os.path.exists('log'):
            os.mkdir('log')
        for hdlr in app.logger.handlers[:]:  # remove all old handlers
            app.logger.removeHandler(hdlr)
        Config.add_logger(app, logging.StreamHandler(stream=sys.stdout), level='DEBUG')
        Config.add_logger(app, RotatingFileHandler('log/neoflask.log', maxBytes=10240, backupCount=10))
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
        app.logger.info("CONFIG LOADED")

    @classmethod
    def add_logger(self, app, handler, level=None):
        formatter = logging.Formatter('[%(levelname)s %(asctime)s %(name)s] %(pathname)s:%(lineno)d: %(message)s')
        if (not level):
            level = logging.DEBUG if app.debug else logging.INFO
        handler.setFormatter(formatter)
        handler.setLevel(level)
        app.logger.addHandler(handler)
