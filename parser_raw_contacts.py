from requests_html import HTMLSession
import json

def raw_contacts(contacts):
    print(f"Parsing raw data *****")
    all_contacts_list = []
    for contact in contacts:
        parsed_data = {}
        name = contact["displayName"]
        company = None
        position = None
        if contact["designation"] != None:
            pos_raw = contact["designation"].split(" at ")
            position = pos_raw[0]
            if len(pos_raw)>1:
                company = pos_raw[1]
        profile_type = contact["profileTypes"]

        linkedin = None
        if contact["linkedin"] != None:
            linkedin = contact["linkedin"]["url"]

        parsed_data = {
            "contact_name": name,
            "position": position,
            "company_name": company,
            "profile_type": profile_type,
            "linkedin": linkedin
        }
        
        all_contacts_list.append(parsed_data)
    
    with open(f"parsed_raw_contacts.json", "w+", encoding="utf-8") as f:
        json.dump(all_contacts_list, f, ensure_ascii=False, indent=2)
    
    return all_contacts_list
    
def get_indiv(url):
    print(f"Start crawling API *****")
    with HTMLSession() as session:
        r = session.get(url)
        print(f"response status: {r.status_code} *******")
        r_json = json.loads(r.content)
        return r_json['data']