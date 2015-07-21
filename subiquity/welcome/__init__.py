# Copyright 2015 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Welcome

Welcome provides user with language selection

"""
import logging
from urwid import (WidgetWrap, ListBox, Pile, BoxAdapter, emit_signal)
from subiquity.ui.lists import SimpleList
from subiquity.ui.buttons import confirm_btn, cancel_btn
from subiquity.ui.utils import Padding, Color

log = logging.getLogger('subiquity.welcome')


class WelcomeModel:
    """ Model representing language selection
    """

    supported_languages = ['English', 'Belgian', 'German', 'Italian']
    selected_language = None

    def __repr__(self):
        return "<Selected: {}>".format(self.selected_language)


class WelcomeView(WidgetWrap):
    def __init__(self, model, signal):
        self.model = model
        self.signal = signal
        self.items = []
        self.body = [
            Padding.center_79(self._build_model_inputs()),
            Padding.line_break(""),
            Padding.center_20(self._build_buttons()),
        ]
        super().__init__(ListBox(self.body))

    def _build_buttons(self):
        self.buttons = [
            Color.button_secondary(cancel_btn(on_press=self.cancel),
                                   focus_map='button_secondary focus'),
        ]
        return Pile(self.buttons)

    def _build_model_inputs(self):
        sl = []
        for lang in self.model.supported_languages:
            sl.append(Color.button_primary(
                confirm_btn(label=lang, on_press=self.confirm),
                focus_map="button_primary focus"))

        return BoxAdapter(SimpleList(sl),
                          height=len(sl))

    def confirm(self, result):
        self.model.selected_language = result.label
        emit_signal(self.signal, 'installpath:show')

    def cancel(self, button):
        raise SystemExit("No language selected, exiting as there are no "
                         "more previous controllers to render.")
