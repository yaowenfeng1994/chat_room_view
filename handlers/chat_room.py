#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from handlers.base import BaseHandler


class ChatRoomHandler(BaseHandler):
    def get(self, *args, **kwargs):
        if self.token.is_login and not self.token.token_expire:
            print(self.token.nickname)
            self.render("chat_room.html")
        else:
            self.render("login.html")
