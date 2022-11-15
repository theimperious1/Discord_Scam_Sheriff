class ServerConfiguration:

    def __init__(self, server_id, output_channel_id, monitor_channel_id, welcome_trigger_phrase,
                 action_mode_pfp, action_mode_username, name_blacklist_mode, matching_enabled, created_on, updated_on):
        self.server_id = server_id
        self.output_channel_id = output_channel_id
        self.monitor_channel_id = monitor_channel_id
        self.welcome_trigger_phrase = welcome_trigger_phrase
        self.action_mode_pfp = action_mode_pfp
        self.action_mode_username = action_mode_username
        self.name_blacklist_mode = name_blacklist_mode
        self.matching_enabled = matching_enabled
        self.created_on = created_on
        self.updated_on = updated_on

    def set_server_id(self, server_id):
        self.server_id = server_id

    def set_output_channel_id(self, output_channel_id):
        self.output_channel_id = output_channel_id

    def set_monitor_channel_id(self, monitor_channel_id):
        self.monitor_channel_id = monitor_channel_id

    def set_welcome_trigger_phrase(self, welcome_trigger_phrase):
        self.welcome_trigger_phrase = welcome_trigger_phrase

    def set_action_mode_pfp(self, action_mode_pfp):
        self.action_mode_pfp = action_mode_pfp

    def set_action_mode_username(self, action_mode_username):
        self.action_mode_username = action_mode_username

    def set_name_blacklist_mode(self, name_blacklist_mode):
        self.name_blacklist_mode = name_blacklist_mode

    def set_matching_enabled(self, matching_enabled):
        self.matching_enabled = matching_enabled

    def set_created_on(self, created_on):
        self.created_on = created_on

    def set_updated_on(self, updated_on):
        self.updated_on = updated_on

    def get_server_id(self):
        return self.server_id

    def get_output_channel_id(self):
        return self.output_channel_id

    def get_monitor_channel_id(self):
        return self.monitor_channel_id

    def get_welcome_trigger_phrase(self):
        return self.welcome_trigger_phrase

    def get_action_mode_pfp(self):
        return self.action_mode_pfp

    def get_action_mode_username(self):
        return self.action_mode_username

    def get_name_blacklist_mode(self):
        return self.name_blacklist_mode

    def get_matching_enabled(self):
        return self.matching_enabled

    def get_created_on(self):
        return self.created_on

    def get_updated_on(self):
        return self.updated_on


