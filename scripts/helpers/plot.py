import seaborn as sns


PLOT_DEFAULTS = {
    "dpi": 300,
    "bbox_inches": 'tight',
}


def configure_seaborn():
    sns.set_style("ticks")
    sns.set_context("notebook")
    sns.set_palette("deep")
