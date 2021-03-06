from collections import defaultdict
from enum import Enum

from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives import unchanged, unchanged_required
from rv.api import m


def project_modules_map():
    return defaultdict(dict)


class ModuleDirective(Directive):

    has_content = True
    option_spec = dict(
        type=unchanged,
        name=unchanged,
    )
    required_arguments = 1

    def run(self):
        env = self.state.document.settings.env
        if not hasattr(env, 'file_projects_modules'):
            env.file_projects_modules = defaultdict(project_modules_map)
        src_path = self.state.document['source']
        varname, = self.arguments
        projname, modname = varname.split('.')
        p = env.file_projects[src_path]
        project = p[projname]
        pm = env.file_projects_modules[src_path]
        mods = pm[projname]
        if modname == '*':
            # Register all project's modules.
            for mod in project.modules:
                if mod is not None:
                    modname = (mod.name or mod.mtype).replace(' ', '_').lower()
                    mods[modname] = mod
        else:
            # Create and register a module specified in the doc.
            module_cls = getattr(m, self.options['type'])
            mod = project.new_module(module_cls)
            if 'name' in self.options:
                mod.name = self.options['name']
            for line in self.content:
                line = line.replace(' ', '')
                parts = line.split('=')
                if len(parts) == 2:
                    ctlname, value = parts
                    t = mod.controllers[ctlname].value_type
                    if not isinstance(t, type) or not issubclass(t, Enum):
                        value = int(value)
                    setattr(mod, ctlname, value)
            mods[modname] = mod
        return []
