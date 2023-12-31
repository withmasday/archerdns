import os, re, sys, requests, cloudscraper
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
scraper = cloudscraper.create_scraper()

class Subdomain:
    def __init__(self, domain):
        self.domain = domain
        self.ua = UserAgent()
        self.headers = {'User-Agent': str(self.ua)}
        self.timeout = 30
        self.path = open('securitytrails.path', 'r').read()
        
    def regexers(self, data, filename, platform):
        try:
            lines = list(dict.fromkeys(data))
            print (f'[ {platform} ] {self.domain} get {len(lines)}')
            for line in lines:
                open(filename, 'a').write(line +'\n')
        except:pass

    def alienvault(self):
        try:
            response = requests.get('https://otx.alienvault.com/api/v1/indicators/domain/'+ self.domain +'/passive_dns', headers=self.headers, timeout=self.timeout).text
            regex = re.findall(r'"hostname": "(.*?)", "record_type"', response)
            self.regexers(regex, 'domain.txt', 'ALIENVAULT')
        except:pass

    def crtsh(self):
        try:
            response = requests.get('https://crt.sh/?q='+ self.domain +'&output=json', headers=self.headers, timeout=self.timeout).text
            regex = re.findall(r'"common_name":"(.*?)","name_value"', response)
            self.regexers(regex, 'domain.txt', 'CRT.sh')
        except:pass

    def dnsdumpster(self):
        try:
            sess = requests.session()
            tokenGet = sess.get('https://dnsdumpster.com/')
            cookies = tokenGet.cookies.get_dict()
            csrftoken = cookies['csrftoken']
            token = re.findall('name="csrfmiddlewaretoken" value="(.*?)"', tokenGet.text)[0]

            data = {"csrfmiddlewaretoken": token, "targetip": self.domain, "user": "free"}
            dnsdumpsterHeaders = {"csrftoken": csrftoken, "Referer": "https://dnsdumpster.com/"}

            response = sess.post('https://dnsdumpster.com/', headers=dnsdumpsterHeaders, data=data, timeout=self.timeout).text
            domains = re.findall(r'httpheaders/\?q=http://(.*?)" data-target="#myModal"', response)
            self.regexers(domains, 'domain.txt', 'DNSDUMPSTER SUBDOMAIN')

            ips = re.findall(r'mtr/\?q=(.*?)" data-target="#myModal"', response)
            self.regexers(ips, 'ip.txt', 'DNSDUMPSTER IP')
        except:pass
        
    def rapiddns(self):
        try:
            response = requests.get('https://rapiddns.io/subdomain/'+ self.domain +'?full=1&down=1#result', headers=self.headers, timeout=self.timeout).text
            domains = re.findall(r'</th>\n<td>(.*?)</td>', response)
            self.regexers(domains, 'domain.txt', 'RAPIDDNS')
        except:pass
        
    def rasenmedia(self):
        try:
            data = {'input': self.domain, 'execute': 'Scan'}
            response = requests.post('https://rasenmedia.my.id/tools/networking/subdomain-scanner', headers=self.headers, data=data, timeout=self.timeout).text
            soup = BeautifulSoup(response, 'html.parser')
            domains = soup.find('textarea',{'class':'form-control'}).text
            if 'Not Found!' in domains:
                return False
            
            domains = domains.split('\n')
            domains = list(filter(None, domains))
            self.regexers(domains, 'domain.txt', 'RASENMEDIA')
        except:pass
    
    def securitytrails(self):
        try:
            response = scraper.get('https://securitytrails.com/_next/data/'+ self.path +'/list/apex_domain/'+ self.domain +'.json?domain='+ self.domain, headers=self.headers, timeout=self.timeout).text
            if '<title>Just a moment...</title>' in response:
                return False
            else:pass
            
            domains = re.findall('"hostname":"(.*?)",', response)
            self.regexers(domains, 'domain.txt', 'SECURITYTRAILS')
            
            max = re.findall('"pages":(.*?),"records"', response)[0]
            if int(max) == 1:
                return True
            else:pass
            
            for page in range(1, int(max + 1)):
                response = scraper.get('https://securitytrails.com/_next/data/'+ self.path +'/list/apex_domain/'+ self.domain +'.json?page='+ page +'&domain='+ self.domain, headers=self.headers, timeout=self.timeout).text
                if '<title>Just a moment...</title>' in response:
                    return False
                else:pass
                
                domains = re.findall('"hostname":"(.*?)",', response)
                self.regexers(domains, 'domain.txt', 'SECURITYTRAILS')
                
        except:pass
    
    def hackertarget(self):
        try:
            domains = []
            ips = []

            response = scraper.get('https://api.hackertarget.com/hostsearch/?q='+ self.domain, headers=self.headers, timeout=self.timeout).text
            
            if 'API count exceeded' in response:
                return False
            else:pass
            
            response = response.split('\n')
            response = list(filter(None, response))
            
            
            for data in response:
                data = data.split(',')
                domains.append(data[0])
                ips.append(data[1])
                
            self.regexers(domains, 'domain.txt', 'HACKERTARGET DOMAIN')
            self.regexers(ips, 'ip.txt', 'HACKERTARGET IP')
        except:pass