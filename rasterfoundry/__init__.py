# Flag to indicate whether notebook support is available
try:
    import ipyleaflet
    NOTEBOOK_SUPPORT = True
except ImportError:
    NOTEBOOK_SUPPORT = False
