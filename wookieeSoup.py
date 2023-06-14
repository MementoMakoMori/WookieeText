from bs4 import BeautifulSoup as bs
import requests
import re
import json
h = "starwars.fandom.com"


def block_cats(title: str, ref: str) -> bool:
    assert ref in ["org", "loc", "occ"]
    if ref == "org":
        words = [r'[I|i]ndividuals', r'Families', r'\b[P|p]ersonnel', r'\b[M|m]embers\b', r'\b[V|v]ehicles',
                 r'[D|d]roid model', r'droids', r'\b[R|r]ank', r'\b[S|s]pecies', r'[M|m]ilitary units?', r'\b[C|c]lans',
                 r'\b[R|r]esidents', r'[O|o]fficers', r'[A|a]dmirals and generals', r'[M|m]atriarchs',
                 r'\b[O|o]ccupations?\b', r'\b[B|b]attles?\b', r'[C|c]onflicts?', r'\b[L|l]ocations?',
                 r'[U|u]nidentified']
    elif ref == "loc":
        words = [r'[I|i]ndividuals', r'Families', r'\b[P|p]ersonnel', r'\b[M|m]embers\b', r'\b[V|v]ehicles',
                 r'[D|d]roid model', r'droids', r'\b[R|r]ank', r'\b[S|s]pecies', r'[M|m]ilitary units?', r'\b[C|c]lans',
                 r'\b[R|r]esidents', r'[O|o]fficers', r'[A|a]dmirals and generals', r'[M|m]atriarchs',
                 r'\b[O|o]ccupations?\b', r'\b[B|b]attles?\b', r'[C|c]onflicts?', r'[U|u]nidentified']
    elif ref == "occ":
        words = [r'[I|i]ndividuals', r'Families', r'\b[P|p]ersonnel', r'\b[M|m]embers\b', r'\b[V|v]ehicles',
                 r'[D|d]roid model', r'\bdroids\b', r'\b[S|s]pecies', r'\b[C|c]lans', r'\b[R|r]esidents',
                 r'[M|m]atriarchs', r'\b[B|b]attles?\b', r'[C|c]onflicts', r'\b[L|l]ocations?',
                 r'[U|u]nidentified']
    for word in words:
        if re.search(word, title):
            return False
    return True


def scrape_occ(host: str, category: str, ):
    soup = bs(requests.get("".join(["https://", host, category])).content, 'html.parser')
    print("Scraping Category: {}".format(category))
    if block_cats(soup.find(class_="page-header__categories").get_text(), "occ"):
        members = soup.find_all('div', class_="category-page__members-wrapper")
        for each in members:
            each_lttr = each.find('div', class_="category-page__first-char")
            if each_lttr and "*" not in each_lttr.get_text():
                for member in each.find_all('a', class_="category-page__member-link"):
                    t = member.get("title")
                    if "Category" in t:
                        if not occ_seen_cat.get(t) and block_cats(t, "occ"):
                            occ_seen_cat[t] = True
                            scrape_occ(host, member.get("href"))
                    else:
                        if not occs.get(t):
                            occs[t] = {"url": member.get("href"), "content": scrape_page(host, member.get("href"))}


def scrape_page(host: str, link: str):
    return bs(requests.get("".join(["https://", host, link])).content, 'html.parser')


occs = dict()
occ_seen_cat = dict()
scrape_occ(h, "/wiki/Category:Occupations")
print(list(occs.keys())[(slice(933, 1333, 40))])
# there still some !@#$%& individual people in the jobs files -_-
rm_cats = [r'\bIndividuals\b', r'\b[P|p]ersonnel\b', r'\b[U|u]nidentified\b']
rm_title2 = []
for each in occs.keys():
    header = occs.get(each).get('content').find(class_="page-header__categories").get_text()
    total = 0
    for word in rm_cats:
        if bool(re.search(word, header)):
            total += 1
    if total > 0:
        rm_title2.append(each)
for each in rm_title2:
    del occs[each]

# save jobs to file
for each in occs.keys():
    occs[each]["content"] = str(occs.get(each).get("content"))
with open('jobs.json', 'w') as f:
    f.write(json.dumps(occs))
f.close()
# # to read back in
# with open('jobs.json', 'r') as f:
#     occs = json.load(f)
# f.close()
# for each in occs.keys():
#     occs[each]['content'] = bs(occs.get(each).get('content'), 'html.parser')


def location_names(host: str, category: str = "/wiki/Category:Locations", rc: int = 0):
    soup = bs(requests.get("".join(["https://", host, category])).content, 'html.parser')
    print("Getting members of {}".format(category))
    for member in soup.find_all('a', class_="category-page__member-link"):
        t = member.get("title")
        if "Category" in t:
            if not loc_seen_cat.get(t) and block_cats(t, "loc") and rc <= 3:
                loc_seen_cat[t] = True
                location_names(host, member.get("href"), rc+1)
        else:
            if not locations.get(t) and "nidentified" not in t:
                locations[t] = {"url": member.get("href")}


locations, loc_seen_cat = dict(), dict()
# this long version has 31522 locations across 3963 categories
location_names(h, "/wiki/Category:Locations")

# save locations just like jobs
with open('long_locs.json', 'w') as f:
    f.write(json.dumps(locations))
f.close()

# # to read back in
# with open('long_locs.json', 'r') as f:
#     locations = json.load(f)
# f.close()

# # for a MUCH smaller list, start at the Locations by affiliation subcategory page
# # 5252 locations across 222 categories
# locations = dict()
# loc_seen_cat = dict()
location_names(h, "/wiki/Category:Locations_by_affiliation")

with open('short_locs.json', 'w') as f:
    f.write(json.dumps(locations))
f.close()

# # to read back in
# with open('short_locs.json', 'r') as f:
#     locations = json.load(f)
# f.close()


def org_names(host: str, category: str = "/wiki/Category:Organizations", rc: int = 0):
    soup = bs(requests.get("".join(["https://", host, category])).content, 'html.parser')
    if block_cats(soup.find(class_="page-header__categories").get_text(), "org"):
        print("Getting members of {}".format(category))
        for member in soup.find_all('a', class_="category-page__member-link"):
            if "Category" in member.get("href"):
                t = member.get("title")
                if not org_seen_cat.get(t) and block_cats(t, "org") and rc <= 3:
                    org_seen_cat[t] = True
                    org_names(host, member.get("href"), rc+1)
            else:
                if not orgs.get(member.get("title")) and "nidentified" not in member.get("title"):
                    orgs[member.get("title")] = {"url": member.get("href")}


orgs, org_seen_cat = dict(), dict()
# 7119 orgs from 376 categories
# REFINED: 5115 orgs from 286 categories
org_names(h)

# save locations just like jobs
# with open('orgs.json', 'w') as f:
#     f.write(json.dumps(orgs))
# f.close()
# # to read back in
# with open('orgs.json', 'r') as f:
#     orgs = json.load(f)
# f.close()
