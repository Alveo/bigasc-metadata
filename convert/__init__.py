from item import ItemMapper, parse_media_filename
from participant import get_participant_list, get_participant, participant_rdf, map_site_name, reset_site_mapping, item_site_name
from session import session_metadata, component_metadata, item_metadata 
from ra_maptask import RAMapTask



## generate a component map, do this only once and we'll use it below
from session import component_map
COMPONENT_MAP = component_map()

def generate_item_path(site, spkr, session, component, basename):
    """Generate a suitable path for an item file"""
    
    componentName = COMPONENT_MAP[int(component)]
    return os.path.join(site, spkr, session, componentName, basename)