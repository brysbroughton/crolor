import crol
from otcregistry import registry_data as rd

rg = crol.Registry(rd)

class Job:

    visited_urls = set([])
    
    def __init__(self):
        pass
        
    
    
class CrawlJob(crol.GenericType):
    """
    CrawlJob must be instantiated with valid registration object,
    or valid parameters for registration and log objects
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'crawljob',
            'registration' : None,
            'log' : None,
            'crawl' : None,
            'has_broken_links' : False
        }
        
        super(CrawlJob, self).__init__(**kwargs)

        if not isinstance(self.registration, crol.Registration):
            self.setprop('registration', crol.Registration(self.registration))

        if not isinstance(self.log, crol.WebLog):
            self.setprop('log', crol.WebLog(self.log or {}))

    def go(self):
        self.log.filename = self.registration.department.name
        self.log.openfile()
        self.setprop('crawl', crol.Crawl({'seed_url':self.registration.site, 'log':self.log}))
        self.crawl.start(self.lognode)#need to pass logging function here
        self.logstats()
        self.log.closefile()
        if self.has_broken_links:
            report_location = self.log.path+self.log.filename+self.log.endfilename
            msg = '<h1>Link Report</h1><p>You can review the report at: <a href="' + report_location + '">this link</a></p>'
            subject = 'Crawl Completed'
            to_address = self.registration.department.main_email
            from_address = 'web@otc.edu'
            email_props = {'to_address':to_address, 'from_address':from_address, 'subject':subject, 'msg_body':msg}
            e = crol.Email(email_props)
            e.send()
    def lognode(self, node):
        if str(node.status) == '404':
            self.has_broken_links = True
        if node.parent == "HEAD":
            self.log.addtable()
            self.log.writerow(['STATUS', 'REASON', 'MIMETYPE', 'URL', 'PARENT'], self.log.tables[0])
            self.log.writerow([node.status, node.reason, node.mimetype, node.url, node.parent], self.log.tables[0])
        else:
            self.log.writerow([node.status, node.reason, node.mimetype, node.url, node.parent.url], self.log.tables[0])
    
    def logstats(self):
        self.log.addtable()
        self.log.writerow(['STAT NAME', 'VALUE'], self.log.tables[1])
        self.log.writerow(['Broken URLs Found:', '999'], self.log.tables[1])
        self.log.writerow(['Redirect URLs Found:', '999'], self.log.tables[1])


##this is how the CrawlJob is used
#cj = CrawlJob({'registration':rg.registrations[0]})
#cj.go()


