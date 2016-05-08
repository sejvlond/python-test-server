"""
Simple test server

Usage:
    server.py -c CONFIG_FILE

Options:
    -c CONFIG_FILE      configuration file
"""
import docopt
import sys
import os
import jinja2
import tornado.log
import schema
import logging
import yaml
import tornado.ioloop
import tornado.web
import tornado.httpserver

from dictobj import DictObj
import handlers
import filters


class Context(DictObj):
    """
    Context object for server. Includes config, logger and jinja enviroment
    """
    pass


def jinja_filters():
    """
    Jinja filters used in templates

    Returns
    -------
    dict
        name: func
    """
    return {
        "nl2br": filters.nl2br,
        "str": filters.str_,
        "datetime": filters.datetime,
        "timedelta": filters.timedelta,
    }


def guess_autoescape(template_name):
    """
    Guess if we want to espace template by its extension (xml, htm[l], -> Yes)

    Parameters
    ----------
    template_name: string
        path to template file

    Returns
    -------
    bool
        escape or not
    """
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')


def start(ctx):
    """
    Start server

    Parameters
    ----------
    ctx: Context
    """
    root_dir = os.path.abspath(os.path.dirname(__file__))
    templ_dir = os.path.join(root_dir, "templates")
    static_dir = os.path.join(root_dir, "static")

    env = jinja2.Environment(
        autoescape=guess_autoescape,
        loader=jinja2.FileSystemLoader([templ_dir]),
        extensions=['jinja2.ext.autoescape'],
    )
    env.filters.update(jinja_filters())
    ctx.env = env

    dispatch_table = [
        (r"/", handlers.Homepage, dict(ctx=ctx)),
        (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=static_dir)),
    ]

    app = tornado.web.Application(
        dispatch_table,
        debug=ctx.cfg["debug"],
        xsrf_cookies=True,
        default_handler_class=handlers.NotFoundHandler,
        default_handler_args=dict(ctx=ctx))
    svr = tornado.httpserver.HTTPServer(app)
    svr.bind(ctx.cfg["port"])
    svr.start(ctx.cfg["processes"])
    tornado.ioloop.IOLoop.current().start()


def create_logger():
    """
    Prepars logger

    Returns
    -------
    logging.Logger
    """
    lgr = logging.getLogger("SERVER")
    lgr.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()  # stdout logging
    # Formatting
    fmt = logging.Formatter('%(asctime)s %(levelname)s: %(message)s'
                            ' {%(module)s:%(funcName)s:%(lineno)d}')
    sh.setFormatter(fmt)  # Set format for stdout
    lgr.addHandler(sh)  # Add output to stdout
    return lgr


def main():
    """
    Main func of this module
    """
    ctx = Context()
    ctx.lgr = create_logger()
    args = docopt.docopt(__doc__)
    sch = schema.Schema({
        "port": int,
        "processes": int,
        "debug": bool,
    })

    with open(args["-c"], 'r') as stream:
        try:
            data_cfg = yaml.load(stream)
        except yaml.YAMLError as exc:
            ctx.lgr.critical(exc)
            sys.exit(1)

    try:
        sch.validate(data_cfg)
    except schema.SchemaError as exc:
        ctx.lgr.critical(exc)
        sys.exit(1)

    ctx.cfg = data_cfg
    try:
        ctx.lgr.info("==== SERVER started ====")
        start(ctx)
        ctx.lgr.info("==== SERVER finished ====")
    except Exception as exc:
        ctx.lgr.critical("Server failed: '%s'", str(exc), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
