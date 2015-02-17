from ppsay.sources import get_source_if_matches
import socket
import feedparser

socket.setdefaulttimeout(10.0)

weeklies = ['http://www.tewkesburyadmag.co.uk',
 'http://www.suttonguardian.co.uk',
 'http://www.wandsworthguardian.co.uk',
 'http://www.wallingfordherald.co.uk',
 'http://www.sthelensstar.co.uk',
 'http://www.richmondandtwickenhamtimes.co.uk',
 'http://www.herefordtimes.com',
 'http://www.enfieldindependent.co.uk',
 'http://www.basingstokegazette.co.uk',
 'http://www.bucksfreepress.co.uk',
 'http://www.darlingtonandstocktontimes.co.uk',
 'http://www.haringeyindependent.co.uk',
 'http://www.hampshirechronicle.co.uk',
 'http://www.witneygazette.co.uk',
 'http://www.essexcountystandard.co.uk',
 'http://www.times-series.co.uk',
 'http://www.gazetteseries.co.uk',
 'http://www.bridgwatermercury.co.uk',
 'http://www.middevonstar.co.uk',
 'http://www.kingstonguardian.co.uk',
 'http://www.maldonandburnhamstandard.co.uk',
 'http://www.ilkleygazette.co.uk',
 'http://www.middlewichguardian.co.uk',
 'http://www.freepressseries.co.uk',
 'http://www.stalbansreview.co.uk',
 'http://www.bicesteradvertiser.net',
 'http://www.chorleycitizen.co.uk',
 'http://www.didcotherald.co.uk',
 'http://www.bridportnews.co.uk',
 'http://www.hillingdontimes.co.uk',
 'http://www.burytimes.co.uk',
 'http://www.messengernewspapers.co.uk',
 'http://www.andoveradvertiser.co.uk',
 'http://www.wharfedaleobserver.co.uk',
 'http://www.westerntelegraph.co.uk',
 'http://www.dailyecho.co.uk',
 'http://www.swanageandwarehamadvertiser.co.uk',
 'http://www.tivysideadvertiser.co.uk',
 'http://www.ealingtimes.co.uk',
 'http://www.theadvertiserseries.co.uk',
 'http://www.campaignseries.co.uk',
 'http://www.halesowennews.co.uk',
 'http://www.braintreeandwithamtimes.co.uk',
 'http://www.swindonadvertiser.co.uk',
 'http://www.knutsfordguardian.co.uk',
 'http://www.durhamtimes.co.uk',
 'http://www.cotswoldjournal.co.uk',
 'http://www.alcesterchronicle.co.uk',
 'http://www.wantageherald.co.uk',
 'http://www.redditchadvertiser.co.uk',
 'http://www.eveshamjournal.co.uk',
 'http://www.wirralglobe.co.uk',
 'http://www.harrowtimes.co.uk',
 'http://www.guardian-series.co.uk',
 'http://www.barryanddistrictnews.co.uk',
 'http://www.thurrockgazette.co.uk',
 'http://www.stroudnewsandjournal.co.uk',
 'http://www.borehamwoodtimes.co.uk',
 'http://www.worcesternews.co.uk',
 'http://www.cravenherald.co.uk',
 'http://www.wimbledonguardian.co.uk',
 'http://www.falmouthpacket.co.uk',
 'http://www.thewestmorlandgazette.co.uk',
 'http://www.surreycomet.co.uk',
 'http://www.clactonandfrintongazette.co.uk',
 'http://www.theargus.co.uk/leader',
 'http://www.wiltsglosstandard.co.uk',
 'http://www.somersetcountygazette.co.uk',
 'http://www.watfordobserver.co.uk',
 'http://www.croydonguardian.co.uk',
 'http://www.asianimage.co.uk',
 'http://www.truropacket.co.uk',
 'http://www.chardandilminsternews.co.uk',
 'http://www.thepacket.co.uk',
 'http://www.yeovilexpress.co.uk',
 'http://www.northwichguardian.co.uk',
 'http://www.southendstandard.co.uk',
 'http://www.thetelegraphandargus.co.uk',
 'http://www.gazette-news.co.uk',
 'http://www.kidderminstershuttle.co.uk',
 'http://www.chelmsfordweeklynews.co.uk',
 'http://www.streathamguardian.co.uk',
 'http://www.leighjournal.co.uk',
 'http://www.thisisthewestcountry.co.uk',
 'http://www.newsshopper.co.uk',
 'http://www.penarthtimes.co.uk',
 'http://www.epsomguardian.co.uk',
 'http://www.basildonrecorder.co.uk',
 'http://www.oxfordtimes.co.uk',
 'http://www.droitwichadvertiser.co.uk',
 'http://www.keighleynews.co.uk',
 'http://www.romseyadvertiser.co.uk',
 'http://www.oxfordmail.co.uk',
 'http://www.warringtonguardian.co.uk',
 'http://www.theboltonnews.co.uk',
 'http://www.milfordmercury.co.uk',
 'http://www.redhillandreigatelife.co.uk',
 'http://www.camborneredruthpacket.co.uk',
 'http://www.stourbridgenews.co.uk',
 'http://www.dudleynews.co.uk',
 'http://www.berrowsjournal.co.uk',
 'http://www.bexleynewsshopper.co.uk',
 'http://www.brentwoodweeklynews.co.uk',
 'http://www.banburycake.co.uk',
 'http://www.wiltshiretimes.co.uk',
 'http://www.southwalesargus.co.uk',
 'http://www.blackburncitizen.co.uk',
 'http://www.malverngazette.co.uk',
 'http://www.southwalesguardian.co.uk',
 'http://www.bromsgroveadvertiser.co.uk',
 'http://www.ledburyreporter.co.uk',
 'http://www.thepress.co.uk',
 'http://www.gazetteherald.co.uk',
 'http://www.elmbridgeguardian.co.uk',
 'http://www.burnhamandhighbridgeweeklynews.co.uk',
 'http://www.burnleycitizen.co.uk',
 'http://www.ludlowadvertiser.co.uk',
 'http://www.creweguardian.co.uk',
 'http://www.halsteadgazette.co.uk',
 'http://www.salisburyjournal.co.uk',
 'http://www.abingdonherald.co.uk',
 'http://www.harwichandmanningtreestandard.co.uk',
 'http://www.prestwichandwhitefieldguide.co.uk',
 'http://www.winsfordguardian.co.uk']

daylies = ['http://www.echo-news.co.uk',
 'http://www.oxfordmail.co.uk',
 'http://www.thepress.co.uk',
 'http://www.thenorthernecho.co.uk',
 'http://www.swindonadvertiser.co.uk',
 'http://www.theargus.co.uk',
 'http://www.bournemouthecho.co.uk',
 'http://www.dorsetecho.co.uk',
 'http://www.thetelegraphandargus.co.uk',
 'http://www.theboltonnews.co.uk',
 'http://www.heraldscotland.com',
 'http://www.eveningtimes.co.uk',
 'http://www.southwalesargus.co.uk',
 'http://www.dailyecho.co.uk',
 'http://www.lancashiretelegraph.co.uk']

sundays = ['http://www.sundayherald.com']

for url in weeklies:
    print url
    feed = feedparser.parse(url + '/news/rss/')

    def clean_link(x):
        return x.split('#')[0].split('?')[0]

    for item in feed['items']:
        url = clean_link(item['link'])
        print url
        get_source_if_matches(url, 'rss', 'approved', min_candidates=1, min_parties=1, min_constituencies=0)


