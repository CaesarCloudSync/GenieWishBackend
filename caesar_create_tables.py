class CaesarCreateTables:
    def __init__(self) -> None:
        self.quotapostersfields = ("company","email","password","quoterkey")
        self.contributorsfields = ("contributor","email","password","emailhash","contributorid")
        self.quotasfields = ("quoter","quotatitle","quotatype","thumbnailfilename","thumbnail","description","visibility","quotahash","quoterkey","thumbnailfiletype")
        self.numquotas = ("quoterkey","numofquotas")
        self.quotatypes = ("quotatype",)
        self.quotamagneturifields = ("quotamagneturi","torrentfilename","quotahash","contributor","quoter","filesize")
        self.askcontribpermisionfield = ("quoter","contributor","quotahash","permissionstatus")
    def create(self,caesarcrud):
        caesarcrud.create_table("quotaposterid",self.quotapostersfields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL"),
        "quotaposters")
        caesarcrud.create_table("contributorkeyid",
        self.contributorsfields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL"),
        "contributors")
        caesarcrud.create_table("quotaid",
        self.quotasfields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL",
         "mediumblob NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL",
         "varchar(255) NOT NULL","varchar(255) NOT NULL"),
        "quotas")
        caesarcrud.create_table("quotatypeid",
        self.quotatypes,
        ("varchar(255) NOT NULL",),
        "quotatypes")
        caesarcrud.create_table("askcontribpermisionid",
        self.askcontribpermisionfield,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL"),
        "askcontribpermission")
        caesarcrud.create_table("quotamagneturid",
        self.quotamagneturifields,
        ("TEXT NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","BIGINT NOT NULL"),
        "quotamagneturis")