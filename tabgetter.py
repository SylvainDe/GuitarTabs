import tabs


class GuitarTabGetter(object):

    @classmethod
    def get_class_for_url(cls, url):
        print(url)
        for class_ in (tabs.GuitarTabFromUltimateGuitar,
                       tabs.GuitarTabFromGuitarTabDotCom,
                       tabs.GuitarTabFromTabs4Acoustic,
                       tabs.GuitarTabFromGuitarTabsDotCc,
                       tabs.GuitarTabFromEChords,
                       tabs.GuitarTabFromSongsterr,
                       tabs.GuitarTabFromAzChords,
                       tabs.GuitarTabFromBoiteAChansons,
                       tabs.GuitarTabFromGuitarTabsExplorer):
            for prefix in class_.prefixes:
                if url.startswith(prefix):
                    return class_
        raise Exception("Unsupported URL %s" % url)

    @classmethod
    def from_url(cls, url):
        return cls.get_class_for_url(url).from_url(url)

    @classmethod
    def from_list_url(cls, url):
        return cls.get_class_for_url(url).from_list_url(url)
