class GUIDummy(object):
    def set_position(self, team, pos):
        message = 'New position for ' + team + ' : ' + str(pos)
        print message

    def set_height(self, team, pos):
        message = 'New height for ' + team + ' : ' + str(pos)
        print message

    def set_goal_position(self, team, pos):
        message = 'New goal-position for ' + team + ' : ' + str(pos)
        print message

    def set_goal_height(self, team, pos):
        message = 'New goal-height for ' + team + ' : ' + str(pos)
        print message

    def set_direction(self, team,  direction):
        message = 'New direction for ' + team + ' : ' + str(direction)
        print message

    def add_to_console(self, info):
        #message = 'New console info: ' + info
        #print message
        pass


