from urllib import request, error
import xml.etree.ElementTree as ET

def base_data_check(teams_or_players, id):
    '''
    Возвращает данные команды или игрока по его ID. Информация берется с сайта
    http://rating.chgk.info
    :param teams_or_player: {'teams', 'players'}
    :param id: ID команды или игрока
    :return: словарь параметров игрока или команды
    '''
    url_link = 'http://rating.chgk.info/api/%s/%d.xml' % (teams_or_players, id)
    request1 = request.Request(url_link)
    request1.add_header('Host', 'rating.chgk.info')
    request1.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0')
    request1.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    request1.add_header('Accept-Language', 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3')
    request1.add_header('Accept-Encoding', 'gzip, deflate')
    request1.add_header('Connection', 'keep-alive')
    request1.add_header('Upgrade-Insecure-Requests', '1')
    request1.add_header('Cookie', 'chgk_last_seen_news=2016-10-16+00%3A30%3A54')

    try:
        response1 = request.urlopen(request1)
    except error.URLError:
        return {'ConnectionFAILED' : 1}
    xml_string = response1.read().decode()
    root = ET.fromstring(xml_string)

    result_dict = dict()
    #print('LEN ', len(root))
    #print(root.attrib, root.tag, root.text)
    if len(root):
        for item in root[0]:
            result_dict[item.tag] = item.text

    #print(result_dict)
    #print(root[0].attrib, root[0].tag, root[0].text)
    return result_dict


if __name__ == '__main__':
    print(base_data_check('players', 113534))
    print(base_data_check('teams', 28207))