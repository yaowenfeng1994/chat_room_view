#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from handlers.base import BaseHandler


class ChatRoomHandler(BaseHandler):
    def get(self, *args, **kwargs):
        if self.token.is_login and not self.token.token_expire:
            print(self.token.nickname)
            if len(self.token.nickname) > 0:
                username = self.token.nickname
            else:
                username = self.token.account
            self.render("chat_room.html", username=username)
        else:
            self.render("login.html")
