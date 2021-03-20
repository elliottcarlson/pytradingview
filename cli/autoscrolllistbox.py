import urwid

class AutoScrollListBox(urwid.ListBox, metaclass=urwid.MetaSignals):
    signals = ['set_auto_scroll']

    @property
    def auto_scroll(self):
        return self._auto_scroll


    @auto_scroll.setter
    def auto_scroll(self, switch: bool):
        self._auto_scroll = switch
        urwid.emit_signal(self, 'set_auto_scroll', switch)


    def __init__(self, body):
        super(AutoScrollListBox, self).__init__(body)
        self.auto_scroll = True


    def switch_body(self, body):
        if self.body:
            urwid.disconnect_signal(body, 'modified', self._invalidate)

        self.body = body
        self._invalidate()

        urwid.connect_signal(body, 'modified', self._invalidate)


    def keypress(self, size, key):
        urwid.ListBox.keypress(self, size, key)

        if key in ('page up', 'page down'):
            if self.get_focus()[1] == len(self.body)-1:
                self.auto_scroll = True
            else:
                self.auto_scroll = False


    def scroll_to_bottom(self):
        if self.auto_scroll:
            self.set_focus(len(self.body)-1)
