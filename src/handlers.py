import tornado.web
import jinja2
import traceback
import base64
import random
import string


class BaseHandler(tornado.web.RequestHandler):
    """
    Base handler for application
    """
    def initialize(self, ctx, *args, **kwargs):
        """
        init handler

        Parameters
        ----------
        ctx: Context
        """
        super().initialize(*args, **kwargs)
        self.ctx = ctx
        self.ctx.base_path = "/"

    def prepare(self):
        """
        Prepare before each request
        """
        super().prepare()

    def on_finish(self):
        """
        On finish of each request log message
        """
        self.ctx.lgr.info(
            "%s %s from %s [%.3f ms]",
            self.request.method,
            self.request.uri,
            self.request.remote_ip,
            self.request.request_time()*1000,
        )


class JinjaHandler(BaseHandler):
    """
    Base handler for all Jinja handlers

    * render templates
    * support flash messages
    * on error write custom page
    """
    def initialize(self, *args, **kwargs):
        """
        Init handler
        """
        super().initialize(*args, **kwargs)
        self.__flash_messages = []

    def write_error(self, status_code, **kwargs):
        """
        Write error if occurs

        Parameters
        ----------
        status_code: int
        """
        level = self.ctx.lgr.error
        if status_code in (403, 404, 405):
            level = self.ctx.lgr.warning
        level("returning status code '%d' because '%s'", status_code, kwargs)

        super().prepare()  # manually prepare
        message = self._reason
        trace = None
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            trace = "".join(
                traceback.format_exception(*kwargs["exc_info"])
            )
        # egg
        code = ''.join(random.choice(string.ascii_lowercase + string.digits)
                       for _ in range(400))

        self.render(
            "error.html",
            status_code=status_code,
            message=message,
            traceback=trace,
            code=base64.b64encode(code.encode("utf-8")).decode("utf-8"),
        )

    def flash_message(self, type, message, *args):
        """
        Save flash_message for future use - save to cookie as base64(json(...))

        Parameters
        ----------
        type: str
            type of message

        message:
            formating string of message

        *args:
            arguments of message, used with formating string
        """
        self.__flash_messages.append((type, message, args,))
        self.set_cookie("flashmessages", base64.b64encode(
            tornado.escape.json_encode(self.__flash_messages).encode('utf-8')))

    def prepare(self, *args, **kwargs):
        """
        Prepare before each request

        Load flash messages from cookie
        """
        super().prepare(*args, **kwargs)
        fm = self.get_cookie("flashmessages")
        if fm:
            # list of tuples, where 3th argument (data) is tuple as well
            self.__flash_messages = \
                list(
                    map(
                        lambda x: (x[0], x[1], tuple(x[2])),
                        tornado.escape.json_decode(
                            base64.b64decode(fm).decode("utf-8")
                        )
                    )
                )

    def render(self, template_path=None, **kwargs):
        """
        Render template

        Clear flash messages from cookie - we are rendering, prepare template,
        render

        Parameters
        ----------
        template_path: str|None
            path to template or None = load default (class_name+.html)
        """
        self.clear_cookie("flashmessages")  # delete when rendering
        if template_path is None:
            template_path = self.__class__.__name__+".html"

        try:
            template = self.ctx.env.get_template(template_path)
        except jinja2.TemplateNotFound:
            raise

        kwargs['flash_messages'] = self.__flash_messages
        self.__flash_messages = []  # rendered
        kwargs['base_path'] = self.ctx.base_path
        kwargs['uri'] = self.request.uri
        kwargs.update(self.get_template_namespace())  # tornado template funcs
        content = template.render(kwargs)
        self.write(content)


class Homepage(JinjaHandler):
    def get(self):
        """
        GET method

        show homepage
        """
        self.render(ultimate_answer=42)


class NotFoundHandler(tornado.web.ErrorHandler, JinjaHandler):
    """
    404 not found handler
    """
    def initialize(self, *args, **kwargs):
        """
        Init handler as JinjaHandler
        """
        tornado.web.ErrorHandler.initialize(self, 404)
        JinjaHandler.initialize(self, *args, **kwargs)
