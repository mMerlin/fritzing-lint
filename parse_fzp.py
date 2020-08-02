#!/usr/bin/env python
# coding=utf-8

'''
open Fritzing part definition file, and extract information from it

xml parsing
'''

# pipenv shell
# pipenv run pylint parse_fzp.py

# standard library imports
from typing import Dict
import subprocess
import re
import argparse
import defusedxml.ElementTree as ET

# local application/library specific imports
from myutilities import ReadableFile
from yield_parts import PartFinder

PARSE_FZP_VERSION = '0.0.1'

def is_trimmed_string(source: str) -> bool:
    '''check if string has any leading, trailing whitespace, or embedded newline'''
    # print('is_trimmed? "{0}"'.format(source),
    #       re.match(r'^\s', source) is None,
    #       re.match(r'.*\s$', source) is None,
    #       re.match(r'.*\n', source) is None,
    #       (re.match(r'^\s', source) is None and re.match(r'.*\s$', source) is None
    #        and re.match(r'.*\n', source) is None)
    #      ) # DEBUG
    return re.match(r'^\s', source) is None and re.match(r'.*\s$', source) is None \
        and re.match(r'.*\n', source) is None
# end def is_trimmed_string:


class ProcessParts:
    '''process a set/series of part definition files

    later, will include a core or user part library scan
    for now, just pass a single fzp file from cli arguments to
    the parsing code
    '''
    # pylint: disable=too-few-public-methods
    def __init__(self, cmd_args: argparse.Namespace):
        '''select part files and processing options from command line arguments'''
        self.command_arguments = cmd_args
        # first_file = cmd_args.definition_file
        # print('request part is {0}'.format(type(first_file))) # DEBUG
        # print('requested part file(s): {0}'.format(cmd_args.definition_file)) # DEBUG
        # print('cli args namespace: {0}'.format(cmd_args)) # DEBUG
        part_parse_options = {
            'exceptions': cmd_args.exceptions,
            'process_svg': cmd_args.svg,
            'verbose': cmd_args.verbose,
            'dtd': 'FritzingPart.dtd' # hard-coded for now
        }
        # _definition_instance = FritzingPartDefinition(first_file, part_parse_options)

        args = argparse.Namespace()
        args.folder = None
        args.svg = False
        args.part_library = None
        args.pattern = None

        # args.folder = './'
        # args.folder = '/home/phil/Documents/data_files/fritzing-parts/core/'

        args.part_library = '/home/phil/Documents/data_files/fritzing-parts/'

        for part_file in PartFinder(args).filtered_files():
            # print(part_file.name) # DEBUG
            # print(part_file.path) # DEBUG
            _definition_instance = FritzingPartDefinition(part_file, part_parse_options)
            # try:
            #     _definition_instance = FritzingPartDefinition(part_file, part_parse_options)
            # except NotImplemented as ni_exc:
            #     print(part_file.path, part_file.name)
            #     print(ni_exc)
            #     break

    # end def __init__:
# end class ProcessParts:


class FritzingPartDefinition:
    '''handle all references to the content of single Fritzing part definition file'''
            # print(self.data_set['file_path'].path) # DEBUG
    EXCEPTION_DATA = {
        'bad_layer4image': {
            'severity' : 'warning', 'msg': 'unexpected view layer id for image path'},
        'bad_icon_layer': {
            'severity' : 'warning', 'msg': 'unexpected icon layer for image path'},
        'bad_bb_layer': {
            'severity' : 'warning', 'msg': 'breadboardView not using breadboard layer'},
        'redundant_attribute': {
            'severity' : 'information', 'msg': 'redundant attribute for view'},
        'dup_support_ele': {
            'severity' : 'warning', 'msg': 'duplicate supporting element in module'},
        'dup_main_ele': {
            'severity' : 'error', 'msg': 'duplicate main element in module'},
        'not_child_element': {
            'severity' : 'error', 'msg': 'unrecognized xml element for context'},
        'bb_no_bb_path': {
            'severity' : 'error', 'msg': 'breadboardView not using breadboard folder'},
        'multiple_layer': {
            'severity' : 'error', 'msg': 'multiple layer elements for non-pcb view'},
        'null_family': {
            'severity' : 'error', 'msg': 'empty family property'},
        'duplicate_layer': {
            'severity' : 'error', 'msg': '2 layers in same view with the same id'},
        'no_bb_view': {
            'severity' : 'warning', 'msg': 'part does not have a breadboard view'},
        'untrimmed_text': {
            'severity' : 'error', 'msg': 'found unexpected surrounding whitespace for context'}
    }

    def __init__(self, part_file: str, options: dict):
        self.root = None
        self.data_set = {
            'have_part_definition': False,
            'data_error_detected': False,
            'part_views': {},
            'properties': {},
            'file_path': part_file
        }
        self.options = {
            'exceptions': options['exceptions'],
            'process_svg': options['process_svg'],
            'verbosity': options['verbose'],
            'dtd': options['dtd']
        }
        self.exceptions = {
            'information': [],
            'warning': [],
            'error': []
        }

        self.load_part_definition(part_file)
        if not self.data_set['have_part_definition']:
            print('part definition not loaded for "{0}"'.format(part_file))
            # raise ??
            return
        self.walk_fzp_xml_tree()
        if self.data_set['data_error_detected']:
            print(self.data_set['file_path'].path) # DEBUG
            print(self.exceptions) # DEBUG
            print()
    # def __init__:

    def record_exception(self, case: str, cause: str, context: list) -> None:
        '''save information about something strange detected in the part definition'''
        self.data_set['data_error_detected'] = True
        case_data = self.EXCEPTION_DATA[case]
        self.exceptions[case_data['severity']].append({
            'key': case,
            'msg': case_data['msg'],
            'value': cause,
            'context': list(context)
            })
    # end def record_exception:

    def load_part_definition(self, part_file_spec: str) -> None:
        '''load part definition information from file'''
        # dtd_info = self.validate_via_dtd(part_file_spec)
        # if dtd_info['state'] != 'valid':
        #     msg_fmt = 'Specified part definition file "{0}" failed the dtd check\n' \
        #         '  with state {state}\n  Parsing information: \n{fail}'
        #     print(msg_fmt.format(part_file_spec, **dtd_info))
        #     return
        tree = ET.parse(
            part_file_spec, forbid_dtd=True, forbid_entities=True, forbid_external=True)
        self.root = tree.getroot()
        self.data_set['have_part_definition'] = True
    # end def load_part_definition:

    def validate_via_dtd(self, xml_file_path: str) -> Dict[str, str]:
        '''check a single part definition xml file against the dtd

        This does NOT verify that the part data makes sense. Only that the xml structure
        matches the DTD specification. Which itself is incomplete and limited.

        This is also NOT safe to use as an initial validation check. xmllint is apparently
        susceptible to maliciously malformed xml documents'''
        # https://docs.python.org/3/library/subprocess.html#subprocess.run
        lint_result = subprocess.run(
            ['xmllint', '--nocatalogs', '--dtdvalid', self.options['dtd'], xml_file_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False)
        if lint_result.returncode == 0:
            return {'state': 'valid'}
        if lint_result.returncode != 3:
            return {
                'state': 'checkfail', 'status': lint_result.returncode, 'fail': lint_result.stderr
            }
        return {'state': 'invalid', 'fail': lint_result.stderr}
    # end def validate_via_dtd(…)

    def walk_fzp_xml_tree(self) -> None:
        '''explore the fzp content'''
        self.sanity_check_module_elements()
        self.process_part_properties()
        # print(self.data_set['properties']) # DEBUG collected property details
        self.process_part_views()
        # print(self.data_set['part_views']) # DEBUG collected part view and layer details
        # hpd
    # end def walk_fzp_xml_tree:

    @staticmethod
    def _report_str_or_other_variable(source: str, label: str) -> None: # DEBUG
        '''show content of variable that is expected to be a str or None, but others work too'''
        if isinstance(source, str):
            print('{0} str len = {1}, and value is "{2}"'.format(
                label, len(source), source))
        else:
            print('{0} type is {1}, and value is "{2}"'.format(
                label, type(source), source))
    # end def _report_str_or_other_variable: # DEBUG

    def expecting_none_or_whitespace(self, source: str, context: dict) -> None:
        '''default handling trap when expecting either None or str with only whitespace'''
        if source is not None:
            # all_whitespace_match = re.match(r'\A\s*\Z', source)
            all_whitespace_match = re.fullmatch(r'\s+', source)
            if all_whitespace_match is None:
                print('module{parent}{tag} {ref} content is "{0}"'.format(
                    source, **context)) # DEBUG
                self.data_set['data_error_detected'] = True
                raise NotImplementedError(
                    'handling not written yet for non-whitespace {ref}'
                    ' in module{parent}{tag} element'.format(**context))
    # end def expecting_none_or_whitespace:

    def check_required_and_no_duplicates(
            self, existing: list, required: list, context: dict) -> None:
        '''assert that all required (attribute) values exist, and no duplicates'''
        for key in required:
            if not key in existing:
                print(self.data_set['file_path'].path) # DEBUG
                self.data_set['data_error_detected'] = True
                print(existing, required)
                raise NotImplementedError(
                    'handling not written yet for missing "{0}" required attribute on'
                    ' module{parent}{tag} element'.format(key, **context))
        key_collection = []
        for key in existing:
            if key in key_collection:
                raise NotImplementedError(
                    'handling not written yet for duplicate "{0}" attribute on module{parent}{tag}'
                    ' element'.format(key, **context))
            key_collection.append(key)
    # end def check_required_and_no_duplicates:

    def expecting_wrapper_only_element(self, element, context: dict) -> None:
        '''default handling trap when expecting an element that should only be a container

        no text
        no attrib
        '''
        self.expecting_required_wrapper_element(element, context)
        # if element is None:
        #     self.data_set['data_error_detected'] = True
        #     raise NotImplementedError(
        #         'handling not written yet for missing {tag} child element in'
        #         ' module{parent}'.format(**context))
        # text_context = dict(context)
        # text_context['ref'] = 'text'
        # self.expecting_none_or_whitespace(element.text, text_context)
        # text_context['ref'] = 'tail'
        # self.expecting_none_or_whitespace(element.tail, text_context)
        if element.attrib:
            print(element.attrib)
            raise NotImplementedError(
                'handling not written yet for attributes on module{parent}{tag}'
                ' element'.format(**context))
    # end def expecting_wrapper_only_element:

    def expecting_required_wrapper_element(self, element, context: dict) -> None:
        '''default handling trap when expecting a container element

        must exist
        no text
        '''
        if element is None:
            self.data_set['data_error_detected'] = True
            raise NotImplementedError(
                'handling not written yet for missing {tag} child element in'
                ' module{parent}'.format(**context))
        text_context = dict(context)
        text_context['ref'] = 'text'
        self.expecting_none_or_whitespace(element.text, text_context)
        text_context['ref'] = 'tail'
        self.expecting_none_or_whitespace(element.tail, text_context)
    # end def expecting_required_wrapper_element:

    def expecting_wrapper_with_optional_attributes(
            self, element, optional: list, context: dict) -> None:
        '''default handling trap when expecting an element that should be a container\
        with optional attributes

        must exist
        no text
        may have attributes
        '''
        self.expecting_required_wrapper_element(element, context)
        self.expecting_attribute_set(element, [], optional, context)
    # end def expecting_wrapper_with_optional_attributes:

    def expecting_exact_attribute_set(
            self, element, attributes: list, context: dict) -> None:
        '''default handling trap when expecting exact list of attributes on an element'''
        ele_attrib_keys = list(element.attrib)
        self.check_required_and_no_duplicates(ele_attrib_keys, attributes, context)
        for key in ele_attrib_keys:
            if key not in attributes:
                print(self.data_set['file_path'].path) # DEBUG
                raise NotImplementedError(
                    'handling not written yet for unexpected "{0}" attribute on module{parent}{tag}'
                    ' element'.format(key, **context))
        if len(ele_attrib_keys) != len(attributes):
            print(element.attrib)
            raise NotImplementedError(
                'handling not written yet for missmatched attribute counts on module{parent}{tag}'
                ' element'.format(**context))
    # end def expecting_exact_attribute_set:

    def expecting_attribute_set(
            self, element, required: list, optional: list, context: dict) -> None:
        '''default handling trap when required and optional attributes could be on an element'''
        ele_attrib_keys = list(element.attrib)
        self.check_required_and_no_duplicates(ele_attrib_keys, required, context)
        for key in ele_attrib_keys:
            if key not in required and key not in optional:
                print(self.data_set['file_path'].path) # DEBUG
                raise NotImplementedError(
                    'handling not written yet for unexpected (optional) "{0}" attribute on'
                    ' module{parent}{tag} element'.format(key, **context))
    # end def expecting_attribute_set:

    def expecting_trimmed_text_string(self, source: str, context: dict) -> None:
        '''default handling trap when expecting trimmed, not empty single line string

        not empty
        no newline
        no leading whitespace
        no trailing whitespace'''
        # print('trimmed? "{0}"'.format(source)) # DEBUG
        # print(bool(source), is_trimmed_string(source)) # DEBUG
        if not(source and is_trimmed_string(source)):
            self.data_set['data_error_detected'] = True
            print('"{0}"'.format(source))
            raise NotImplementedError(
                'handling not written yet for empty, untrimmed or multiline text'
                ' string {context}'.format(**context))
    # def expecting_trimmed_text_string:

    def expecting_none_empty_or_trimmed_text_string(self, source: str, context: dict) -> None:
        '''default handling trap when expecting None, only whitespace, or trimmed text string

        None
        only whitespace
        trimmed single string
          no newline
          no leading whitespace
          no trailing whitespace
        '''
        # print('None or trimmed? "{0}"'.format(source),
        #       bool(source),
        #       re.match(r'\A\s*\Z', source),
        #       is_trimmed_string(source)) # DEBUG
        if source is not None:
            if re.match(r'\A\s*\Z', source) is None and not is_trimmed_string(source):
                self.record_exception('untrimmed_text', source, [context])
    # end def expecting_none_empty_or_trimmed_text_string:

    def sanity_check_module_elements(self) -> None:
        '''global checks of the elements in the root module'''
        all_child_elements = (
            'author', 'buses', 'connectors', 'date', 'description', 'label', 'properties',
            'schematic-subparts', 'spice', 'tags', 'taxonomy', 'title', 'url', 'version', 'views')
        main_child_elements = ('buses', 'connectors', 'properties', 'views')
        self.expecting_none_or_whitespace(
            self.root.text, {'parent': '', 'tag': '', 'ref': 'text'})
        if self.root.tail is not None: # even blank string not expected here
            print('root node tail content is "{0}"'.format(self.root.tail)) # DEBUG
            raise NotImplementedError(
                'handling not written yet for non-null tail in module')

        child_elements = {}
        for ele in self.root:
            if not ele.tag in all_child_elements:
                self.record_exception('not_child_element', ele.tag, ['module'])
                continue
            if ele.tag in child_elements:
                if ele.tag in main_child_elements:
                    self.record_exception('dup_main_ele', ele.tag, ['root'])
                else:
                    self.record_exception('dup_support_ele', ele.tag, ['root'])
            child_elements[ele.tag] = 0
            self.expecting_none_or_whitespace(
                ele.tail, {'parent': '', 'tag': '.' + ele.tag, 'ref': 'tail'})
    # def sanity_check_module_elements(self) -> None:

    def process_part_properties(self) -> None:
        '''validate and collect information about the part properties'''
        # only need to get a single element: module element validation checks that it does
        # not contain any repeated child elements
        property_required_attributes = ['name']
        property_optional_attributes = ['showInLabel']
        properties = self.root.find('properties')
        # print('process part properties: {0}'.format(type(properties))) # DEBUG
        self.expecting_wrapper_only_element(
            properties, {'tag': '.properties', 'parent': ''})
        property_names = {}
        for prop in properties:
            if prop.tag != 'property':
                self.record_exception('not_child_element', prop.tag, ['module.properties'])
                continue
            self.expecting_attribute_set(
                prop, property_required_attributes, property_optional_attributes,
                {'parent': '.properties', 'tag': '.property'})
            prop_name = prop.get('name')
            if prop_name in property_names:
                raise NotImplementedError(
                    'handling not written yet for duplicate property name ("{0}")'
                    ' in module.properties.property'.format(prop_name))
            # self._report_str_or_other_variable(prop.text, 'property text') # DEBUG
            self.expecting_none_empty_or_trimmed_text_string(
                prop.text, {'context': 'property name text value'})
            # if not prop.text is None:
            #     self.expecting_trimmed_text_string(
            #         prop.text, {'context': 'property name text value'})
            property_names[prop_name] = prop.text
            self.expecting_none_or_whitespace(
                prop.tail, {'parent': '.properties', 'tag': '.property', 'ref': 'tail'})
        if 'family' not in property_names:
            print(property_names)
            raise NotImplementedError(
                'handling not written yet for missing family property name'
                ' in module.properties.property')
        if property_names['family'] is None:
            self.record_exception('null_family', property_names['family'], [])
        self.data_set['properties'] = property_names # save for later use
    # end def process_part_properties:

    def process_part_views(self) -> None:
        '''validate and collect information about the view specific graphics for the part

        This does not look at the view information for connectors'''
        # only need to get a single element: module element validation checks that it does
        # not contain any repeated child elements
        views = self.root.find('views')
        self.expecting_wrapper_only_element(views, {'parent': '', 'tag': '.views'})
        part_views = {}
        for view in views:
            # print(view.tag, view.attrib) # DEBUG
            self.detail_module_views_child_checks(view, part_views)
            part_views[view.tag] = {}
            views_children = {}
            for layers in view:
                self.detail_module_views_layers_checks(layers, views_children)
                part_views[view.tag]['image'] = layers.get('image')
                part_views[view.tag]['layers'] = []
                # print('  {0} {1}'.format(layers.tag, layers.attrib)) # DEBUG
                layers_children = {}
                for layer in layers:
                    self.detail_layer_check(
                        layer, layers_children, view.tag, part_views[view.tag]['image'])
                    # print('    {0} {1}'.format(layer.tag, layer.attrib)) # DEBUG
                    part_views[view.tag]['layers'].append(layer.get('layerId'))
                # print(layers_children) # DEBUG
                # self.detail_layer_accumulated_check(layers_children, view.tag)
                # hpd
        # Until shown otherwise, assume that all parts must have a breadboardView,
        # using a file in the breadboard folder, with a layer of "breadboard"
        # ("breadboardbreadboard" ONLY when part family is "breadboard")
        part_family = self.data_set['properties']['family']
        if 'breadboardView' not in part_views:
            self.record_exception('no_bb_view', None, ['family', part_family])
            return
        image_details = self.parse_svg_view_image_path(part_views['breadboardView']['image'])
        if image_details['folder'] != 'breadboard':
            self.record_exception(
                'bb_no_bb_path', image_details['folder'],
                ['family', part_family, image_details['name']])
        if part_family == "Breadboard":
            if part_views['breadboardView']['layers'][0] != 'breadboardbreadboard':
                print(self.data_set['file_path'].path) # DEBUG
                print(part_family, image_details)
                raise NotImplementedError(
                    'handling not written yet for breadboard family not using'
                    ' breadboardbreadboard layer')
        else:
            if part_views['breadboardView']['layers'][0] != 'breadboard':
                self.record_exception(
                    'bad_bb_layer', part_views['breadboardView']['layers'][0],
                    ['family', part_family, image_details['name']])
        self.data_set['part_views'] = part_views
    # end def process_part_views:

    def detail_layer_check(
            self, child_ele, processed_children: dict, parent_view: str, image_path: str) -> None:
        '''validation checks for a child element of module.views.*.layers'''
        view_layers = {
            'breadboard': ('breadboard', 'breadboardbreadboard'),
            'icon': ('icon'),
            'pcb': ('copper0', 'copper1', 'keepout', 'outline', 'silkscreen', 'silkscreen0',
                    'soldermask'),
            'schematic': ('schematic'),
        }
        layer_required_attributes = ['layerId']
        layer_optional_attributes = ['sticky'] # is this really used?
        if child_ele.tag != 'layer':
            print(child_ele.tag)
            self.data_set['data_error_detected'] = True
            raise NotImplementedError(
                'handling not written yet for bad child element in module.views.*.layers')
        if not child_ele.text is None:
            print('"{0}"'.format(child_ele.text))
            raise NotImplementedError(
                'handling not written yet for text in module.views.*.layers.layer element')
        self.expecting_none_or_whitespace(
            child_ele.tail, {'parent': '.views.*View.layers', 'tag': '.layer', 'ref': 'tail'})
        # self._report_str_or_other_variable(child_ele.tail, 'layers tail')
        if parent_view != 'pcbView':
            if child_ele.tag in processed_children:
                self.record_exception('multiple_layer', parent_view, [image_path])
        if child_ele.tag not in processed_children:
            processed_children[child_ele.tag] = []
        self.expecting_attribute_set(
            child_ele, layer_required_attributes, layer_optional_attributes,
            {'parent': '.views.*View.layers', 'tag': '.layer'})
        # self.expecting_exact_attribute_set(
        #     child_ele, ['layerId'], {'parent': '.views.*View.layers', 'tag': '.layer'})
        layer = child_ele.get('layerId')
        # valid (at least expected) layer ids are based on the target image path,
        # NOT the parent_view
        image_details = self.parse_svg_view_image_path(image_path)
        if layer not in view_layers[image_details['folder']]:
            if parent_view == 'iconView':
                if layer != 'icon':
                    self.record_exception('bad_icon_layer', layer, [parent_view, image_path])
            else:
                self.record_exception('bad_layer4image', layer, [parent_view, image_path])
        if layer in processed_children[child_ele.tag]:
            self.record_exception(
                'duplicate_layer', layer, ['module.views.*View.layers.layer', parent_view,
                                           image_details])
        processed_children[child_ele.tag].append(layer)
    # end def detail_layer_check:

    def detail_module_views_layers_checks(self, child_ele, processed_children: dict) -> None:
        '''validation checks for a child element of module.views.*'''
        if child_ele.tag != 'layers':
            self.record_exception('not_child_element', child_ele.tag, ['module.views'])
            return
        if child_ele.tag in processed_children:
            print(child_ele.tag)
            raise NotImplementedError(
                'handling not written yet for duplicate layers element in module.views')
        self.expecting_none_or_whitespace(
            child_ele.text, {'parent': '.views.*View', 'tag': '.layers', 'ref': 'text'})
        self.expecting_none_or_whitespace(
            child_ele.tail, {'parent': '.views.*View', 'tag': '.layers', 'ref': 'tail'})
        processed_children[child_ele.tag] = 1
        self.expecting_exact_attribute_set(
            child_ele, ['image'], {'parent': '.views.*View', 'tag': '.layers'})
        view_image = child_ele.get('image')
        self.parse_svg_view_image_path(view_image)
    # end def detail_module_views_layers_checks:

    def parse_svg_view_image_path(self, image_path: str) -> dict:
        '''separate meaningful details embedded in a part view svg file path'''
        view_folders = ('breadboard', 'icon', 'pcb', 'schematic')
        image_split = image_path.split('/')
        if len(image_split) != 2:
            self.data_set['data_error_detected'] = True
            print(image_path, image_split)
            raise NotImplementedError(
                'handling not written yet for bad image path splitting')
        image_folder = image_split[0]
        if image_folder not in view_folders:
            print(image_folder, image_path)
            raise NotImplementedError(
                'handling not written yet for bad image view folder')
        # (at least) breadboard parts use different pattern for (at least) breadboard svg images
        # image_suffix = '_' + image_folder + '.svg'
        # if not image_path.endswith(image_suffix):
        #     print(image_path)
        #     raise NotImplementedError(
        #         'handling not written yet for bad image name suffix')
        return {'folder': image_folder, 'name': image_split[1]}
    # end def parse_svg_view_image_path:

    def detail_module_views_child_checks(self, view_ele, processed_views: dict) -> None:
        '''validation checks for the child elements of module.views'''
        # property_required_attributes = []
        view_optional_attributes = ['flipvertical', 'fliphorizontal']
        redundant_attribute_views = ['iconView', 'schematicView']

        # print(type(view_ele)) # DEBUG <class 'xml.etree.ElementTree.Element'>
        if view_ele.tag not in ('breadboardView', 'iconView', 'pcbView', 'schematicView'):
            self.record_exception('not_child_element', view_ele.tag, ['module.views'])
            return
        self.expecting_wrapper_with_optional_attributes(
            view_ele, view_optional_attributes,
            {'parent': '.views', 'tag': '.' + view_ele.tag})
        if view_ele.attrib and view_ele.tag in redundant_attribute_views:
            for attribute in view_ele.attrib:
                self.record_exception('redundant_attribute', attribute, [view_ele.tag])
        if view_ele.tag in processed_views:
            raise NotImplementedError(
                'handling not written yet for duplicate "{}" element'
                ' in module.views'.format(view_ele.tag))
    # end def detail_module_views_child_checks:

    # for child in root: # DEBUG
    #     print(child.tag, child.attrib) # DEBUG
    # print([elem.tag for elem in root.iter()]) # DEBUG
    # print(ET.tostring(root, encoding='utf8').decode('utf8')) # DEBUG
    # for layer in root.iter('layers'): # DEBUG
    #     print(layer.attrib) # DEBUG
    #     print(ET.tostring(layer, encoding='utf8').decode('utf8')) # DEBUG
    # for prop in root.iter('property'):
    #     print(prop.text)
    # for view in root.findall('./views/'):
    #     print(view.tag, view.attrib)
    #     print(view.tag) # DEBUG
    #     print(ET.tostring(view, encoding='utf8').decode('utf8')) # DEBUG
    #     for child in view:
    #         print('child {0}'.format(child.tag))
    #     print(list(view))
    #     print(view.items)
    #     for layer in view.findall('./layers/'):
    #         print(layer.tag) # DEBUG
    # for layer in root.findall('./views/*/layers/'):
    #     print(layer.tag, layer.attrib)
    #     print(ET.tostring(layer, encoding='utf8').decode('utf8')) # DEBUG
    # for layers in root.findall('./views/*/'):
    #     print(layers.tag, layers.attrib)
    #     # print(ET.tostring(layer, encoding='utf8').decode('utf8')) # DEBUG
# end class FritzingPartDefinition:


class CommandLineParser:
    '''handle command line argument parsing'''
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.parser = CommandLineParser.build_parser()
        self.command_arguments = self.parser.parse_args()

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        '''create command line argument parser'''
        parser = argparse.ArgumentParser(description='Fritzing part definition parser')
        parser.add_argument('--version', action='version',
                            version='%(prog)s ' + PARSE_FZP_VERSION)
        # hpd later may want to support wild card patterns, without having the
        # os expand the command line arguments
        # --folder --pattern --family --property --tag
        # raw folder (of .fzp)
        # parts library (core, contrib, obsolete, user)
        # user parts (contrib, user)
        # specified file(s)
        parser.add_argument('definition_file', metavar='Part Definition',
                            action=ReadableFile,
                            help='Fritzing part definition file')
        parser.add_argument('-v', '--verbose', action='count', default=0,
                            help='increase verbosity')
        parser.add_argument('-e', '--exceptions', action='store_true',
                            help='report «non-fatal» exceptions while processing')
        parser.add_argument('-s', '--svg', action='store_true',
                            help='verify existence of matching svg view files')
        return parser
    # end def build_parser:
# end class CommandLineParser:


def my_main() -> None:
    '''wrapper for test/start code so that variables do not look like constants'''
    print('\n\n\n') #DEBUG
    cli_parser = CommandLineParser()
    ProcessParts(cli_parser.command_arguments)
# end def my_main:

# Standalone module execution
if __name__ == "__main__":
    my_main()

# variables, options, flags
#   cSpell:words nocatalogs dtdvalid iterfind
