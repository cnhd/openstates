import json

from billy.scrape.legislators import Legislator, LegislatorScraper


class VTLegislatorScraper(LegislatorScraper):
    jurisdiction = 'vt'
    latest_only = True

    def scrape(self, term, chambers):
        # Load all members via the private API
        LEGISLATOR_DUMP_URL = \
                'http://legislature.vermont.gov/people/loadAll/2016'
        json_data = self.urlopen(LEGISLATOR_DUMP_URL)
        legislators = json.loads(json_data)['data']

        # Parse the information from each legislator
        for info in legislators:
            # Strip whitespace from strings
            info = { k:v.strip() for k, v in info.iteritems() }

            leg = Legislator(
                    term=term,
                    chamber=('upper' if info['Title'] == 'Senator' else 'lower'),
                    district=info['District'],
                    party=info['Party'],
                    email=info['Email'],
                    full_name="{0}{1} {2}".format(
                            info['FirstName'],
                            (" " + info['MI'] if info['MI'] else ""),
                            info['LastName']
                            ),
                    photo_url=
                            'http://legislature.vermont.gov/assets/Documents/Legislators/{}.jpg'.
                            format(info['Email'][ :-(len("@leg.state.vt.us"))]
                            )
                    )
            leg.add_source(
                    'http://legislature.vermont.gov/people/single/2016/{}'.
                    format(info['PersonID'])
                    )
            leg.add_office(
                    type='district',
                    name='District Office',
                    address="{0}{1}\n{2}, {3} {4}".format(
                            info['MailingAddress1'],
                            ("\n" + info['MailingAddress2']
                                    if info['MailingAddress2']
                                    else ""),
                            info['MailingCity'],
                            info['MailingState'],
                            info['MailingZIP']
                            ),
                    phone=(info['HomePhone'] if info['HomePhone'] else None),
                    email=(info['HomeEmail'] if info['HomeEmail'] else None)
                    )
            self.save_legislator(leg)
