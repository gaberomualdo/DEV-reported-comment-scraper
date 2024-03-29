import requests
import sys
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urljoin
import uuid

searched_links = []

domainToSearch = urlparse(sys.argv[1]).netloc

queue = [sys.argv[1]]

def getLinksFromHTML(html):
    def getLink(el):
        return el["href"]
    return list(map(getLink, BeautifulSoup(html, features="html.parser").select("a[href]")))

def checkForBadComment(html):
    badComment = BeautifulSoup(html, features="html.parser").select(".low-quality-comment");
    return len(badComment) >= 1

while len(queue) > 0:
    for URL in queue:
        if (not (URL in searched_links)) and (not URL.startswith("mailto:")) and (not ("javascript:" in URL)) and (not URL.endswith(".png")) and (not URL.endswith(".jpg")) and (not URL.endswith(".jpeg")):
            try:
                requestObj = requests.get(URL);
                searched_links.append(URL)
                if(requestObj.status_code == 200):
                    if(checkForBadComment(requestObj.text)):
                        print("BAD COMMENT: " + URL)

                        tempFile = open(str(uuid.uuid4()) + ".txt", "w")
                        tempFile.write("BAD COMMENT: " + URL)
                        tempFile.close()

                    else:
                        print("checked but nothing bad: " + URL)

                    if urlparse(URL).netloc == domainToSearch:
                        linksToSearch = getLinksFromHTML(requestObj.text)
                        linksToSearch.sort(key=len)
                        linksToSearch = reversed(linksToSearch)
                        for link in linksToSearch:
                            urlToSearch = urljoin(URL, link)
                            if(urlparse(urlToSearch).netloc == domainToSearch and "#" not in urlToSearch and "?" not in urlToSearch and not urlToSearch.endswith("/edit") and not urlToSearch.endswith("/delete_confirm") and not "/comment" in urlToSearch and len(urlToSearch.split("/")) > 4):
                                queue += [urljoin(URL, link)]
            except Exception as e:
                print("ERROR: " + str(e));
                searched_links.append(domainToSearch)

print("\n--- DONE! ---\n")
