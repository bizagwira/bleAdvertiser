import sys, optparse, time, datetime, re


class IndentedHelpFormatterWithNL(optparse.IndentedHelpFormatter):
    def format_description(self, description):
        if not description: return ""

        desc_width = self.width - self.current_indent
        indent = " "*self.current_indent

        bits = description.split('\n')
        formatted_bits = [
          optparse.textwrap.fill(bit,
            desc_width,
            initial_indent=indent,
            subsequent_indent=indent)
          for bit in bits]
        result = "\n".join(formatted_bits) + "\n"
        return result

    def format_option(self, option):
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2

        if len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        else: # start help on same line as opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0

        result.append(opts)
        if option.help:
            help_text = self.expand_default(option)
            help_lines = []
            for para in help_text.split("\n"):
                help_lines.extend(optparse.textwrap.wrap(para, self.help_width))

            result.append("%*s%s\n" % (
            indent_first, "", help_lines[0]))
            result.extend(["%*s%s\n" % (self.help_position, "", line) for line in help_lines[1:]])

        elif opts[-1] != "\n":
            result.append("\n")

        return "".join(result)

class OptionFormatter(optparse.OptionParser):
    def format_epilog(self, formatter=None):
        return self.epilog

    def format_option_help(self, formatter=None):
        formatter = IndentedHelpFormatterWithNL()
        if formatter is None:
            formatter = self.formatter

        formatter.store_option_strings(self)
        result = []
        result.append(formatter.format_heading(optparse._("Options")))
        formatter.indent()

        if self.option_list:
            result.append(optparse.OptionContainer.format_option_help(self, formatter))
            result.append("\n")
        for group in self.option_groups:
            result.append(group.format_help(formatter))
            result.append("\n")

        formatter.dedent()

        # Drop the last "\n", or the header if no options or option groups:
        return "".join(result[:-1])
