
import base64
import binascii
import hmac
import logging
import time
import urllib
import urlparse
import uuid

from tornado import escape, httpclient
from tornado.auth import OAuthMixin, _oauth_parse_response, _oauth_signature
from tornado.util import bytes_type, b

class NetflixMixin(OAuthMixin):

    _OAUTH_REQUEST_TOKEN_URL = "http://api.netflix.com/oauth/request_token"
    _OAUTH_ACCESS_TOKEN_URL = "http://api.netflix.com/oauth/access_token"
    # _OAUTH_AUTHORIZE_URL = "http://api.netflix.com/oauth/authorize"
    _OAUTH_AUTHORIZE_URL = "https://api-user.netflix.com/oauth/login"
    _OAUTH_AUTHENTICATE_URL = "http://api.netflix.com/oauth/authenticate"
    _OAUTH_VERSION = '1.0'
    _OAUTH_NO_CALLBACKS = False

# oauth_token=n9gs3sfnk3xubrg5znubxeza&oauth_token_secret=C6s64cxGkXet&application_name=Green+Eggs&login_url=https%3A%2F%2Fapi-user.netflix.com%2Foauth%2Flogin%3Foauth_token%3Dn9gs3sfnk3xubrg5znubxeza

    def netflix_api(self, path, callback, access_token=None, post_args=None,
                        **kwargs):
        if path.startswith('http:') or path.startswith('https:'):
            url = path
        else:
            url = "http://api.netflix.com/" + path
        # Add the OAuth resource request signature if we have credentials
        if access_token:
            all_args = {}
            all_args.update(kwargs)
            all_args.update(post_args or {})
            method = "POST" if post_args is not None else "GET"
            oauth = self._oauth_request_parameters(
                url, access_token, all_args, method=method)
            kwargs.update(oauth)
        if kwargs:
            url += "?" + urllib.urlencode(kwargs)
        callback = self.async_callback(self._on_netflix_request, callback)
        http = httpclient.AsyncHTTPClient()
        if post_args is not None:
            http.fetch(url, method="POST", body=urllib.urlencode(post_args),
                       callback=callback)
        else:
            http.fetch(url, callback=callback)

    def _on_netflix_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error,
                            response.request.url)
            callback(None)
            return
        callback(escape.json_decode(response.body))

    def _oauth_get_user(self, access_token, callback):
        self.netflix_api(
            "users/current",
            access_token=access_token,
            callback=callback
            )

    def _oauth_consumer_token(self):
        self.require_setting("netflix_consumer_key", "Netflix OAuth")
        self.require_setting("netflix_consumer_secret", "Netflix OAuth")
        self.require_setting("netflix_callback_uri", "Netflix OAuth")
        x = dict(
            key=self.settings["netflix_consumer_key"],
            secret=self.settings["netflix_consumer_secret"])
        print "X", x
        return x


    # OAUTH 1.0 Y U NO TAKE extra_params
    def _oauth_request_token_url(self, callback_uri=None, extra_params=None):
        consumer_token = self._oauth_consumer_token()
        url = self._OAUTH_REQUEST_TOKEN_URL
        args = dict(
            oauth_consumer_key=escape.to_basestring(consumer_token["key"]),
            oauth_signature_method="HMAC-SHA1",
            oauth_timestamp=str(int(time.time())),
            oauth_nonce=escape.to_basestring(binascii.b2a_hex(uuid.uuid4().bytes)),
            oauth_version=getattr(self, "_OAUTH_VERSION", "1.0a"),

        )
        if getattr(self, "_OAUTH_VERSION", "1.0a") == "1.0a":
            if callback_uri == "oob":
                args["oauth_callback"] = "oob"
            elif callback_uri:
                args["oauth_callback"] = urlparse.urljoin(
                    self.request.full_url(), callback_uri)
            if extra_params:
                args.update(extra_params)
            signature = _oauth10a_signature(consumer_token, "GET", url, args)
        else:
            signature = _oauth_signature(consumer_token, "GET", url, args)

        args["oauth_signature"] = signature
        x = url + "?" + urllib.urlencode(args)
        print "XXX", x
        return x

    def _on_request_token(self, authorize_url, callback_uri, response):
        if response.error:
            raise Exception("Could not get request token")
        consumer_token = self._oauth_consumer_token()
        request_token = _oauth_parse_response(response.body)
        data = (base64.b64encode(request_token["key"]) + b("|") +
                base64.b64encode(request_token["secret"]))
        self.set_cookie("_oauth_request_token", data)
        args = dict(
                oauth_token=request_token["key"],
                oauth_consumer_key=escape.to_basestring(consumer_token['key']),
                )
        if callback_uri == "oob":
            self.finish(authorize_url + "?" + urllib.urlencode(args))
            return
        elif callback_uri:
            args["oauth_callback"] = urlparse.urljoin(
                self.request.full_url(), callback_uri)
        self.redirect(authorize_url + "?" + urllib.urlencode(args))

