import os.path

application = "/Users/michaelsamjatin/repos/CW/dist/CSV Formatter.app"
appname = os.path.basename(application)

format = 'UDBZ'
size = '120M'

files = [application]

symlinks = {
    'Applications': '/Applications'
}

badge_icon = 'icon.icns'

icon_locations = {
    appname: (100, 100),
    'Applications': (300, 100),
}

background = None

default_view = 'icon-view'
show_icon_preview = False
show_item_info = False

icon_size = 80
text_size = 16

arrange_by = None
grid_offset = (0, 0)
grid_spacing = 100

scroll_position = (0, 0)

label_pos = 'bottom'
include_icon_view_settings = 'auto'
include_list_view_settings = 'auto'

window_rect = ((200, 120), (520, 360))

list_icon_size = 16
list_text_size = 12
list_scroll_position = (0, 0)
list_sort_by = 'name'
list_use_relative_dates = True
list_calculate_all_sizes = False,
list_columns = ('name', 'date-modified', 'size', 'kind', 'date-added')
list_column_widths = {
    'name': 300,
    'date-modified': 181,
    'size': 97,
    'kind': 115,
    'date-added': 181
}

list_column_sort_directions = {
    'name': 'ascending',
    'date-modified': 'descending',
    'size': 'descending',
    'kind': 'ascending',
    'date-added': 'descending'
}