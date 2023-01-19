def setPanel(objConfig):
    # defaults, with spacing, general settings
    # items, recursive, with overrides to defaults
    # first we set the defaults, so that all other defaults passe din are optional overrides
    objDefaults = {
        "spacing": {
            "groupSpacing": 10,
            "itemSpacing": 5,
            "itemSize": 50
        },
        "button": {
            "bg_color": (0.5, 0.5, 0.5, 0.3),
            "text": "",
            "outline_color": (0, 0, 0, 0),
            "roundness": 0.4,
            "corner_radius": 10,
            "has_shadow": True,
            "rounded_corners": (0, 0, 0, 0),
            "iconFile": "",
            "imageSize": (44, 44),
            "imagePosition": (3, 3)
        }
    }
