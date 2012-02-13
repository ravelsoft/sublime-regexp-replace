import sublime, sublime_plugin
from itertools import izip
import re

class RegexpReplaceWindowCommand(sublime_plugin.WindowCommand):
    """ Offer to replace regexps dynamically.
    """

    key = "RegexpReplaceRegions"

    def run(self):
        self.regions = []
        input_panel = self.window.show_input_panel("Replace What", "", self.on_done, self.on_change, self.on_cancel)

        # Have the input be highlighted as a Regular Expression !
        input_panel.set_syntax_file("Packages/Regular Expressions/RegExp.tmLanguage")

    def on_change(self, s):
        view = self.window.active_view()
        current_selection = view.sel()

        # Compute the size of all the items in the selections
        selsize = 0
        for r in current_selection:
            selsize += r.end() - r.begin()

        try:
            if s:
                regions = view.find_all(s)

                # Filter the set of matched regions to only those that are inside the
                # current selection if its size is > 0.
                if selsize > 0: regions = [r for r in regions if current_selection.contains(r)]

                # We reverse the regions. If we didn't, when we modify their contents later on
                # we get in trouble since the beginning and end index of the subsquent
                # regions change with the edits we make.
                self.regions = list(reversed(regions))

                # Highlight the regions in the editor.
                view.add_regions(RegexpReplaceWindowCommand.key,
                    regions,
                    "keyword",
                    "bookmark",
                    sublime.DRAW_OUTLINED)
            else:
                self.window.active_view().erase_regions(RegexpReplaceWindowCommand.key)
        except Exception as e:
            # FIXME should maybe print an error ?
            pass

    def on_done(self, s):
        view = self.window.active_view()
        self.look = s
        self.pat = re.compile(s)

        if s and self.regions:
            self.original_regions = [view.substr(r) for r in self.regions]
            self.window.show_input_panel("Replace /{0}/ With...".format(s), "", self.on_done_repl, self.on_change_repl, self.on_cancel_repl)

    def on_cancel(self):
        self.window.active_view().erase_regions(RegexpReplaceWindowCommand.key)

    def replace_regions(self, changes):
        new_regions = []
        offsets = []

        view = self.window.active_view()
        edit = view.begin_edit()
        offset = 0

        for r, s in izip(self.regions, changes):
            offsets.append(len(s) - r.end() + r.begin())
            view.replace(edit, r, s)

        offset = 0
        for r, o, s in izip(reversed(self.regions), reversed(offsets), reversed(changes)):
            new_regions.append(sublime.Region(r.begin() + offset, r.begin() + offset + len(s)))
            offset += o
        new_regions.reverse()

        view.end_edit(edit)
        return new_regions

    def compute_changes(self, s):
        changes = []
        for o in self.original_regions:
            match = self.pat.match(o)
            changes.append(s.format(*match.groups()))
        return changes

    def on_done_repl(self, s):
        self.replace_regions(self.compute_changes(s))
        self.window.active_view().erase_regions(RegexpReplaceWindowCommand.key)

    def on_change_repl(self, s):
        new_regions = self.replace_regions(self.compute_changes(s))
        self.regions = new_regions
        self.window.active_view().add_regions(RegexpReplaceWindowCommand.key, new_regions, "type")

    def on_cancel_repl(self):
        self.replace_regions(self.original_regions)
        self.window.active_view().erase_regions(RegexpReplaceWindowCommand.key)
