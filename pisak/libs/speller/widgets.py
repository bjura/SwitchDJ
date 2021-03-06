'''
Definitions of widgets specific to speller applet
'''
import re

from gi.repository import Clutter, Mx, GObject, Pango

from pisak import res
from pisak.libs import unit, layout, properties, scanning, configurator, \
    style, text_tools
from pisak.libs.speller.prediction import predictor
import pisak.libs.widgets


class CursorGroup(layout.Bin, configurator.Configurable):
    """
    Object linking text cursor with its target text box.
    """
    __gtype_name__ = "PisakCursorGroup"

    def __init__(self):
        super().__init__()
        self.connect("notify::mapped", self.init_content)
        self.first_run = True
        self.apply_props()

    def init_content(self, *args):
        self.label = [i for i in self.get_children()
                     if type(i) == Text][0]
        self.label.clutter_text.connect('text-changed', self.move_cursor)
        self.label.clutter_text.connect('cursor-changed', self.move_cursor)

    def init_cursor(self):
        font_name = self.label.clutter_text.get_font_name()
        for i in font_name.split():
            try:
                self.cursor_height = unit.pt_to_px(int(i))
            except ValueError:
                if 'px' in i:
                    self.cursor_height = int(i.strip('px'))
                else:
                    pass
        self.cursor_height = round(self.cursor_height)
        self.label.clutter_text.set_cursor_size(self.cursor_height)
        self.cursor = Cursor((5, self.cursor_height))
        self.cursor.set_depth(10)
        self.add_child(self.cursor)
        self.cursor.set_x(0)
        self.cursor.set_y(0)

    def move_cursor(self, event):
        if self.first_run:
            self.init_cursor()
            self.first_run = False
        cursor_pos = self.label.clutter_text.get_cursor_position()
        coords = self.label.clutter_text.position_to_coords(cursor_pos)
        y_offset = self.label.margin.top
        x_offset = self.label.margin.left
        self.cursor.set_x(coords[1] + x_offset)
        self.cursor.set_y(
            coords[2]-self.label.get_children()[1].get_adjustment().get_value() +
            y_offset)
        
class Cursor(Clutter.Actor):
    """
    Widget displaying text cursor drawn on ClutterCanvas.
    """
    def __init__(self, size):
        super().__init__()
        self.width = size[0]
        self.height = size[1]
        self.set_size(self.width, self.height)
        self.canvas = Clutter.Canvas()
        self.canvas.set_size(self.width, self.height)
        self.canvas.connect('draw', self.draw)
        self.canvas.invalidate()
        self.set_content(self.canvas)

    @staticmethod
    def draw(canvas, context, width, height):
        context.set_source_rgb(0, 0, 0)
        context.rectangle(0, 0, width, height)
        context.fill()
        return True

class Text(Mx.ScrollView, properties.PropertyAdapter, configurator.Configurable,
           style.StylableContainer):
    """
    Speller specific text box where all the text operations happen.

   Properties:

   * :attr:`ratio_width`
   * :attr:`ratio_height`

    """
    class Insertion(object):
        """
        Text replacement operation
        """
        def __init__(self, pos, value):
            """
            Creates text insertion

            :param: pos absolute position of insertion

            :param: value nonempty string to be inserted
            """
            self.pos = pos
            self.value = value
            assert self.pos >= 0, "Invalid position"
            assert len(self.value) > 0, "Invalid insertion"

        def apply(self, text):
            text.clutter_text.insert_text(self.value, self.pos)

        def revert(self, text):
            end = self.pos + len(self.value)
            text.clutter_text.delete_text(self.pos, end)

        def compose(self, operation):
            if isinstance(operation, Text.Insertion):
                consecutive = self.pos + len(self.value) == operation.pos
                compatible = not self.value[-1].isspace() or \
                    operation.value[0].isspace()
                if consecutive and compatible:
                    self.value = self.value + operation.value
                    return True
                else:
                    return False
            else:
                return False

        def __str__(self):
            return "+ {} @ {}".format(self.value, self.pos)

    class Deletion(object):
        """
        Text deletion operation
        """
        def __init__(self, pos, value):
            """
            Creates text deletion

            :param: pos absolute position of deletion

            :param: value nonempty string to be deleted
            """
            self.pos = pos
            self.value = value
            assert pos >= 0, "Invalid position"
            assert len(self.value), "Invalid deletion"

        def apply(self, text):
            end = self.pos + len(self.value)
            text.clutter_text.delete_text(self.pos, end)

        def revert(self, text):
            text.clutter_text.insert_text(self.value, self.pos)

        def compose(self, operation):
            if isinstance(operation, Text.Deletion):
                consecutive = operation.pos + len(operation.value) == self.pos
                compatible = operation.value[-1].isspace() or \
                    not self.value[0].isspace()
                if consecutive and compatible:
                    self.pos = operation.pos
                    self.value = operation.value + self.value
                    return True
                else:
                    return False
            else:
                return False

        def __str__(self):
            return "- {} @ {}".format(self.value, self.pos)

    class Replacement(object):
        """
        Replacement operation
        """
        def __init__(self, pos, before, after):
            """
            Creates text insertion

            :param: pos position of replacement
            :param: before nonempty string to be deleted
            :param: after nonemty string to be inserted
            """
            self.pos = pos
            self.before = before
            self.after = after
            assert pos >= 0, "Invalid position"

        def _replace(self, text, before, after):
            text.clutter_text.delete_text(self.pos, self.pos + len(before) + 1)
            text.clutter_text.insert_text(after, self.pos)

        def apply(self, text):
            self._replace(text, self.before, self.after)

        def revert(self, text):
            self._replace(text, self.after, self.before)

        def compose(self, *args):
            return False

        def __str__(self):
            return "{} -> {} @ {}".format(self.before, self.after, self.pos)

    __gtype_name__ = "PisakScrolledText"
    __gproperties__ = {
        "ratio_width": (GObject.TYPE_FLOAT, None, None, 0, 1., 0, GObject.PARAM_READWRITE),
        "ratio_height": (GObject.TYPE_FLOAT, None, None, 0, 1., 0, GObject.PARAM_READWRITE)}

    def __init__(self):
        super().__init__()
        self.history = []
        self._init_text()
        self.line = 0
        self.prepare_style()

    def _init_text(self):
        self.box = Mx.BoxLayout()
        self.box.set_orientation(Mx.Orientation.VERTICAL)
        self.box.set_scroll_to_focused(True)
        self.text = Mx.Label()
        self.margin = Clutter.Margin.new()
        self.margin.top = 20
        self.margin.left = self.margin.right = 10
        self.text.set_margin(self.margin)
        self.box.add_actor(self.text, 0)
        self.clutter_text = self.text.get_clutter_text()
        self.clutter_text.connect("text-changed", self.check_to_resize)
        self.clutter_text.connect("cursor-changed", self.scroll_to_view)
        self.clutter_text.connect("text-changed", self.scroll_to_view)
        self._set_text_params()
        self.add_actor(self.box)
        self.connect("notify::mapped", self._adjust_view)

    def add_operation(self, operation):
        if len(self.history) == 0 or not self.history[-1].compose(operation):
            self.history.append(operation)
        operation.apply(self)

    def revert_operation(self):
        if len(self.history) > 0:
            self.history.pop().revert(self)

    def _adjust_view(self, source, event):
        self.text.set_height(self.text.get_height() - self.margin.top)

    def _set_text_params(self):
        self.clutter_text.set_editable(True)
        self.clutter_text.set_line_wrap(True)
        self.clutter_text.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)

    def get_text(self):
        """
        Return the entire text from the text buffer
        """
        return self.clutter_text.get_text()

    def get_text_length(self):
        """
        Return the number of characters in the text buffer
        """
        return len(self.clutter_text.get_text())

    def get_cursor_position(self):
        pos = self.clutter_text.get_cursor_position()
        return pos if pos >= 0 else self.get_text_length()

    def check_to_resize(self, *args):
        pango_layout = self.clutter_text.get_layout()
        pango_height = pango_layout.get_size()[1] / Pango.SCALE
        label_height = self.text.get_size()[1]
        font_height = re.findall(r'\d+',
                                 self.clutter_text.get_font_name())[0]
        font_height = int(font_height)
        if label_height <= pango_height + font_height:
            self.text.set_height(self.text.get_height() + unit.h(self.ratio_height))
        elif label_height > pango_height + unit.h(self.ratio_height) + font_height:
            self.text.set_height(self.text.get_height() - unit.h(self.ratio_height))

    def scroll_to_view(self, *args):
        pos = self.get_cursor_position()
        scroll_bar = self.get_children()[1]
        adj = scroll_bar.get_adjustment()
        coords = self.clutter_text.position_to_coords(pos)
        adj.set_value(coords[2] - 3*unit.h(self.ratio_height)/4)
        scroll_bar.set_adjustment(adj)
        
    def type_text(self, text):
        """
        Insert the given text to the text buffer on the
        current cursor position

        :param: text string passed after a user's actions
        """
        pos = self.get_cursor_position()
        operation = Text.Insertion(pos, text)
        self.add_operation(operation)

    def type_unicode_char(self, char):
        """
        Append the given unicode character to the text buffer

        :param char: unicode character in the form of unicode escape sequence
        :deprecated:
        """
        # TODO: remove
        operation = Text.Insertion(self.get_text_length(), char)
        self.add_operation(operation)

    def delete_char(self):
        """
        Delete the single character from behind the
        current cursor position
        """
        pos = self.get_cursor_position()
        if pos == 0:
            return
        elif pos > 0:
            pos -= 1
        text = self.get_text()[pos]
        operation = Text.Deletion(pos, text)
        self.add_operation(operation)

    def delete_text(self, start_pos, end_pos):
        """
        Delete all characters from positions from the given range

        :param start_pos: start position given in characters
        :param end_pos: end position given in characters
        """
        self.clutter_text.delete_text(start_pos, end_pos)

    def clear_all(self):
        """
        Clear the entire text buffer
        """
        text = self.get_text()
        if len(text) > 0:
            operation = Text.Deletion(0, self.get_text())
            self.add_operation(operation)

    def get_endmost_string(self):
        """
        Look for and return the first string of characters with no whitespaces
        starting from the end of the text buffer
        """
        text = self.get_text()
        stripped_text = text.rstrip()
        start_pos = stripped_text.rfind(' ') + 1
        end_pos = len(stripped_text)
        return text[start_pos : end_pos]

    def replace_endmost_string(self, text_after):
        """
        Look for the first string of characters with no whitespaces starting
        from the end of the text buffer and replace it with the given text

        :param text_after: string passed after a user's action
        """
        current_text = self.get_text()
        # if the text buffer is empty, or ends with whitespace, simply
        # add predicted words. Otherwise, replace the last word.
        if current_text:
            # if the text buffer ends in a commas, add a space before
            # adding the predicted word
            if current_text[-1] in ['.', ',', ';', '?', '!', '(', ')', ':', '"']:
                self.type_text(' ' + text_after)
            elif current_text[-1] == ' ':
                self.type_text(text_after)
            else:
                stripped_text = current_text.rstrip(" ")
                start_pos = max(stripped_text.rfind(' '),
                                stripped_text.rfind("\n")) + 1
                text_before = current_text[start_pos : -1]
                operation = Text.Replacement(start_pos, text_before, text_after)
                self.add_operation(operation)
        else:
            self.type_text(text_after)

    def move_cursor_forward(self):
        """
        Move cursor one position forward
        """
        current_position = self.get_cursor_position()
        if current_position < self.get_text_length():
            self.clutter_text.set_cursor_position(current_position+1)
            
    def move_cursor_backward(self):
        """
        Move cursor one position backward
        """
        current_position = self.get_cursor_position()
        text_length = self.get_text_length()
        if current_position > 0:
            self.clutter_text.set_cursor_position(current_position-1)
        elif current_position == -1 and text_length > 0:
            self.clutter_text.set_cursor_position(text_length-1)

    def move_word_backward(self):
        """
        Move cursor one word backward
        """
        current_position = self.get_cursor_position()
        text = self.clutter_text.get_text()
        if current_position == 0:
            pass
        else:
            if current_position == -1:
                current_position = len(text) - 1
            letter = text[current_position-1]
            while letter == ' ':
                current_position -= 1
                letter = text[current_position]
            while letter != ' ':
                current_position -= 1
                letter = text[current_position-1]
                if current_position == 0:
                    break
            self.clutter_text.set_cursor_position(current_position)

    def move_word_forward(self):
        """
        Move cursor one word forward
        """
        current_position = self.get_cursor_position()
        text = self.clutter_text.get_text()
        if current_position <= -1:
            pass
        else:
            try:
                letter = text[current_position]
                while letter == ' ':
                    current_position += 1
                    letter = text[current_position]
                while letter != ' ':
                    current_position += 1
                    letter = text[current_position-1]
            except IndexError:
                current_position = -1
        self.clutter_text.set_cursor_position(current_position)

    def move_line_up(self):
        """
        Move cursor one line up.
        """
        self._move_line(-1)

    def move_line_down(self):
        """
        Move cursor one line down.
        """
        self._move_line(+1)

    def _move_line(self, where):
        layout = self.clutter_text.get_layout()
        pos = self.clutter_text.get_cursor_position()
        if pos == -1:
            pos = self.get_text_length()
        line_idx, _line_x = layout.index_to_line_x(pos, 0)
        lines = layout.get_lines_readonly()
        line_count = len(lines)
        if where == +1 and line_idx == line_count - 1:
            new_pos = self.get_text_length()
        else:
            offset = 5  # safety measure for an extra distance between lines
            rect = self.clutter_text.get_cursor_rect()
            x, y = rect.origin.x, rect.origin.y
            height = rect.size.height
            new_y = y + where * (height + offset)
            new_pos = self.clutter_text.coords_to_position(x, new_y)
        self.clutter_text.set_cursor_position(new_pos)

    def move_to_new_line(self):
        """
        Move to new line
        """
        self.type_text("\n")

    @property
    def ratio_width(self):
        return self._ratio_width

    @ratio_width.setter
    def ratio_width(self, value):
        self._ratio_width = value
        self.set_width(unit.w(value))
        self.text.set_width(unit.w(value))

    @property
    def ratio_height(self):
        return self._ratio_height

    @ratio_height.setter
    def ratio_height(self, value):
        self._ratio_height = value
        self.set_height(unit.h(value))
        self.text.set_height(unit.h(value))


class Key(pisak.libs.widgets.Button, configurator.Configurable):
    """
    Widget representing speller specific single keyboard key.
    
    Properties:

    * :attr:`default_text`
    * :attr:`altgr_text`
    * :attr:`special_text`
    * :attr:`target`
    """
    __gtype_name__ = "PisakSpellerKey"
    __gproperties__ = {
        "default_text": (
            GObject.TYPE_STRING,
            "key default text",
            "string appended to a text",
            " ",
            GObject.PARAM_READWRITE),
        "altgr_text": (
            GObject.TYPE_STRING,
            "altgr text",
            "altgr string appended to a text",
            "?",
            GObject.PARAM_READWRITE),
        "special_text": (
            GObject.TYPE_STRING,
            "special text",
            "special string appended to a text",
            "?",
            GObject.PARAM_READWRITE),
        "target": (
            Text.__gtype__,
            "typing target",
            "id of text box to type text",
            GObject.PARAM_READWRITE)
    }

    def __init__(self):
        super().__init__()
        self.pre_special_text = None
        self.undo_chain = []
        self.allowed_undos = set()
        #self.set_size(dims.MENU_BUTTON_H_PX, dims.MENU_BUTTON_H_PX)
        self.connect("clicked", self.on_activate)
        self.connect("notify::default-text", self._set_initial_label)
        self.apply_props()

    def _set_initial_label(self, source, spec):
        self.set_default_label()
        self.disconnect_by_func(self._set_initial_label)

    def _cache_pre_special_text(self, text_to_cache):
        if not self.pre_special_text:
            self.pre_special_text = text_to_cache

    def undo_label(self):
        while self.undo_chain:
            operation = self.undo_chain.pop()
            if callable(operation) and operation in self.allowed_undos:
                operation(self)

    def set_pre_special_label(self):
        if self.pre_special_text:
            self.set_label(self.pre_special_text)
            self.pre_special_text = None

    def set_default_label(self):
        self.set_label(self.default_text)

    def set_special_label(self):
        self._cache_pre_special_text(self.get_label())
        self.set_label(self.special_text)

    def set_caps_label(self):
        label = self.get_label()
        if label.isalpha():
            self.set_label(label.upper())

    def set_lower_label(self):
        label = self.get_label()
        if label.isalpha():
            self.set_label(label.lower())

    def set_altgr_label(self):
        try:
            label = self.get_label()
            if label.isalpha():
                if label.islower():
                    self.set_label(self.altgr_text.lower())
                elif label.isupper():
                    self.set_label(self.altgr_text.upper())
        except AttributeError:
            return None

    def set_swap_altgr_label(self):
        try:
            label = self.get_label()
            if self.altgr_text.lower() == label.lower():
                if label.islower():
                    # from lowercase altgr to lowercase default
                    self.set_label(self.default_text.lower())
                else:
                    # from uppercase altgr to (uppercase) default
                    self.set_label(self.default_text.upper())
            else:
                if label.isalpha() and self.altgr_text:
                    if label.islower():
                        # from lowercase default to lowercase altgr
                        self.set_label(self.altgr_text.lower())
                    else:
                        # from (uppercase) default to uppercase altgr
                        self.set_label(self.altgr_text.upper())
        except AttributeError:
            return None

    def set_swap_caps_label(self):
        label = self.get_label()
        if label.isalpha():
            self.set_label(label.swapcase())

    def set_swap_special_label(self):
        try:
            if self.get_label() == self.special_text:
                self.set_pre_special_label()
            else:
                self.set_special_label()
        except AttributeError:
            return None

    def on_activate(self, source):
        if self.target:
            self.target.type_text(self.get_label())

    @property
    def default_text(self):
        return self._default_text

    @default_text.setter
    def default_text(self, value):
        self._default_text = str(value)

    @property
    def altgr_text(self):
        return self._altgr_text

    @altgr_text.setter
    def altgr_text(self, value):
        self._altgr_text = str(value)

    @property
    def special_text(self):
        return self._special_text

    @special_text.setter
    def special_text(self, value):
        self._special_text = str(value)

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value


class Dictionary(text_tools.Predictor):
    """
    Object that follows changes in the text field and updates its content
    in a reaction to these changes.
    """
    __gtype_name__ = "PisakSpellerDictionary"

    LAST_CONTEXT_SRC = """
       \s*  # greedy leading whitespace
       ([A-Zążźćśłóęń]*?\s?)  # group of symbols which restart context
       \s*  # greedy trailing whitespace
       $  # end of text
       """
    LAST_CONTEXT = re.compile(LAST_CONTEXT_SRC, re.VERBOSE|re.IGNORECASE)

    def __init__(self):
        super().__init__()
        self.basic_content = ['Chciałbym', 'Czy', 'Jak', 'Jestem',
                              'Nie', 'Niestety', 'Rzeczywiście',
                              'Super', 'Witam']  # this is subject to change, perhaps should be a class argument
        self.apply_props()

    def do_prediction(self, text, position):
        text_segment = text[0:position]
        context = self.get_prediction_context(text_segment)
        if len(text_segment) == 0 or not context:
            self.content = self.basic_content
        else:
            self.content = predictor.get_predictions(context)
        if len(self.content) == 1:
            self.content[0] = self.content[0] + ' '  # automatic space if only one suggestion
        self.notify_content_update()

    @staticmethod
    def get_prediction_context(text):
        """
        Extract prediction context from a text. Strips any leading or trailing
        whitespace. Takes only a fragment of a text after last
        context-clearing symbol.
        """
        context = Dictionary.LAST_CONTEXT.search(text)
        if context:
            return context.group(1)


class Prediction(pisak.libs.widgets.Button, configurator.Configurable):
    """
    Widget representing a button being a placeholder for predicting
    engine results.

    Properties:

    * :attr:`dictionary`
    * :attr:`order_num`
    * :attr:`target`
    * :attr:`idle_icon_name`
    """
    __gtype_name__ = "PisakSpellerPrediction"
    __gproperties__ = {
        "dictionary": (
            Dictionary.__gtype__,
            "prediction dictionary",
            "dictionary to get the suggested words from",
            GObject.PARAM_READWRITE),
        "order_num": (
            GObject.TYPE_INT,
            "order number",
            "position in a line for the new words",
            1,
            9,
            1,
            GObject.PARAM_READWRITE),
        "target": (
            Text.__gtype__,
            "typing target",
            "id of text box to type text",
            GObject.PARAM_READWRITE),
        "idle_icon_name": (
            GObject.TYPE_STRING,
            "idle icon name",
            "name of the icon on button while idle",
            " ",
            GObject.PARAM_READWRITE)
    }

    def __init__(self):
        super().__init__()
        #self.set_size(dims.MENU_BUTTON_W_PX, dims.MENU_BUTTON_H_PX)
        self.connect("clicked", self._on_activate)
        self.idle_icon_name = "hourglass"
        self.icon_name = None
        self.order_num = None
        self.icon_size = 50
        self.set_layout_manager(Clutter.BinLayout())
        self.layout = self.get_children()[0]
        self.clutter_text = [i for i in self.layout.get_children()
                            if type(i) == Clutter.Text][0]
        self.clutter_text.set_property("ellipsize", 0)
        self.clutter_text.connect("text-changed", self._resize_reflow)
        self.connect("notify::mapped", self._initial_label)
        self.apply_props()

    @property
    def idle_icon_name(self):
        return self._idle_icon_name

    @idle_icon_name.setter
    def idle_icon_name(self, value):
        self._idle_icon_name = value

    def _initial_label(self, *args):
        if self.get_property("mapped") and self.order_num is not None:
            self.set_label(self.dictionary.basic_content[self.order_num-1])

    def _on_activate(self, source):
        label = self.get_label()
        if label and self.target:
            self.target.replace_endmost_string(label)

    def _update_button(self, source):
        self.icon_name = ""
        new_label = self.dictionary.get_suggestion(self.order_num-1)
        if new_label:
            self.set_label(new_label)
        else:
            self.set_label("")
            self.set_disabled(True)
        self._group_schedule_update()

    def _group_schedule_update(self):
        """
        Finds group among ancestors and schedules its update to include
        disable/enable.
        """
        ancestor = self.get_parent()
        scheduled = False
        while ancestor is not None and not scheduled:
            if isinstance(ancestor, scanning.Group):
                ancestor.schedule_update()
                scheduled = True
            else:
                ancestor = ancestor.get_parent()

    def _resize_reflow(self, *args):
        button_width = self.get_width()
        button_height = self.get_height()
        self.clutter_text.set_pivot_point(0.5, 0.5)
        self.clutter_text.set_scale(1, 1)
        text_width = self.clutter_text.get_width()
        text_height = self.clutter_text.get_height()
        self.set_disabled(False)
        if text_width + 27 > button_width:
            self.set_offscreen_redirect(Clutter.OffscreenRedirect.ALWAYS)
            self.clutter_text.set_pivot_point(0, 0.5)
            self.clutter_text.set_scale(button_width/(text_width*1.3),
                                        button_width/(text_width*1.3))

    def _button_idle(self, source):
        self.set_label(" ")
        if self.idle_icon_name is not None:
            self.icon_name = self.idle_icon_name
        self.set_disabled(True)

    def _follow_dictionary(self):
        if self.dictionary is not None:
            self.dictionary.connect("content-update", self._update_button)
            self.dictionary.connect("processing-on", self._button_idle)

    def _stop_following_dictionary(self):
        try:
            if self.dictionary is not None:
                self.dictionary.disconnect_by_func("content-update", 
                                                   self._update_button)
                self.dictionary.disconnect_by_func("processing-on", 
                                                   self._button_idle)
        except AttributeError:
            return None

    @property
    def dictionary(self):
        return self._dictionary

    @dictionary.setter
    def dictionary(self, value):
        self._stop_following_dictionary()
        self._dictionary = value
        self._follow_dictionary()

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    @property
    def order_num(self):
        return self._order_num

    @order_num.setter
    def order_num(self, value):
        self._order_num = value


class PopUp(pisak.libs.widgets.DialogWindow):
    """
    Dialog window for purposes of saving and loading text documents.
    """
    __gtype_name__ = "PisakSpellerPopUp"
    
    def __init__(self):
        super().__init__()
        self.apply_props()

    def _generate_content(self, text_files=None):
        if text_files:
            for idx, file in enumerate(text_files):
                if idx % self.column_count == 0:
                    row = layout.Box()
                    row.spacing = self.spacing
                    self.space.add_child(row)
                button = pisak.libs.widgets.Button()
                button.set_style_class("PisakSpellerButton")
                button.set_label(file.name)
                button.ratio_width = self.tile_ratio_width
                button.ratio_height = self.tile_ratio_height
                button.connect("clicked", self._on_select, file.path)
                row.add_child(button)
        row = layout.Box()
        row.spacing = self.spacing
        self.space.add_child(row)
        button = pisak.widgets.Button()
        row.add_child(button)
        button.set_style_class("PisakSpellerButton")
        button.ratio_width = self.tile_ratio_width
        button.ratio_height = self.tile_ratio_height
        button.connect("clicked", self._close)
        if text_files:
            button.set_label(self.exit_button_label)
        else:
            button.set_label(self.continue_button_label)

    def _on_select(self, button, path):
        if self.mode == "save":
            new_text = self.target.get_text()
            with open(path, "w") as file:
                file.write(new_text)
        elif self.mode == "load":
            with open(path, "r") as file:
                text = file.read()
            self.target.clear_all()
            self.target.type_text(text)
        self._close()
