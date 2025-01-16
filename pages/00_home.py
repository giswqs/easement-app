import solara


@solara.component
def Page():
    with solara.Column(align="center"):
        markdown = """
        ## Visualizing Wetland Inundation Dynamics

        ![](https://i.imgur.com/cj4wI2y.gif)
        """

        solara.Markdown(markdown)
