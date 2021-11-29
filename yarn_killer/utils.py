def get_yarn_weight_list():
    return ['Thread', 'Cobweb', 'Lace', 'Light Fingering', 'Fingering', 'Sport', 'DK', 'Worsted', 'Aran', 'Bulky', 'Super Bulky', 'Jumbo']


def get_fiber_types_list():
    return sorted(['Acrylic', 'Cotton', 'Wool', 'Polyester', 'Silk', 'Bamboo', 'Nylon', 'Rayon', 'Tencel', 'Alpaca', 'Other', 'Cashmere', ''])


def get_texture_list():
    return sorted(['Single-ply', 'Plied (3+)', 'Cabled', 'Tape'])


def get_color_styles_list():
    return ['Solid', 'Heathered', 'Semi-solid/Tonal', 'Variegated', 'Self-striping']


def format_name(name):
    label = name.replace('-', ' ').replace('_', ' ').strip()
    value = label.lower().replace("'", '') 

    return (label, value)
