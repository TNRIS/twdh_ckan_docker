from operator import truediv
import ckan.lib.helpers as h
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

from ckan.lib.plugins import DefaultTranslation

from datetime import datetime, timedelta
    
from PIL import Image
from os.path import exists
import logging

from ckanext.pages.interfaces import IPagesSchema

from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit
from ckanext.twdh_theme.auth import zip_resource
from ckanext.twdh_theme import routes
from ckanext.twdh_theme.logic import action

from ckanext import scheming

import ckan.model as model
from ckan.common import g, config, request, _


import re
import csv
import io
import json

log = logging.getLogger(__name__)

def dictated_sort(List, Key, list_order):
    """Returns dataset schema in display group order"""
    List.sort(key=lambda k:list_order.index(k[Key]))
    return

def order_by_display_group(schema):
    dictated_sort(schema['dataset_fields'], 'display_group', schema['display_group_order'])
    return

def recent_datasets(num=4, new_timedelta=31):
    """
    Return a list of recent datasets. 

    Args:
        num: integer number of results to return
        new_timedelta: integer number of days to consider a dataset 'new'

    Returns:
        list of dataset dicts

    """

    recent_datasets = []
    modified_datasets = []

    """ # calculate the date from which to compare if a dataset is 'new'
    new_since_date = datetime.today() - timedelta(days=new_timedelta)

    # query for datasets that are new from the past 31 days
    search_result_new = toolkit.get_action('package_search')({},{'rows': num, 'sort': 'metadata_created desc', 'q': 'metadata_created:[{}Z TO NOW]'.format( new_since_date.isoformat() ) })
    if search_result_new['count'] > 0:
        recent_datasets = add_tracking_to_datasets( search_result_new['results'] )

    # if less then 4 new datasets found from last 31 days, then query for recently modified datasets to fill out the set of 4
    if len( recent_datasets ) < num:
        search_result_modified = toolkit.get_action('package_search')({},{'rows': num, 'sort': 'metadata_modified desc'})
        if search_result_modified['count'] > 0:
            modified_datasets = add_tracking_to_datasets( search_result_modified['results'] )

        
        for modified_dataset in modified_datasets:
            found = False
            for new_dataset in recent_datasets:
                if modified_dataset['name'] == new_dataset['name']:
                    found = True
                    break
            if not found:
                recent_datasets.append( modified_dataset )
    """
    return recent_datasets

def add_tracking_to_datasets( datasets ):
    tracking_datasets = []
    
    # There has to be a better way to do this, but current_package_list_with_resources doesn't return tracking_summary, so this fixes that ...
    #tracking_datasets = []
    try:
        for pkg_dict in datasets:
            tracking_datasets.append( toolkit.get_action("package_show")({}, {'include_tracking': True,'id': pkg_dict['id']}) )
        return tracking_datasets
    except:
        print("PLEASE WORK :(")
        return tracking_datasets
    # Seems like the above should be doable with a lambda function but I can't get it working right now
    # datasets = map(lambda key: toolkit.get_action("package_show")({}, {'include_tracking': True,'id': datasets[key]['id']}), datasets )

def popular_datasets(num=5):
    """Return a list of popular datasets."""
    datasets = []
    search = toolkit.get_action('package_search')({},{'rows': num, 'sort': 'views_recent desc'})
    if search.get('results'):
        datasets = search.get('results')
    return datasets[:num]

def statewide_datasets(num=5):
    """Return a list of datasets datasets tagged statewide."""
    datasets = []
    sorted_datasets = []
    search = toolkit.get_action('package_search')({},{'fq': 'tags:statewide','facet.limit': num})
    if search.get('results'):
        datasets = add_tracking_to_datasets( search.get('results') )

    if datasets:
        sorted_datasets = sorted(datasets, key=lambda k: k['metadata_modified'], reverse=True)
    return sorted_datasets[:num]

def statewide_dataset_count():
    """Return a count of all datasets tagged with Statewide"""
    count = 0
    result = toolkit.get_action('package_search')({}, {'fq': 'tags:statewide','rows': 1})
    if result.get('count'):
        count = result.get('count')
    return count

def dataset_count():
    """Return a count of all datasets"""
    count = 0
    result = toolkit.get_action('package_search')({}, {'rows': 1})
    if result.get('count'):
        count = result.get('count')
    return count

def showcase_count():
    """Return a count of all showcases"""
    count = 0
    result = toolkit.get_action('package_search')({}, {'rows': 1, 'fq': '+dataset_type:showcase'})
    if result.get('count'):
        count = result.get('count')
    return count


def groups(num=100):
    """Return a list of groups"""
    groups = toolkit.get_action('group_list')({}, {'all_fields': True, 'sort': 'title asc', 'include_dataset_count': True, 'include_extras': True })
    return groups[:num]

def get_group_by_name(name):
    """Return a group"""

    groups = toolkit.get_action('group_list')({}, {'all_fields': True, 'sort': 'title asc', 'include_dataset_count': True, 'include_extras': True })
    for group in groups:
        if group.get('name') == name:
            return group
    return None

def get_group_by_id(id):
    """Return a group"""

    groups = toolkit.get_action('group_list')({}, {'all_fields': True, 'sort': 'title asc', 'include_dataset_count': True, 'include_extras': True })
    for group in groups:
        if group.get('id') == id:
            return group
    return None

def get_organization_groups( org_dict, num=3 ):
    """Return a list of of the top 'num' groups that the organization's datasets are members of """

    import operator

    cats = {}

    # retrieve all of the orgs' datasets
    fq =  'organization:' + org_dict['name']
    datasets = toolkit.get_action('package_search')({}, {'fq': fq,'rows': 1000})

    # loop through the datasets and count the catgories
    for dataset in datasets['results']:
        for category in dataset['groups']:
            if category['name'] in cats:
                cats[category['name']] = cats[category['name']] + 1
            else:
                cats[category['name']] = 1

    # reverse sort the cats and return the top num results
    return sorted(cats.items(), key=operator.itemgetter(1), reverse=True)[0:num]

def get_organization_admins( id ):
    """Return a list of all admins for an organization"""

    # 'member_tuples' is a list of (user_id, object_type, capacity) tuples
    member_tuples = toolkit.get_action('member_list')( data_dict={
        'id': id,
        'object_type': 'user',
        'capacity': 'admin'
    })

    members = []

    for member_tuple in member_tuples:
        members.append( toolkit.get_action('user_show')( data_dict={ 'id': member_tuple[0] } ) )

    return members

def scheming_groups_choices(dummy_var='none'):
    """Return a list of groups for scheming choices helper"""
    groups = toolkit.get_action('group_list')({}, {'all_fields': True})

    group_choices = [{
        'value': g['name'],
        'label': g['display_name']
    } for g in groups]
    return group_choices


def showcases(num=6):
    """Return a list of showcases"""
    sorted_showcases = []
    try:
        showcases = toolkit.get_action('ckanext_showcase_list')()
        # sorted_showcases = sorted(showcases, key=lambda k: k.get('metadata_modified'), reverse=True)
    except:
        print("[twdh_theme] Error in retrieving list of showcases")
    return showcases[:num]


def get_package_metadata(package):
    """Return the metadata of a dataset"""
    try:
        result = toolkit.get_action('package_show')(None, {'id': package.get('name'), 'include_tracking': True})
    except:
        print("Error in retrieving dataset metadata: {}".format(package.get('id', '')))
        package_metadata = package
        package_metadata['tracking_summary'] = {}
        package_metadata['tracking_summary']['total'] = 0
        package_metadata['tracking_summary']['recent'] = 0
        return package_metadata
    return result

def is_new(created_date, limit=31, title=None):
    """ display a 'new' icon. """
    """ created_date: the date the package was created """
    """ limit: a package must be less than or equal limit days old for the new icon to show """
    """ title: tooltip text for new icon """

    date2 = datetime.now()
    date1 = datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%S.%f')
    timedelta = date2 - date1

    if not title:
        raise Exception('is_new() did not recieve a valid type_ or title')
    return h.snippet('snippets/is_new.html',
                   title=title, age=timedelta.days, limit=limit)

def linked_resource_count(pkg_list):
    """ display the resource count of a package list """
    """ pkg_list: the list of packages """

    return len( pkg_list )

def strip_url( url ):
    """ Remove protocol prefix and trailing clash from a URL

    Args:
        url (_type_): URL

    Returns:
        str: Display-ready URL
    """

    # {{ h.url_for( 'home', _external = True ) | replace( "https", "" ) | replace( "http", "" ) | replace( "://", "" ) | replace( "/", "" ) }}
    # FIXME: Change to use regex
    return url.replace( 'https', '').replace( 'http', '' ).replace( '://', '').replace( '/', '')

def create_thumbnail( image_path ):
    """
    Create a thumbnail image in the samee directory the original image exists in
    thumbnail for image.png will be called image-thumbnail.png
    """

    log.info( 'create_thumbnail with ' + image_path )

    thumb_path =  "{0}-{2}.{1}".format(*image_path.rsplit('.', 1) + ['thumbnail'])

    log.info( 'thumb_path = ' + thumb_path )

    try:
        image = Image.open(image_path)
        log.info( 'success!' )
    except IOError:
        #if an image can't be parsed from the response...
        log.info( IOError )
        return None

    width = int( toolkit.config.get('ckan.thumbnail_width', 200) )
    height = int( toolkit.config.get('ckan.thumbnail_height', 200) )

    image.thumbnail( ( width, height ) )
    image.save( thumb_path )

    return True

def get_thumbnail( image_url ):
    """
    Given a URL of an existing image, return the thumbnail
    If a thumbnail doesn't exist, create one on the fly
    """

    return image_url
    
    log.info( '-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=')
    log.info( 'get_thumbnail with ' + image_url )

    # check to see if image is remote, if so just return image since we can't make a thumbnail of a remote image
    site_url = toolkit.config.get("ckan.site_url") 
    if image_url.startswith( 'http' ) and not image_url.startswith( site_url ): 
        return image_url

    thumb_url = ""
    image_path = ""
    storage_path = toolkit.config.get("ckan.storage_path") + '/storage'
    log.info( 'storage_path = ' + storage_path )

    if image_url != None and "." in image_url:

        # handle fully qualified URL
        if image_url.startswith( 'http' ):
            image_path =  "/{3}".format( *image_url.split('/', 3) )

        # image is relative path
        else:
            image_path = image_url

        # convert image_fp to thumb_fp by adding -thumbnail before the file extension
        thumb_url =  "{0}-{2}.{1}".format(*image_path.rsplit('.', 1) + ['thumbnail'])


    thumb_path = storage_path + thumb_url
    log.info( 'thumb_path =  ' + thumb_path )

    if not exists( thumb_path ):
        #log.info( 'thumbnail does not exist, trying to create one for ' + storage_path + image_path)
        create_thumbnail( storage_path + image_path )

    if exists( thumb_path ):
        log.info(  'returning thumb image ' + thumb_url );
        return thumb_url
    else:
        log.info(  'returning non-thumb image ' + image_url );
        return image_url



def twdh_user_image(user_id, size=100):
    """
    Copied the user_image function from /lib/ckan/default/src/ckan/ckan/lib/helpers and revised to use get_thumbnail for user image
    FIXME: Is there a better way to do this?

    Args:
        user_id ( str): user id
        size (int, optional): Size to display image. Defaults to 100.

    Returns:
        str: html block for displaying user image
    """

    try:
        user_dict = logic.get_action('user_show')(
            {'ignore_auth': True},
            {'id': user_id}
        )
    except logic.NotFound:
        return ''

    gravatar_default = toolkit.config.get('ckan.gravatar_default', 'identicon')

    if user_dict['image_display_url']:
        return h.literal('''<span class="user-badge"><img src="{url}"
                       class="user-image"
                       width="{size}" height="{size}" alt="{alt}" /></span>'''.format(
            url=h.sanitize_url(get_thumbnail(user_dict['image_display_url'])),
            size=size,
            alt=user_dict['name']
        ))
    elif gravatar_default == 'disabled':
        return h.snippet(
            'user/snippets/placeholder.html',
            size=size, user_name=user_dict['display_name'])
    else:

        return h.literal('''<span class="user-badge"><svg>
            <circle cx="50%" cy="50%" r="35%" />
            <text x="50%" y="50%" dy="0.3em" >{alt}</text>
            Sorry, your browser does not support inline SVG.
            </svg></span>
            '''.format(
            alt=user_dict['display_name'][0:1]
        ))
    
def twdh_linked_user(user, maxlength=0, avatar=20):
    """
    Copied the linked_user function from /lib/ckan/default/src/ckan/ckan/lib/helpers and revised to not use twdh_user_image
    FIXME: Is there a better way to do this?

    Args:
        user ( str): username or user object, 
        maxlength (int, optional): length at which to truncate username. Defaults to 0.
        avatar (int, optional): size to display user avatar. Defaults to 20.

    Returns:
        _type_: _description_
    """

    if not isinstance(user, h.model.User):
        user_name = h.text_type(user)
        user = h.model.User.get(user_name)
        if not user:
            return user_name
    if user:
        name = user.name if h.model.User.VALID_NAME.match(user.name) else user.id
        displayname = user.display_name

        if maxlength and len(user.display_name) > maxlength:
            displayname = displayname[:maxlength] + '...'

        return h.literal(u'{icon} {link}'.format(
            icon=twdh_user_image(
                user.id,
                size=avatar
            ),
            link=h.link_to(
                displayname,
                h.url_for('user.read', id=name)
            )
        ))

def twdh_datetime_now():
    """
    Return a formatted string of the current date
    It would be nice to write this as a Jinja filter

    Args:
        None

    Returns:
        string: current date
    """
    now = datetime.now()
    return now.strftime("%m/%d/%Y, %I:%M%p").lower()


def data_dictionary_to_csv( ddict ):
    """
    Return a csv string of the resource

    Args:
        ddict: data dictionary dict

    Returns:
        string: csv formatted representation of the resource data dictionary
    """

    columns = ['Column','Type','Label','Description']

    csv_file = io.StringIO()
    #csv_writer = csv.writer(csv_file,dialect='unix',quoting=csv.QUOTE_NONE, escapechar='\\')
    csv_writer = csv.writer(csv_file)

    csv_writer.writerow( columns )

    for field in ddict:
        row = []
        row.append( field['id'] )

        # check for type_override value and if it exists use it, otherwise use default type value
        if 'info' in field:
            if 'type_override' in field['info']:
                row.append( field['info']['type_override'] )
            else:                
                row.append( field['type'] )

            if 'label' in field['info']:
                row.append( field['info']['label'] )
            else:
                row.append( '' )

            if 'notes' in field['info']:
                row.append( field['info']['notes'] )
            else:
                row.append( '' )

        else:
            row.append( '' )
            row.append( '' )
            row.append( '' )

        csv_writer.writerow( row )
            
    return csv_file.getvalue()

def json_to_dict( json_string ):
    """
    Return a dict of the json string

    Args:
        json: json string

    Returns:
        string: dict representation of the json string
    """

    return json.loads(json_string)

def render_dataset_date_range( date_string ):
    """
    Return a string with formatted dates

    Args: date_string, formatted as "dd/mm/yyyy - dd/mm/yyyy"
        
    Returns:
        string: string with formatted dates

    FIXME: 
        h.render_datetime returns a date 1 day in the past, probably a TZ bug. 
    """

    from_date, to_date = date_string.split( ' - ' )

    from_month, from_day, from_year = from_date.split( '/' )
    to_month, to_day, to_year = to_date.split( '/' )

    from_date = h.literal(u'{from_year}-{from_month}-{from_day} 12:00:00'.format(
        from_day = from_day, 
        from_month = from_month, 
        from_year = from_year
    ))

    to_date = h.literal(u'{to_year}-{to_month}-{to_day} 12:00:00'.format(
        to_day = to_day, 
        to_month = to_month, 
        to_year = to_year
    ))


    if from_year == to_year and from_month == to_month:
        return h.literal(u'{from_date}'.format(
                from_date=h.render_datetime( from_date, "%b %Y" )
        ))
    else:
        return h.literal(u'{from_date} - {to_date}'.format(
                from_date=h.render_datetime( from_date, "%b %Y" ),
                to_date=h.render_datetime( to_date, "%b %Y" ),
        ))

def get_tag(tag_name):
    """
    Return a CKAN tag object

    Args: tag_name string
        
    Returns:
        string: Tag object for tag with name=tag_name

    """

    from ckan.model.tag import Tag

    return Tag( name=tag_name )

def title_case( str ):
    """
    Return a string in Title Case

    Args: string
        
    Returns:
        string: string formatted in Title Case

    """

    return str.title()

def clean_string( str ):
    """
    Return a string with all non-alphanumeric characters removed
    Args: string
        
    Returns:
        string: string with all non-alphanumeric characters removed
    """
    if not str:
        return ''
    result = []
    if isinstance(str, list):
        result.extend(re.sub( '[^a-zA-Z0-9-]+', '', s ) for s in str[0].split(','))
    else:
        result.extend(re.sub( '[^a-zA-Z0-9-]+', '', str ))
    return result

def get_referrer():
    """
    Return referrer URL
    Args: none
        
    Returns:
        string: referrer URL string
    """
    return request.headers.get("Referer")

def has_unavailable_resources( dataset ):
    """
    Return a boolean indicating whether any of the resources in the dataset are marked as unavailability by the check_link report
    Args: dataset: dict containing the dataset package used on the dataset detail page
        
    Returns:
        boolean: true if 1 or more datasets are marked as unavailable
    """

    has_unavailable_resources = False

    for resource in dataset["resources"]:
        if "url" in resource:
            try:
                report = toolkit.get_action("check_link_url_search")(
                    {},
                    {
                        "url": resource["url"]
                    },
                )
                if "count" in report and report["count"] > 0:
                    if report["results"][0]["state"] != "available":
                        has_unavailable_resources = True
            except:
                pass
            
    return has_unavailable_resources

def check_resource_links( dataset ):
    """
    Args: dataset id
        
    Returns:
        boolean: true if resources are available, false if 1 or more resource links are broken
    """

    log.debug(  'Checking resource links for {}'.format( dataset["id"] ) );

    context = {}
    results = []
    check = toolkit.get_action("check_link_resource_check")

    for resource in dataset["resources"]:
        if "url" in resource:
            try:
                log.debug( resource["url"] )
                result = check(
                    context.copy(),
                    {
                        "save": True,
                        "clear_available": False,
                        "id": resource["id"],
                        "link_patch": {"delay": 0, "timeout": 10},
                    },
                )
            except toolkit.ValidationError as e:
                log.error("Cannot check %s: %s", res.id, e)
                result = {"state": "exception"}
            log.debug( result )

    return not has_unavailable_resources( dataset )

def twdh_combine_tags( primary, secondary ):
    """
    Return union of primary and secondary
        
    Returns: list of tags
    """

    try:
        return primary + secondary
    except:
        return []

def twdh_provided_secret():
    """
    Return True if request contains secret=abracadabra
    Args: none
        
    Returns:
        boolean: True if request contains secret=abracadabra
    """

    if "secret" in toolkit.request.values:
        secret = toolkit.request.values["secret"]
        if( secret == "abracadabra" ):
            return True
        else:
            return False


def get_tag_label( tag_value ):
    """
    Return tag label
    Args: tag value
        
    Returns:
        string: tag label
    """

    schema = scheming.helpers.scheming_get_dataset_schema('dataset')
    field = scheming.helpers.scheming_field_by_name(schema['dataset_fields'], 'primary_tags')

    for choice in scheming.helpers.scheming_field_choices( field ):
        if choice['value'] == tag_value['name']:
            return choice['label']

    if 'display_name' in tag_value:
        return tag_value['display_name']
    elif 'name' in tag_value:
        return tag_value['name']


def escape_survey_html( str ):
    """
    Args: 
        str to be escaped
        
    Returns:
        string: escaped string

    Notes:
        I can't explain why the /script> at the end of the embed code needs to be escaped, but it does. This may break if the Survey123 code changes but the upside is that this method allows the admins to update the survey embed code on using the admin console.

    """

    return str.replace("/script>", r"\\/script>").replace("'", r"\'")


class TwdhThemePlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.ITranslation)
    plugins.implements(IPagesSchema)
    implements(interfaces.IFacets, inherit=True)
    implements(interfaces.IBlueprint, inherit=True)
    implements(interfaces.IAuthFunctions)
    implements(interfaces.IPackageController)
    implements(interfaces.IActions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets', 'ckanext-twdh_theme')

    def update_config_schema(self, schema):

        # Prevent logo and title from being changed using the UI
        # del schema['ckan.site_logo']
        # del schema['ckan.site_title']

        schema.update(
        {
            'ckan.survey_embed_code': [
            ],
            'ckan.landing_tab_1': [
            ],
            'ckan.landing_tab_2': [
            ],
            'ckan.landing_tab_3': [
            ],

        })

        return schema

    # ITemplateHelpers

    def get_helpers(self):
            """Register twdh helper functions"""

            return {'twdh_recent_datasets': recent_datasets,
                    'twdh_popular_datasets': popular_datasets,
                    'twdh_statewide_datasets': statewide_datasets,
                    'twdh_dataset_count': dataset_count,
                    'showcase_count': showcase_count,
                    'twdh_statewide_dataset_count': statewide_dataset_count,
                    'twdh_get_groups': groups,
                    'twdh_get_showcases': showcases,
                    'twdh_get_package_metadata': get_package_metadata,
                    'twdh_order_by_display_group': order_by_display_group,
                    'twdh_scheming_groups_choices': scheming_groups_choices,
                    'twdh_is_new': is_new,
                    'twdh_linked_resource_count': linked_resource_count,
                    'get_thumbnail': get_thumbnail,
                    'twdh_linked_user': twdh_linked_user,
                    'twdh_user_image': twdh_user_image,
                    'get_group_by_name': get_group_by_name,
                    'get_group_by_id': get_group_by_id,
                    'get_organization_groups': get_organization_groups,
                    'get_organization_admins': get_organization_admins,
                    'strip_url': strip_url,
                    'twdh_datetime_now': twdh_datetime_now,
                    'data_dictionary_to_csv': data_dictionary_to_csv,
                    'json_to_dict': json_to_dict,
                    'render_dataset_date_range': render_dataset_date_range,
                    'get_tag': get_tag,
                    'title_case': title_case,
                    'clean_string': clean_string,
                    'get_referrer': get_referrer,
                    'has_unavailable_resources': has_unavailable_resources,
                    'check_resource_links': check_resource_links,
                    'twdh_combine_tags': twdh_combine_tags,
                    'twdh_provided_secret': twdh_provided_secret,
                    'get_tag_label': get_tag_label,
                    'escape_survey_html': escape_survey_html

                }
    
    #IPagesSchema
    def update_pages_schema(self, schema):
        schema.update(
        {
            'include_contact_form': [
                toolkit.get_validator('not_empty'),
                toolkit.get_validator('boolean_validator')
            ],
            'include_suggest_dataset_form': [
                toolkit.get_validator('not_empty'),
                toolkit.get_validator('boolean_validator')
            ],
            'seo_title': [
                toolkit.get_validator('ignore_missing')
            ],
            'seo_description': [
                toolkit.get_validator('ignore_missing')
            ]

        })
        return schema

    ## IBlueprint
    def get_blueprint(self):
        return routes.blueprints

    ## IAuthFunctions
    def get_auth_functions(self):
        ''' '''
        return {
            'zip_resource': zip_resource
        }


    # IFacets

    def dataset_facets(self, facets_dict, package_type):

        # Remove the 'License' facet
        facets_dict.popitem()
        
        return facets_dict

    # BUG: group_facets applies to both group_facets and organization_facets
    # Fixed by this commit, post-2.9.5 https://github.com/ckan/ckan/pull/6682
    # When we upgrade CKAN, we will need to add a def for organization_facets below

    def group_facets(self, facets_dict, group_type, package_type):
        # exclude 'Licenses' from facet options
        return {
            'groups': _('Groups'),
            'tags': _('Tags'),
            'res_format': _('Formats'),
            'placeKeywords': _('Spatial Keywords')
        }        

    # IPackageController

    def read(self, entity):
        pass

    def create(self, entity):
        pass

    def edit(self, entity):
        pass

    def authz_add_role(self, object_role):
        pass

    def authz_remove_role(self, object_role):
        pass

    def delete(self, entity):
        pass

    def before_search(self, search_params):
        if search_params.get('q'):
            search_params['qf'] = 'extras_primary_tags^9 extras_secondary_tags^7.5 title^6.2 notes^2 extras_spatial_description^1.5 extras_caveats_usage^1 extras_additional_information^0.5'
        return search_params

    def after_search(self, search_results, search_params):

        '''
        log.debug( "search_results" )
        log.debug( search_results )
        log.debug( "search_params" )
        log.debug( search_params )
        '''
        return search_results

    def before_index(self, data_dict):
        if data_dict.get('extras_spatial_details', ''):
            spatial_details = json.loads(data_dict.get('extras_spatial_details'))
            geometry = spatial_details.get('features')[0].get('geometry')
            if geometry.get('type') != 'Point' and len(geometry.get('coordinates')[0]) > 5:
                bounds = spatial_details.get('bounds')
                coordinates = [[[bounds.get('w'), bounds.get('s')], [bounds.get('w'), bounds.get('n')], [bounds.get('e'), bounds.get('n')], [bounds.get('e'), bounds.get('s')], [bounds.get('w'), bounds.get('s')]]]
                spatial_details.get('features')[0].get('geometry').pop('coordinates')
                spatial_details.get('features')[0].get('geometry')['coordinates'] = coordinates
            data_dict['extras_spatial'] = json.dumps(spatial_details.get('features')[0].get('geometry'))
        return data_dict

    def before_view(self, pkg_dict):

        resources = []

        if "related_resources" in pkg_dict:
            for resource in pkg_dict["related_resources"]:
                try:
                    resources.append( toolkit.get_action('package_show')(None, {'id': resource, 'include_tracking': True}) )
                except:
                    pass

            pkg_dict['related_resources'] = resources

        return pkg_dict

    def after_create(self, context, data_dict):
        return data_dict

    def after_update(self, context, data_dict):
        return data_dict

    def after_delete(self, context, data_dict):
        return data_dict

    def after_show(self, context, data_dict):
        return data_dict

    def update_facet_titles(self, facet_titles):
        return facet_titles

    # BEGIN Hooks for IActions

    def get_actions(self):

      return {
            'user_create': action.user_create
        }

    # END Hooks for IActions