import urwid
import asyncio
import random
import string
from datetime import datetime

from cli.autoscrolllistbox import AutoScrollListBox
from cli.eventemitter import EventEmitter
from cli.utils import reify

palette = [
    ('divider', 'black', 'dark cyan', 'standout'),
    ('text', 'light gray', 'default'),
    ('bold_text', 'light gray', 'default', 'bold'),
    ('body', 'text'),
    ('footer', 'text'),
]

for type, bg in (
    ('div_fg_', 'dark cyan'),
    ('', 'default')
):
    for name, color in (
        ('red','dark red'),
        ('blue', 'dark blue'),
        ('green', 'dark green'),
        ('yellow', 'yellow'),
        ('magenta', 'dark magenta'),
        ('gray', 'light gray'),
        ('white', 'white'),
        ('black', 'black')
    ):
        palette.append((type + name, color, bg))


def launch(app, loop):
    screen = urwid.raw_display.Screen()
    screen.register_palette(palette)

    urwid.MainLoop(
        app,
        screen=screen,
        event_loop=urwid.AsyncioEventLoop(loop=loop),
        handle_mouse=False,
    ).run()


class Interface(urwid.WidgetWrap, EventEmitter, metaclass=urwid.MetaSignals):
    signals = ['quit', 'keypress']


    def __init__(self):
        super().__init__(self.widget)


    @reify
    def widget(self):
        frame = urwid.Frame(
            urwid.Frame(
                self.body,
                footer=self.divider
            ),
            footer=self.footer
        )
        self.divider.set_text(('divider', ('Connected.')))
        frame.set_focus('footer')

        return frame


    @reify
    def walker(self):
        return urwid.SimpleListWalker([])


    @reify
    def body(self):
        return urwid.AttrWrap(AutoScrollListBox(self.walker), 'body')


    @reify
    def divider(self):
        return urwid.AttrWrap(urwid.Text('Connecting...'), 'divider')


    @reify
    def footer(self):
        widget = urwid.AttrWrap(urwid.Edit(caption='> '), 'footer')
        widget.set_wrap_mode('space')

        return widget


    def send_message(self, text):
        if not isinstance(text, urwid.Text):
            text = urwid.Text(text)

        self.walker.append(text)
        self.body.scroll_to_bottom()
        pass


    def keypress(self, size, key):
        urwid.emit_signal(self, 'keypress', size, key)

        if key in ('page up', 'page down'):
            self.body.keypress(size, key)
        elif key in ('ctrl d', 'ctrl c'):
            raise urwid.ExitMainLoop()
        elif key == 'enter':
            text = self.footer.get_edit_text()

            self.footer.set_edit_text(' '*len(text))
            self.footer.set_edit_text('')

            if text in ('quit', 'q'):
                raise urwid.ExitMainLoop()

            if text.strip():
                self.emit('message', {
                    'client_msg_id': ''.join(random.choice(string.ascii_letters) for i in range(20)),
                    'user': 'test_user',
                    'channel': '#test',
                    'text': text
                })
        else:
            self.widget.keypress(size, key)

        return key
