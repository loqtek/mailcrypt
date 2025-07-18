from configparser import RawConfigParser

class Config:
    def __init__(self, config_path: str = "config.conf"):
        self.config = RawConfigParser()
        self.config.read(config_path)
        self.config_path = config_path

        # general
        self.jwt_expire_time = self._getint("general", "jwt_expire_time")
        self.secret_session_token = self._get("general", "secret_session_token")

        # setup
        self.reset_to_default = self._getbool("setup", "reset_to_default")
        self.erase_database_on_reset = self._getbool("setup", "erase_database_on_reset")

        # mail
        self.email_address = self._get("mail", "email_address")
        self.password = self._get("mail", "password")
        self.imap_server = self._get("mail", "imap_server")
        self.imap_port = self._get("mail", "imap_port")
        self.smtp_server = self._get("mail", "smtp_server")
        self.smtp_port = self._get("mail", "smtp_port")

        # database
        self.database_url = self._get("database", "database_url")
        self.database_name = self._get("database", "database_name")
        self.database_creds = self._get("database", "database_creds")
        self.database_type = self._get("database", "database_type")


    def _get(self, section: str, key: str, fallback: str = None) -> str:
        return self.config.get(section, key, fallback=fallback)

    def _getint(self, section: str, key: str, fallback: int = None) -> int:
        return self.config.getint(section, key, fallback=fallback)

    def _getfloat(self, section: str, key: str, fallback: float = None) -> float:
        return self.config.getfloat(section, key, fallback=fallback)

    def _getbool(self, section: str, key: str, fallback: bool = None) -> bool:
        return self.config.getboolean(section, key, fallback=fallback)
    
    def _getarray(self, section: str, key: str, fallback: list = None, delimiter: str = ",") -> list:
        """
        returns a list by splitting the value on the delimiter.
        """
        if self.config.has_option(section, key):
            raw_value = self.config.get(section, key)
            if raw_value.strip() == "":
                return fallback or []
            return [item.strip() for item in raw_value.split(delimiter)]
        return fallback or []


    def set(self, section: str, key: str, value: str):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)

    def save(self):
        with open(self.config_path, "w") as configfile:
            self.config.write(configfile)

    def export_as_dict(self) -> dict:
        """exports config as a py dictionary."""
        return {section: dict(self.config.items(section)) for section in self.config.sections()}
        
    def database_full_url(self, url: str = None, creds: str = None, dbName: str = None, databaseType: str = None) -> str:
        """get a sqlalc compatible db URI based on the config."""
        print(databaseType)
        db_type = (databaseType or self.database_type).lower()
        url = url or self.database_url
        creds = creds or self.database_creds
        dbName = dbName or self.database_name
        print(db_type)
        if db_type in ["postgres", "psycopg2"]:
            return f"postgresql://{creds}@{url}/{dbName}"
        elif db_type in ("mysql", "mariadb"):
            return f"mysql+pymysql://{creds}@{url}/{dbName}"
        elif db_type == "sqlite":
            return f"sqlite:///{url}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
    def is_async(self, full_db_url: str = None) -> bool:
        """Check if the current driver is async."""
        db_url = self.database_full_url() if not full_db_url else full_db_url
        return any(proto in db_url for proto in ["+asyncpg", "+aiomysql", "+aiosqlite"])
