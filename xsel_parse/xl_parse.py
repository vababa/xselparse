import xlrd
import sys
from xsel_parse import xml_web_access


class Game():
    '''
    Класс, содержащий словарь {team_name: Team_obj}, а знаыит вмещающий всю информаию по данной игре:
    команды, составы, результаты
    '''

    def __init__(self, teams, tours_num, quest_num, error_list):
        self.tour_numbers = tours_num
        self.question_number = quest_num
        self.team_dict = teams
        self.errors = error_list

    def make_sostav_report(self):
        result = ''
        #sostav_file = open('sostav.csv', 'w')
        for team_key in sorted(self.team_dict.keys()):
            team = self.team_dict[team_key]
            for player in team.players:
                output_list = [str(team.id), team.name, team.city, player.flag, str(player.id)] + player.full_name.split()
                output_line = ';'.join(output_list)
                #print(output_line)
                result += output_line + '\n'
                #sostav_file.write(output_line + '\n')
        #sostav_file.close()
        return result

    def make_score_report(self):
        result = ''
        #score_file = open('itogi.csv', 'w')
        for tour_index in range(self.tour_numbers):
            #print('tour = ', tour_index)
            for team_key in sorted(self.team_dict.keys()):
                team = self.team_dict[team_key]
                #print('team = ', team)
                #print('answers = ', answers)
                output_list = [str(team.id), team.name, team.city, str(tour_index + 1)] + list(map(str, team.answers[tour_index]))
                output_line = ';'.join(output_list)
                #print(output_line)
                result += output_line + '\n'
                #score_file.write(output_line + '\n')
        #score_file.close()
        return result

    def get_errors(self):
        return self.errors

    def print_teams(self):
        for team in self.team_dict.keys():
            print(team)

    def print_sostav(self):
        for team in self.team_dict.keys():
            self.team_dict[team].print_sostav()

    def rating_check(self):
        # Проверяем доступность базы rating.chgk.info
        connetion_check = xml_web_access.base_data_check('teams', 673)
        if 'ConnectionFAILED' in connetion_check.keys():
            self.errors.append('Не выполнена проверка по базе rating.chgk.info: сайт недоступен!')
        else:

            for team in self.team_dict.values():
                #print(team)
                if team.id != 0:
                    rating_team = xml_web_access.base_data_check('teams', team.id)
                    #print(rating_team.keys())
                    if rating_team['name'] != team.name:
                        self.errors.append('Несовпадение названия команды %s (ID %d) с сайтом рейтинга: %s' % (team.name,
                                                                                                               team.id,
                                                                                                               rating_team['name']))
                    if rating_team['town'] != team.city:
                        self.errors.append('Несовпадение города ("%s") - команды ID %d с сайтом рейтинга: %s' % (team.city,
                                                                                                             team.id,
                                                                                                             rating_team['town']))
                    for player in team.players:
                        #print(player)
                        if player.id != 0:
                            last_name, first_name, second_name = player.full_name.split()
                            rating_player = xml_web_access.base_data_check('players', player.id)
                            #print(rating_player.keys())
                            rating_full_name = ' '.join([rating_player['surname'], rating_player['name'],
                                                         rating_player['patronymic']])
                            if not (rating_player['name'] == first_name and rating_player['patronymic'] == second_name and
                                            rating_player['surname'] == last_name):
                                self.errors.append('Несовпадение ФИО игрока %s (ID %d) с сайтом рейтинга: %s' % (player.full_name,
                                                   player.id, rating_full_name))


class Player():
    '''
    Класс, содержащий данные игрока - полное имя, ID, флаг(К, Б, Л), а также названеи и ID команды,
    в составе которой он провел данную игру.
    '''

    def __init__(self, full_name, id, flag, team='', team_id=-1):
        self.full_name = full_name
        self.id = id
        self.flag = flag
        self.team = team
        self.team_id = team_id

    def __str__(self):
        return "Name: %s, ID: %d, Flag: %s" % (self.full_name, self.id, self.flag)

    def print_report(self):
        last_name, first_name, second_name = self.full_name.split()
        seq = [str(self.id), self.flag] + self.full_name.split()
        return ';'.join(seq)


class Team():
    '''
    Класс описывающий команду - название, город, ID. Содержит список объектов игроков (Player),
    а также список ответов команды по каждому туру (двумерный список).
    '''

    def __init__(self, name, city, id):
        self.name = name
        self.city = city
        self.id = id
        self.players = []
        self.answers = []
        self.results = []

    def __str__(self):
        return ("Name: %s, city: %s, ID: %s, players count: %d" % (self.name, self.city, self.id, len(self.players)))

    def print_sostav(self):
        print(self)
        for player in self.players:
            print(player)
        print('---------------')

    def set_all_answers(self, answers_list):
        self.answers = answers_list
        self.result = [self.all_sum(), [self.tour_score(tour + 1) for tour in range(len(self.answers))]]

    def get_answer(self, tour, quest_num):
        return self.answers[tour][quest_num]

    def add_player(self, player):
        self.players.append(player)

    def tour_score(self, tour):
        # print("Tour = ", tour)
        return sum([item for item in self.answers[tour - 1] if isinstance(item, int)])

    def all_sum(self):
        result = 0
        for tour in range(len(self.answers)):
            result += self.tour_score(tour + 1)
        return result

    def print_itogi(self):
        # print(self.answers)
        # print(self.name)
        # print(self.answers)
        result = [self.all_sum()] + [self.tour_score(1)]
        for index in range(1, len(self.answers)):
            result += [self.tour_score(index + 1)]
        return result


def formatting_function(index):
    '''
    Форматирующая функция, заменяющая пустую строку или пробел на 0, и 1.0 на 1
    ВХОДНОЙ ПАРАМЕТР => РЕЗУЛЬТАТ
    {'', ' '} => 0
    1.0 => 1
    X => X
    :param index: входной параметр
    :return: отформатированный результат из множества {0, 1, X}
    '''

    if index == '' or index == ' ':
        result = 0
    elif index == 1.0:
        result = 1
    else:
        result = index
    return result


def make_offset_list(quest_num, tours):
    '''
    Создает список кортежей (first_tour_cell, last_tour_cell) с номерами
    столбцов первого и последнего вопроса каждого тура
    :param quest_num: число вопросов в туре
    :param tours: количество туров
    :return: Список кортежей типа (first_tour_cell, last_tour_cell)
    '''
    offset = 0
    begin_col = 2
    result = []
    for tour in range(1, tours + 1):
        if tour == 2:
            offset = quest_num + 1
        elif tour > 2:
            offset = quest_num + 2
        begin_col += offset
        end_col = begin_col + quest_num
        result.append((begin_col, end_col))
    return result


def cells_to_values(cells_list):
    '''
    Принимает список объектов Cell и возвращает список значений (Cell.value) этих объектов
    :param cells_list: список объектов Cell
    :return: список значений объектов Cell
    '''
    result = []
    for cell in cells_list:
        result.append(cell.value)
    return result


def team_answers_processing(row, borders_tuple):
    '''НЕ ИСПОЛЬЗУЕТСЯ!
    Принимает объект row, получает каждый тур с помощью границ из borders_tuple
    :param row: Строка row
    :param borders_tuple: Список кортежей с ячейками первого и последнего вопроса каждого тура
    :return: Возвращает словарь { 'название_команды' : [список с вложенными списками результатов по каждому туру] }
    '''
    team_name = row[1].value.strip()
    # print(team_name)
    answers = []
    for (begin_col, end_col) in borders_tuple:
        # print(begin_col, end_col)
        list_of_cells = row[begin_col:end_col]
        unformated_tour_result = cells_to_values(list_of_cells)
        formated_tour_result = list(map(formatting_function, unformated_tour_result))
        answers.append(formated_tour_result)

    return {team_name: answers}


def check_teams_sheet1(sheet, team_dict):
    '''
    Обрабатывает страницу "Общие сведения". Создает словарь с экземплярами класса Team.
    :param sheet: Страница "Общие сведения".
    :return: Возвращается словарь с экземплярами класса Team формата {team_name: Team_obj}.
    '''

    errors_list = []
    teams = dict()
    row_iter = sheet.get_rows()
    zagolovok = next(row_iter)
    for row in row_iter:
        # print(row)
        if row[1].value != '' and row[1].value != 'Название':
            team_name = row[1].value.strip()
            # print('team = ', team_name)
            team_city = row[3].value.strip()
            teams[team_name] = team_city
    if len(teams) < len(team_dict):
        errors_list.insert(0, 'КРИТИЧНО! На вкладке "Общие сведения" меньше команд, чем на вкладке "Составы команд"')
    elif len(teams) > len(team_dict):
        errors_list.insert(0, 'КРИТИЧНО! На вкладке "Общие сведения" больше команд, чем на вкладке "Составы команд"')
    #difference = (team_dict.keys() - teams.keys()) | (teams.keys() - team_dict.keys())
    only_sheet1 = {'\"' + item + '\"' for item in teams.keys() - team_dict.keys()}
    only_sheet2 = {'\"' + item + '\"' for item in team_dict.keys() - teams.keys()}
    difference = only_sheet1 | only_sheet2
    if difference:
        errors_list.insert(0, 'КРИТИЧНО! Следующие названия команд присутствуют только на одной из двух вкладок: '
                                           ' \n- вкладка "Составы команд: ' + ', '.join(only_sheet2) + '\n- вкладка "Общие сведения": ' +
                                            ', '.join(only_sheet1))
    return errors_list


def answer_processing(sheet, teams_dict, borders_tuple):
    '''
    Дополняет объекты команд списками ответов Team.answers.
    :param sheet: Страница "Таблица"
    :param teams_dict: Словарь, сожержащий экземпляры класса Team
    :param borders_tuple: Список граничных ячеек туров
    :return:
    '''
    row_iter = sheet.get_rows()
    heading = next(row_iter)

    for row in row_iter:
        if row[1].value != '' and row[1].value != 'Название':
            team_name = row[1].value.strip()
            # print(team_name)
            answers = []
            for (begin_col, end_col) in borders_tuple:
                # print(begin_col, end_col)
                list_of_cells = row[begin_col:end_col]
                unformated_tour_result = cells_to_values(list_of_cells)
                formated_tour_result = list(map(formatting_function, unformated_tour_result))
                answers.append(formated_tour_result)
            teams_dict[team_name].set_all_answers(answers)


def sostav_processing(sheet):
    '''
    Обрабатывает страницу "Составы команд", создает экземпляры класса Player и присоединяет
    к соответствующему экземпляру Team. Экземпляры Team добавляются в словарь {'team_name' : Team}
    :param sheet: Страница "Составы команд".
    :param teams: Словарь с экземплярами класса Team {team_name: Team}.
    :return:
    '''

    result_teams = dict()
    row_iter = sheet.get_rows()
    for row in row_iter:
        # print(row)
        if row[6].value != '' and row[6].value != 'Фамилия':
            last_name = row[6].value.strip()
            second_name = row[7].value.strip()
            first_name = row[8].value.strip()
            name = ' '.join((last_name, second_name, first_name))
            id = int(row[5].value)
            flag = row[4].value.strip()

            team_name = row[2].value.strip()
            team_city = row[3].value.strip()
            team_id = int(row[1].value)
            player_instance = Player(name, id, flag, team_name, team_id)
            if team_name not in result_teams.keys():
                team_instance = Team(team_name, team_city, team_id)
                result_teams.update({team_name: team_instance})
            result_teams[team_name].add_player(player_instance)
    return result_teams


def excel_parse(file_name):
    workbook = xlrd.open_workbook(file_name)
    sheet0 = workbook.sheet_by_name('Информация')
    sheet1 = workbook.sheet_by_name('Общие сведения')
    sheet4 = workbook.sheet_by_name('Составы команд')
    sheet2 = workbook.sheet_by_name('Таблица')

    tour_num = int(sheet0.cell_value(2, 3))
    vopros_num = int(sheet0.cell_value(1, 3))
    offset_list = make_offset_list(vopros_num, tour_num)

    # teams_processing(sheet1)
    teams = sostav_processing(sheet4)
    # for team in teams.keys():
    # print(teams[team])
    errors = check_teams_sheet1(sheet1, teams)
    # print('errors = ', errors)

    # for team in teams:
    #     teams[team].print_sostav()
    sostav_line = ''
    score_line = ''
    schet_line = []
    if len(errors) and 'КРИТИЧНО' in errors[0]:
        error_line = errors
    else:
        answer_processing(sheet2, teams, offset_list)
        current_game = Game(teams, tour_num, vopros_num, errors)
        current_game.rating_check()
        score_line = current_game.make_score_report()
        sostav_line = current_game.make_sostav_report()
        error_line = current_game.get_errors()
        for team in sorted(teams.keys()):
            schet_line += [[team] + current_game.team_dict[team].print_itogi()]
        schet_line += [['Название', 'Итог'] + ['Тур ' + str(item + 1) for item in range(current_game.tour_numbers)]]
            # for error_item in current_game.errors:
        #   print(error_item)
        #current_game.make_sostav_report()
        #current_game.make_score_report()
    return (error_line, sostav_line, score_line, schet_line)


if __name__ == '__main__':
    # print(sys.argv[1])
    excel_parse(sys.argv[1])
