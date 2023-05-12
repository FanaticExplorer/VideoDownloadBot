from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    token: SecretStr
    api_server: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config_o = Settings()

videos_folder = 'videos'
start_msg_path = 'start_msg.txt'
help_msg_path = 'help_msg.txt'
fe_id = 806818274
logs_folder = 'logs'
logs_zip = 'logs.zip'