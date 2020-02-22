class Style:
    def __init__(self,title,path,thumb=None,artist=None):
        self.title = title
        self.artist = artist
        self.path = path
        self.thumb = thumb
        
    def __str__(self):
        style_str = '"{}"'.format(self.title)
        if self.artist:
            style_str = "{0} by {1}".format(style_str,self.artist)
        return '{0} ({1})'.format(style_str,self.path)
